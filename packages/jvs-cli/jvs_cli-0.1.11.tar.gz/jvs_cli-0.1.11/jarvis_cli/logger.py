import json
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

class DebugLogger:
    def __init__(self, enabled: bool = False, log_dir: str = "./logs"):
        self.enabled = enabled
        self.log_dir = Path(log_dir)
        self.log_file: Optional[Path] = None
        
        if self.enabled:
            self._setup_log_file()
    
    def _setup_log_file(self) -> None:
        self.log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"jvs_debug_{timestamp}.log"
        self._log_event("session_start", {"timestamp": datetime.now().isoformat()})
    
    def _log_event(self, event_type: str, data: Any) -> None:
        if not self.enabled or not self.log_file:
            return
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False, indent=2))
            f.write("\n" + "="*80 + "\n")
    
    def log_chunk(self, chunk_data: dict) -> None:
        self._log_event("chunk_received", chunk_data)
    
    def log_request(self, request_data: dict) -> None:
        self._log_event("request_sent", request_data)
    
    def log_error(self, error: str) -> None:
        self._log_event("error", {"error": error})

    def log_info(self, message: str) -> None:
        self._log_event("info", {"message": message})

    def close(self) -> None:
        if self.enabled:
            self._log_event("session_end", {"timestamp": datetime.now().isoformat()})

_debug_logger: Optional[DebugLogger] = None

def get_debug_logger() -> DebugLogger:
    global _debug_logger
    if _debug_logger is None:
        _debug_logger = DebugLogger(enabled=False)
    return _debug_logger

def init_debug_logger(enabled: bool = False, log_dir: str = "./logs") -> DebugLogger:
    global _debug_logger
    _debug_logger = DebugLogger(enabled=enabled, log_dir=log_dir)
    return _debug_logger

