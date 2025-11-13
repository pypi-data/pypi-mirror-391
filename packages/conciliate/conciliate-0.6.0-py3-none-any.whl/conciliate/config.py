"""Configuration management for Conciliate."""

import os
from pathlib import Path
from typing import Optional, List, Literal, Dict, Any

import yaml
from pydantic import BaseModel, Field, field_validator


class WebSocketConfig(BaseModel):
    """WebSocket configuration."""
    enabled: bool = True


class SourceConfig(BaseModel):
    """Configuration for a single API source."""
    name: str = Field(description="Display name for this source")
    type: Literal["local", "url"] = Field(description="Source type: local file watching or remote URL")
    
    # Local source fields
    path: Optional[str] = Field(default=None, description="Path to backend code (for local type)")
    framework: Optional[str] = Field(default="auto", description="Backend framework (auto, fastapi, flask, express)")
    watch_patterns: Optional[List[str]] = Field(default=None, description="File patterns to watch")
    
    # Remote source fields
    url: Optional[str] = Field(default=None, description="OpenAPI spec URL (for url type)")
    poll_interval: int = Field(default=300, description="Polling interval in seconds for remote specs")
    headers: Optional[Dict[str, str]] = Field(default=None, description="HTTP headers for authentication")
    
    enabled: bool = Field(default=True, description="Whether this source is enabled")
    
    @field_validator("path")
    @classmethod
    def resolve_path(cls, v: Optional[str]) -> Optional[str]:
        """Resolve relative paths to absolute paths."""
        if v is None:
            return None
        path = Path(v)
        if not path.is_absolute():
            path = Path.cwd() / path
        return str(path.resolve())


class ConciliateConfig(BaseModel):
    """Conciliate configuration model."""
    
    # Multi-source support
    sources: Optional[List[SourceConfig]] = Field(default=None, description="Multiple API sources")
    
    # Legacy single-source fields (for backward compatibility)
    backend_path: Optional[str] = Field(default=None)
    frontend_path: Optional[str] = Field(default=None)
    
    # Server settings
    port: int = Field(default=5678, ge=1024, le=65535)
    
    # Legacy watch patterns (for single source)
    watch_patterns: List[str] = Field(default_factory=lambda: ["**/*.py"])
    ignore_patterns: List[str] = Field(
        default_factory=lambda: [
            "**/__pycache__/**",
            "**/.venv/**",
            "**/node_modules/**",
            "**/.git/**",
            "**/*.pyc",
            "**/.pytest_cache/**",
        ]
    )
    framework: str = Field(default="auto", description="Backend framework (auto, fastapi, flask, express)")
    summary_max_tokens: int = Field(default=1000, ge=100)
    verbose: bool = Field(default=False)
    output_dir: str = Field(default=".conciliate")
    websocket: WebSocketConfig = Field(default_factory=WebSocketConfig)
    custom_spec_command: Optional[str] = Field(default=None)
    
    def get_sources(self) -> List[SourceConfig]:
        """Get list of sources, converting legacy config if needed."""
        if self.sources:
            return [s for s in self.sources if s.enabled]
        
        # Convert legacy single-source config
        if self.backend_path:
            return [SourceConfig(
                name="Main API",
                type="local",
                path=self.backend_path,
                framework=self.framework,
                watch_patterns=self.watch_patterns
            )]
        
        return []
    
    @field_validator("backend_path", "frontend_path")
    @classmethod
    def resolve_path(cls, v: Optional[str]) -> Optional[str]:
        """Resolve relative paths to absolute paths."""
        if v is None:
            return None
        path = Path(v)
        if not path.is_absolute():
            # Resolve relative to current working directory
            path = Path.cwd() / path
        return str(path.resolve())
    
    @field_validator("output_dir")
    @classmethod
    def resolve_output_dir(cls, v: str) -> str:
        """Resolve output directory path."""
        path = Path(v)
        if not path.is_absolute():
            path = Path.cwd() / path
        return str(path.resolve())


def load_config(config_path: Optional[Path] = None) -> ConciliateConfig:
    """
    Load configuration from .conciliate.yaml file.
    
    Args:
        config_path: Optional path to config file. If None, searches for .conciliate.yaml
                    in current directory and parent directories.
    
    Returns:
        ConciliateConfig instance
    
    Raises:
        FileNotFoundError: If config file not found
        ValueError: If config file is invalid
    """
    if config_path is None:
        # Search for .conciliate.yaml in current directory and parents
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            potential_config = parent / ".conciliate.yaml"
            if potential_config.exists():
                config_path = potential_config
                break
    
    if config_path is None or not config_path.exists():
        raise FileNotFoundError(
            "No .conciliate.yaml found. Run 'conciliate init' to create one."
        )
    
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    if not data:
        raise ValueError("Config file is empty")
    
    return ConciliateConfig(**data)


def create_default_config(target_path: Path) -> None:
    """
    Create a default .conciliate.yaml config file.
    
    Args:
        target_path: Path where to create the config file
    """
    default_config = ConciliateConfig()
    config_dict = default_config.model_dump(mode="python", exclude_none=True)
    
    with open(target_path, "w", encoding="utf-8") as f:
        f.write("# Conciliate Configuration\n")
        f.write("# Generated by conciliate init\n\n")
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)


def ensure_output_dir(config: ConciliateConfig) -> Path:
    """
    Ensure output directory exists and return its Path.
    
    Args:
        config: ConciliateConfig instance
    
    Returns:
        Path to output directory
    """
    output_path = Path(config.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (output_path / "cache").mkdir(exist_ok=True)
    (output_path / "logs").mkdir(exist_ok=True)
    
    return output_path
