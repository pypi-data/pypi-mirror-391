"""FastAPI server for exposing API specs and summaries."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config import ConciliateConfig, ensure_output_dir
from .spec_generator import SpecGenerator, SpecGeneratorError
from .diff_engine import DiffEngine, DiffResult
from .summarizer import APISummarizer

logger = logging.getLogger(__name__)


class ConciliateServer:
    """Conciliate FastAPI daemon server."""
    
    def __init__(self, config: ConciliateConfig):
        self.config = config
        self.app = FastAPI(
            title="Conciliate Server",
            description="API context synchronization server",
            version="0.1.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize components
        self.spec_generator = SpecGenerator(config)
        self.diff_engine = DiffEngine()
        self.summarizer = APISummarizer(config.summary_max_tokens)
        
        # State
        self.current_spec: Optional[Dict[str, Any]] = None
        self.current_summary: Optional[str] = None
        self.last_diff: Optional[DiffResult] = None
        self.websocket_clients: List[WebSocket] = []
        
        # Mock server state
        self.mock_enabled: bool = False
        self.mock_server: Optional[Any] = None
        
        # Multi-source support
        from .source_manager import SourceManager
        self.source_manager: Optional[SourceManager] = None
        if config.sources:
            self.source_manager = SourceManager(config)
        
        # Setup output directory
        self.output_dir = ensure_output_dir(config)
        
        # Register routes
        self._setup_routes()
        
        # Register startup/shutdown events
        @self.app.on_event("startup")
        async def startup_event():
            """Initialize source manager on startup"""
            if self.source_manager:
                await self.source_manager.initialize()
                logger.info("Multi-source manager initialized")
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            """Cleanup source manager on shutdown"""
            if self.source_manager:
                await self.source_manager.shutdown()
                logger.info("Multi-source manager shut down")
        
        # Initial spec generation
        self._load_or_generate_spec()
    
    def _setup_routes(self) -> None:
        """Setup API routes."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with server info."""
            return {
                "name": "Conciliate Server",
                "version": "0.1.0",
                "status": "running",
                "backend_path": self.config.backend_path,
                "has_spec": self.current_spec is not None,
            }
        
        @self.app.get("/spec")
        async def get_spec():
            """Get the current OpenAPI specification."""
            if self.current_spec is None:
                raise HTTPException(
                    status_code=404,
                    detail="No API specification available. Try reloading."
                )
            return JSONResponse(content=self.current_spec)
        
        @self.app.get("/summary")
        async def get_summary():
            """Get a human-readable API summary."""
            if self.current_spec is None:
                raise HTTPException(
                    status_code=404,
                    detail="No API specification available. Try reloading."
                )
            
            if self.current_summary is None:
                self.current_summary = self.summarizer.summarize(self.current_spec)
            
            return {
                "summary": self.current_summary,
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        @self.app.get("/diff")
        async def get_diff():
            """Get the latest API changes."""
            if self.last_diff is None:
                return {
                    "message": "No changes detected yet",
                    "has_changes": False,
                }
            
            return JSONResponse(content=self.last_diff.to_dict())
        
        @self.app.post("/reload")
        async def reload_spec():
            """Manually trigger spec reload."""
            try:
                await self._regenerate_spec()
                return {
                    "status": "success",
                    "message": "Specification reloaded",
                    "has_changes": self.last_diff.has_changes() if self.last_diff else False,
                }
            except Exception as e:
                logger.error(f"Failed to reload spec: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.websocket("/stream")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for live updates."""
            await websocket.accept()
            self.websocket_clients.append(websocket)
            
            try:
                # Send initial spec
                if self.current_spec:
                    await websocket.send_json({
                        "type": "spec",
                        "data": self.current_spec,
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                
                # Keep connection alive
                while True:
                    await asyncio.sleep(1)
                    
            except WebSocketDisconnect:
                self.websocket_clients.remove(websocket)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                if websocket in self.websocket_clients:
                    self.websocket_clients.remove(websocket)
        
        # Mock Server endpoints
        @self.app.post("/mock/start")
        async def start_mock_server(delay_min: int = 0, delay_max: int = 0):
            """Start mock server mode."""
            if not self.current_spec:
                raise HTTPException(status_code=400, detail="No API spec available")
            
            try:
                from .mock_server import MockServer
                self.mock_server = MockServer(self.current_spec, (delay_min, delay_max))
                self.mock_enabled = True
                return {
                    "status": "success",
                    "message": "Mock server started",
                    "delay_range": [delay_min, delay_max]
                }
            except Exception as e:
                logger.error(f"Failed to start mock server: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/mock/stop")
        async def stop_mock_server():
            """Stop mock server mode."""
            self.mock_enabled = False
            self.mock_server = None
            return {
                "status": "success",
                "message": "Mock server stopped"
            }
        
        @self.app.get("/mock/status")
        async def mock_server_status():
            """Get mock server status."""
            return {
                "enabled": self.mock_enabled,
                "endpoints": len(self.current_spec.get("paths", {})) if self.current_spec else 0
            }
        
        @self.app.api_route("/mock/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        async def mock_api_request(path: str, request: Request):
            """Handle mock API requests."""
            if not self.mock_enabled or not self.mock_server:
                raise HTTPException(status_code=503, detail="Mock server not enabled")
            
            # Add leading slash if missing
            if not path.startswith("/"):
                path = "/" + path
            
            response = self.mock_server.get_mock_response(path, request.method)
            
            return JSONResponse(
                content=response["body"],
                status_code=response["status"],
                headers=response["headers"]
            )
        
        # Multi-Source endpoints
        @self.app.get("/sources/status")
        async def get_sources_status():
            """Get status of all configured sources."""
            if not self.source_manager:
                return {
                    "multi_source_enabled": False,
                    "sources": []
                }
            
            return {
                "multi_source_enabled": True,
                "sources": self.source_manager.get_status()
            }
        
        @self.app.get("/sources/{source_name}/spec")
        async def get_source_spec(source_name: str):
            """Get spec from a specific source."""
            if not self.source_manager:
                raise HTTPException(status_code=404, detail="Multi-source not enabled")
            
            spec = self.source_manager.get_spec(source_name)
            if not spec:
                raise HTTPException(status_code=404, detail=f"Source {source_name} not found or no spec available")
            
            return JSONResponse(content=spec)
        
        @self.app.get("/sources/aggregate")
        async def get_aggregate_spec():
            """Get aggregated spec from all sources."""
            if not self.source_manager:
                raise HTTPException(status_code=404, detail="Multi-source not enabled")
            
            return JSONResponse(content=self.source_manager.get_aggregate_spec())
        
        @self.app.post("/sources/{source_name}/refresh")
        async def refresh_source(source_name: str):
            """Manually refresh a specific source."""
            if not self.source_manager:
                raise HTTPException(status_code=404, detail="Multi-source not enabled")
            
            success = await self.source_manager.refresh_source(source_name)
            if not success:
                raise HTTPException(status_code=500, detail=f"Failed to refresh {source_name}")
            
            return {
                "status": "success",
                "message": f"Source {source_name} refreshed",
                "spec": self.source_manager.get_spec(source_name)
            }
        
        @self.app.post("/sources/refresh/all")
        async def refresh_all_sources():
            """Refresh all sources."""
            if not self.source_manager:
                raise HTTPException(status_code=404, detail="Multi-source not enabled")
            
            results = await self.source_manager.refresh_all()
            return {
                "status": "success",
                "results": results
            }
    
    def _load_or_generate_spec(self) -> None:
        """Load existing spec from cache or generate new one."""
        cache_file = self.output_dir / "api_spec.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    self.current_spec = json.load(f)
                logger.info("Loaded spec from cache")
                self.diff_engine.update_spec(self.current_spec)
                return
            except Exception as e:
                logger.warning(f"Failed to load cached spec: {e}")
        
        # Generate new spec
        try:
            self.current_spec = self.spec_generator.generate()
            self.diff_engine.update_spec(self.current_spec)
            self._save_spec()
            logger.info("Generated new spec")
        except SpecGeneratorError as e:
            logger.error(f"Failed to generate spec: {e}")
    
    async def _regenerate_spec(self) -> None:
        """Regenerate API spec and detect changes."""
        try:
            # Generate new spec
            new_spec = self.spec_generator.generate()
            
            # Compare with existing
            if self.current_spec:
                diff_result = self.diff_engine.compare(self.current_spec, new_spec)
                self.last_diff = diff_result
                
                if diff_result.has_changes():
                    logger.info("API changes detected")
                    self._save_diff(diff_result)
                    await self._broadcast_changes(diff_result)
            
            # Update current spec
            self.current_spec = new_spec
            self.current_summary = None  # Reset summary to regenerate
            
            # Save to disk
            self._save_spec()
            
            # Generate and save summary
            self.current_summary = self.summarizer.summarize(new_spec)
            self._save_summary()
            
        except SpecGeneratorError as e:
            logger.error(f"Spec generation failed: {e}")
            raise
    
    def _save_spec(self) -> None:
        """Save current spec to disk."""
        if self.current_spec is None:
            return
        
        spec_file = self.output_dir / "api_spec.json"
        with open(spec_file, "w", encoding="utf-8") as f:
            json.dump(self.current_spec, f, indent=2)
    
    def _save_summary(self) -> None:
        """Save current summary to disk."""
        if self.current_summary is None:
            return
        
        summary_file = self.output_dir / "api_summary.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(self.current_summary)
    
    def _save_diff(self, diff_result: DiffResult) -> None:
        """Save diff result to disk."""
        diff_file = self.output_dir / "api_diff.json"
        with open(diff_file, "w", encoding="utf-8") as f:
            f.write(diff_result.to_json())
        
        # Also save human-readable diff summary
        diff_summary = self.summarizer.summarize_diff(diff_result.to_dict())
        diff_summary_file = self.output_dir / "api_diff_summary.txt"
        with open(diff_summary_file, "w", encoding="utf-8") as f:
            f.write(diff_summary)
    
    async def _broadcast_changes(self, diff_result: DiffResult) -> None:
        """Broadcast changes to all WebSocket clients."""
        if not self.websocket_clients:
            return
        
        message = {
            "type": "diff",
            "data": diff_result.to_dict(),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        disconnected = []
        for client in self.websocket_clients:
            try:
                await client.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to WebSocket client: {e}")
                disconnected.append(client)
        
        # Remove disconnected clients
        for client in disconnected:
            self.websocket_clients.remove(client)
    
    async def on_file_change(self) -> None:
        """Callback for file watcher."""
        logger.info("File change detected, regenerating spec...")
        await self._regenerate_spec()
    
    def run(self, host: str = "127.0.0.1", port: Optional[int] = None) -> None:
        """
        Run the server.
        
        Args:
            host: Host to bind to
            port: Port to bind to (uses config.port if None)
        """
        if port is None:
            port = self.config.port
        
        logger.info(f"Starting Conciliate server on {host}:{port}")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info" if self.config.verbose else "warning",
        )


def create_server(config: ConciliateConfig) -> ConciliateServer:
    """
    Create a Conciliate server instance.
    
    Args:
        config: Conciliate configuration
    
    Returns:
        ConciliateServer instance
    """
    return ConciliateServer(config)
