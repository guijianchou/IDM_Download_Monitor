#!/usr/bin/env python3
"""Progress tracking module for Downloads Monitor"""

import sys
import time
import logging
from typing import Optional
from threading import Lock


class ProgressTracker:
    """Simple progress tracker with console output"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.last_update = 0
        self.lock = Lock()
        self.logger = logging.getLogger(__name__)
        self.show_progress = self.logger.isEnabledFor(logging.INFO)
    
    def update(self, increment: int = 1, item_name: Optional[str] = None) -> None:
        with self.lock:
            self.current += increment
            
            if not self.show_progress:
                return
            
            current_time = time.time()
            if current_time - self.last_update < 0.1 and self.current < self.total:
                return
            
            self.last_update = current_time
            self._display_progress(item_name)
    
    def _display_progress(self, item_name: Optional[str] = None) -> None:
        if self.total == 0:
            return
        
        percentage = (self.current / self.total) * 100
        elapsed = time.time() - self.start_time
        
        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = f"ETA: {eta:.1f}s"
        else:
            eta_str = "ETA: --"
        
        bar_length = 30
        filled_length = int(bar_length * self.current // self.total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        item_str = f" | {item_name}" if item_name else ""
        progress_line = f"\r{self.description}: [{bar}] {percentage:.1f}% ({self.current}/{self.total}) | {eta_str}{item_str}"
        print(progress_line[:80], end='', flush=True)
        
        if self.current >= self.total:
            print()
    
    def finish(self, message: Optional[str] = None) -> None:
        with self.lock:
            self.current = self.total
            elapsed = time.time() - self.start_time
            
            if self.show_progress:
                self._display_progress()
                self.logger.info(message or f"Completed in {elapsed:.2f}s")


def create_progress_tracker(total: int, description: str = "Processing") -> ProgressTracker:
    return ProgressTracker(total, description)
