"""File watcher for monitoring backend changes."""

import asyncio
from pathlib import Path
from typing import Callable, Optional, Set
import logging

from watchfiles import awatch, Change

from .config import ConciliateConfig

logger = logging.getLogger(__name__)


class FileWatcher:
    """Watches backend files for changes and triggers callbacks."""
    
    def __init__(
        self,
        config: ConciliateConfig,
        on_change: Optional[Callable[[], None]] = None
    ):
        self.config = config
        self.on_change = on_change
        self.backend_path = Path(config.backend_path)
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start watching for file changes."""
        if self._running:
            logger.warning("File watcher already running")
            return
        
        self._running = True
        logger.info(f"Starting file watcher for {self.backend_path}")
        
        try:
            async for changes in awatch(
                self.backend_path,
                watch_filter=self._should_watch,
                stop_event=None,
            ):
                if not self._running:
                    break
                
                await self._handle_changes(changes)
                
        except Exception as e:
            logger.error(f"File watcher error: {e}")
            self._running = False
            raise
    
    async def stop(self) -> None:
        """Stop watching for file changes."""
        logger.info("Stopping file watcher")
        self._running = False
        
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    def _should_watch(self, change: Change, path: str) -> bool:
        """
        Filter function to determine if a file should be watched.
        
        Args:
            change: Type of change
            path: File path
        
        Returns:
            True if file should be watched
        """
        file_path = Path(path)
        
        # Check ignore patterns
        for pattern in self.config.ignore_patterns:
            if file_path.match(pattern):
                return False
        
        # Check watch patterns
        for pattern in self.config.watch_patterns:
            if file_path.match(pattern):
                return True
        
        return False
    
    async def _handle_changes(self, changes: Set[tuple]) -> None:
        """
        Handle file changes.
        
        Args:
            changes: Set of (change_type, path) tuples
        """
        if not changes:
            return
        
        # Log changes
        for change_type, path in changes:
            change_name = change_type.name if hasattr(change_type, 'name') else str(change_type)
            logger.info(f"File {change_name}: {path}")
        
        # Trigger callback
        if self.on_change:
            try:
                if asyncio.iscoroutinefunction(self.on_change):
                    await self.on_change()
                else:
                    self.on_change()
            except Exception as e:
                logger.error(f"Error in change callback: {e}")
    
    def run(self) -> None:
        """Run the watcher in a blocking manner (for sync contexts)."""
        asyncio.run(self.start())


async def watch_backend(
    config: ConciliateConfig,
    on_change: Callable[[], None]
) -> None:
    """
    Convenience function to start watching backend.
    
    Args:
        config: Conciliate configuration
        on_change: Callback function to call on changes
    """
    watcher = FileWatcher(config, on_change)
    await watcher.start()
