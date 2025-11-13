"""
Multi-Source Manager - Handles fetching specs from local and remote sources
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

import httpx
from .config import SourceConfig, ConciliateConfig
from .spec_generator import SpecGenerator, SpecGeneratorError

logger = logging.getLogger(__name__)


class SourceManager:
    """Manages multiple API sources (local and remote)"""
    
    def __init__(self, config: ConciliateConfig):
        self.config = config
        self.sources = config.get_sources()
        self.specs: Dict[str, Dict[str, Any]] = {}  # source_name -> spec
        self.last_updated: Dict[str, datetime] = {}  # source_name -> timestamp
        self.polling_tasks: Dict[str, asyncio.Task] = {}
        
    async def initialize(self):
        """Initialize all sources and start polling for remote ones"""
        for source in self.sources:
            try:
                await self.fetch_spec(source)
                
                # Start polling task for remote sources
                if source.type == "url":
                    task = asyncio.create_task(self._poll_remote_source(source))
                    self.polling_tasks[source.name] = task
                    
            except Exception as e:
                logger.error(f"Failed to initialize source {source.name}: {e}")
    
    async def fetch_spec(self, source: SourceConfig) -> Optional[Dict[str, Any]]:
        """Fetch spec from a single source"""
        if source.type == "local":
            return await self._fetch_local_spec(source)
        elif source.type == "url":
            return await self._fetch_remote_spec(source)
        return None
    
    async def _fetch_local_spec(self, source: SourceConfig) -> Optional[Dict[str, Any]]:
        """Fetch spec from local file watching"""
        try:
            # Create a temporary config for this source
            from .config import ConciliateConfig
            temp_config = ConciliateConfig(
                backend_path=source.path,
                framework=source.framework or "auto",
                watch_patterns=source.watch_patterns or ["**/*.py"],
                ignore_patterns=self.config.ignore_patterns,
                output_dir=self.config.output_dir
            )
            
            generator = SpecGenerator(temp_config)
            spec = generator.generate()
            
            self.specs[source.name] = spec
            self.last_updated[source.name] = datetime.utcnow()
            
            logger.info(f"Fetched local spec from {source.name}")
            return spec
            
        except SpecGeneratorError as e:
            logger.error(f"Failed to generate spec for {source.name}: {e}")
            return None
    
    async def _fetch_remote_spec(self, source: SourceConfig) -> Optional[Dict[str, Any]]:
        """Fetch spec from remote URL"""
        if not source.url:
            logger.error(f"No URL configured for remote source {source.name}")
            return None
        
        try:
            # Replace environment variables in URL and headers
            url = self._expand_env_vars(source.url)
            headers = {}
            
            if source.headers:
                headers = {
                    k: self._expand_env_vars(v) 
                    for k, v in source.headers.items()
                }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                spec = response.json()
                self.specs[source.name] = spec
                self.last_updated[source.name] = datetime.utcnow()
                
                logger.info(f"Fetched remote spec from {source.name} ({url})")
                return spec
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching {source.name}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from {source.name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to fetch remote spec from {source.name}: {e}")
            return None
    
    async def _poll_remote_source(self, source: SourceConfig):
        """Continuously poll a remote source"""
        while True:
            try:
                await asyncio.sleep(source.poll_interval)
                await self._fetch_remote_spec(source)
            except asyncio.CancelledError:
                logger.info(f"Stopped polling {source.name}")
                break
            except Exception as e:
                logger.error(f"Error polling {source.name}: {e}")
    
    def _expand_env_vars(self, text: str) -> str:
        """Expand ${VAR} environment variables in text"""
        import os
        import re
        
        def replacer(match):
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))
        
        return re.sub(r'\$\{([^}]+)\}', replacer, text)
    
    async def refresh_source(self, source_name: str) -> bool:
        """Manually refresh a specific source"""
        source = next((s for s in self.sources if s.name == source_name), None)
        if not source:
            logger.error(f"Source {source_name} not found")
            return False
        
        spec = await self.fetch_spec(source)
        return spec is not None
    
    async def refresh_all(self) -> Dict[str, bool]:
        """Refresh all sources"""
        results = {}
        for source in self.sources:
            success = await self.refresh_source(source.name)
            results[source.name] = success
        return results
    
    def get_spec(self, source_name: str) -> Optional[Dict[str, Any]]:
        """Get cached spec for a source"""
        return self.specs.get(source_name)
    
    def get_all_specs(self) -> Dict[str, Dict[str, Any]]:
        """Get all cached specs"""
        return self.specs.copy()
    
    def get_aggregate_spec(self) -> Dict[str, Any]:
        """Aggregate all specs into a single OpenAPI spec"""
        if not self.specs:
            return {
                "openapi": "3.0.0",
                "info": {
                    "title": "Aggregated API",
                    "version": "1.0.0"
                },
                "paths": {},
                "components": {"schemas": {}}
            }
        
        # Start with first spec as base
        first_spec = next(iter(self.specs.values()))
        aggregate = {
            "openapi": first_spec.get("openapi", "3.0.0"),
            "info": {
                "title": "Aggregated API",
                "version": "1.0.0",
                "description": f"Aggregated from {len(self.specs)} sources: {', '.join(self.specs.keys())}"
            },
            "paths": {},
            "components": {"schemas": {}}
        }
        
        # Merge paths and schemas from all specs
        for source_name, spec in self.specs.items():
            # Merge paths with source prefix
            for path, path_item in spec.get("paths", {}).items():
                prefixed_path = f"/{source_name}{path}"
                aggregate["paths"][prefixed_path] = {
                    **path_item,
                    "x-source": source_name  # Tag with source name
                }
            
            # Merge schemas with source prefix to avoid conflicts
            for schema_name, schema in spec.get("components", {}).get("schemas", {}).items():
                prefixed_name = f"{source_name}_{schema_name}"
                aggregate["components"]["schemas"][prefixed_name] = schema
        
        return aggregate
    
    def get_status(self) -> List[Dict[str, Any]]:
        """Get status of all sources"""
        status = []
        for source in self.sources:
            status.append({
                "name": source.name,
                "type": source.type,
                "enabled": source.enabled,
                "has_spec": source.name in self.specs,
                "last_updated": self.last_updated.get(source.name).isoformat() if source.name in self.last_updated else None,
                "endpoint_count": len(self.specs.get(source.name, {}).get("paths", {})),
                "url": source.url if source.type == "url" else None,
                "path": source.path if source.type == "local" else None
            })
        return status
    
    async def shutdown(self):
        """Stop all polling tasks"""
        for task in self.polling_tasks.values():
            task.cancel()
        
        # Wait for all tasks to complete
        if self.polling_tasks:
            await asyncio.gather(*self.polling_tasks.values(), return_exceptions=True)
        
        logger.info("SourceManager shutdown complete")
