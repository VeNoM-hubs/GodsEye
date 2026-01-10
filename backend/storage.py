"""
Storage Layer
Handles persistent storage of events and alerts
Currently supports JSON file storage (Database support planned)
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

from backend.schemas import AccessEvent, HoneypotEvent, NetworkEvent, EndpointEvent, TeapotEvent
from backend.alert_engine import Alert
from backend.config import get_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StorageLayer:
    """
    Storage layer for events and alerts
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        self.config = get_config().storage
        self.storage_dir = storage_dir or self.config.log_directory
        
        # Create storage directories
        self._setup_directories()
        
        logger.info(f"Storage Layer initialized: {self.storage_dir}")
    
    def _setup_directories(self):
        """Create necessary storage directories"""
        directories = [
            self.storage_dir,
            os.path.join(self.storage_dir, "events"),
            os.path.join(self.storage_dir, "alerts"),
            os.path.join(self.storage_dir, "archive")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def save_event(
        self, 
        event: AccessEvent | HoneypotEvent | NetworkEvent | EndpointEvent | TeapotEvent
    ) -> bool:
        """
        Save event to storage
        
        Args:
            event: Event to save
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get event type directory
            event_dir = os.path.join(self.storage_dir, "events", event.event_type)
            os.makedirs(event_dir, exist_ok=True)
            
            # Create filename with timestamp
            date_str = event.timestamp.strftime("%Y%m%d")
            filename = f"{event.event_type}_{date_str}.jsonl"
            filepath = os.path.join(event_dir, filename)
            
            # Append event to file (JSONL format - one JSON per line)
            with open(filepath, 'a') as f:
                json.dump(event.model_dump(mode='json'), f)
                f.write('\n')
            
            logger.debug(f"Saved event {event.event_id} to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving event {event.event_id}: {e}")
            return False
    
    def save_alert(self, alert: Alert) -> bool:
        """
        Save alert to storage
        
        Args:
            alert: Alert to save
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get alert directory
            alert_dir = os.path.join(self.storage_dir, "alerts")
            
            # Create filename with timestamp
            date_str = alert.timestamp.strftime("%Y%m%d")
            filename = f"alerts_{date_str}.jsonl"
            filepath = os.path.join(alert_dir, filename)
            
            # Append alert to file
            with open(filepath, 'a') as f:
                json.dump(alert.to_dict(), f)
                f.write('\n')
            
            logger.debug(f"Saved alert {alert.alert_id} to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving alert {alert.alert_id}: {e}")
            return False
    
    def load_events(
        self,
        event_type: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Load events from storage
        
        Args:
            event_type: Type of events to load
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum number of events to return
        
        Returns:
            List of event dictionaries
        """
        try:
            event_dir = os.path.join(self.storage_dir, "events", event_type)
            
            if not os.path.exists(event_dir):
                return []
            
            events = []
            
            # Get all event files
            files = sorted(Path(event_dir).glob(f"{event_type}_*.jsonl"))
            
            # Filter by date range if specified
            if start_date or end_date:
                filtered_files = []
                for file in files:
                    # Extract date from filename
                    date_str = file.stem.split('_')[-1]
                    file_date = datetime.strptime(date_str, "%Y%m%d")
                    
                    if start_date and file_date < start_date:
                        continue
                    if end_date and file_date > end_date:
                        continue
                    
                    filtered_files.append(file)
                
                files = filtered_files
            
            # Read events from files
            for file in files:
                with open(file, 'r') as f:
                    for line in f:
                        if line.strip():
                            event = json.loads(line)
                            events.append(event)
                            
                            if limit and len(events) >= limit:
                                return events
            
            return events
            
        except Exception as e:
            logger.error(f"Error loading events: {e}")
            return []
    
    def load_alerts(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Load alerts from storage
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            severity: Filter by severity
            limit: Maximum number of alerts to return
        
        Returns:
            List of alert dictionaries
        """
        try:
            alert_dir = os.path.join(self.storage_dir, "alerts")
            
            if not os.path.exists(alert_dir):
                return []
            
            alerts = []
            
            # Get all alert files
            files = sorted(Path(alert_dir).glob("alerts_*.jsonl"))
            
            # Read alerts from files
            for file in files:
                with open(file, 'r') as f:
                    for line in f:
                        if line.strip():
                            alert = json.loads(line)
                            
                            # Apply filters
                            if severity and alert.get('severity') != severity:
                                continue
                            
                            timestamp = datetime.fromisoformat(alert['timestamp'])
                            if start_date and timestamp < start_date:
                                continue
                            if end_date and timestamp > end_date:
                                continue
                            
                            alerts.append(alert)
                            
                            if limit and len(alerts) >= limit:
                                return alerts
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error loading alerts: {e}")
            return []
    
    def cleanup_old_data(self):
        """
        Archive or delete data older than retention period
        """
        try:
            retention_days = self.config.retention_days
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            logger.info(f"Cleaning up data older than {retention_days} days")
            
            # Process event files
            events_dir = os.path.join(self.storage_dir, "events")
            for event_type_dir in Path(events_dir).iterdir():
                if event_type_dir.is_dir():
                    for file in event_type_dir.glob("*.jsonl"):
                        # Extract date from filename
                        date_str = file.stem.split('_')[-1]
                        file_date = datetime.strptime(date_str, "%Y%m%d")
                        
                        if file_date < cutoff_date:
                            # Archive or delete
                            archive_dir = os.path.join(
                                self.storage_dir, 
                                "archive", 
                                event_type_dir.name
                            )
                            os.makedirs(archive_dir, exist_ok=True)
                            
                            archive_path = os.path.join(archive_dir, file.name)
                            file.rename(archive_path)
                            logger.info(f"Archived {file.name}")
            
            # Process alert files
            alerts_dir = os.path.join(self.storage_dir, "alerts")
            for file in Path(alerts_dir).glob("alerts_*.jsonl"):
                date_str = file.stem.split('_')[-1]
                file_date = datetime.strptime(date_str, "%Y%m%d")
                
                if file_date < cutoff_date:
                    archive_dir = os.path.join(self.storage_dir, "archive", "alerts")
                    os.makedirs(archive_dir, exist_ok=True)
                    
                    archive_path = os.path.join(archive_dir, file.name)
                    file.rename(archive_path)
                    logger.info(f"Archived {file.name}")
            
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_storage_stats(self) -> dict:
        """Get storage statistics"""
        try:
            stats = {
                "total_size_bytes": 0,
                "event_files": 0,
                "alert_files": 0,
                "archive_files": 0
            }
            
            # Count event files
            events_dir = os.path.join(self.storage_dir, "events")
            if os.path.exists(events_dir):
                for file in Path(events_dir).rglob("*.jsonl"):
                    stats["event_files"] += 1
                    stats["total_size_bytes"] += file.stat().st_size
            
            # Count alert files
            alerts_dir = os.path.join(self.storage_dir, "alerts")
            if os.path.exists(alerts_dir):
                for file in Path(alerts_dir).glob("*.jsonl"):
                    stats["alert_files"] += 1
                    stats["total_size_bytes"] += file.stat().st_size
            
            # Count archive files
            archive_dir = os.path.join(self.storage_dir, "archive")
            if os.path.exists(archive_dir):
                for file in Path(archive_dir).rglob("*.jsonl"):
                    stats["archive_files"] += 1
                    stats["total_size_bytes"] += file.stat().st_size
            
            stats["total_size_mb"] = stats["total_size_bytes"] / (1024 * 1024)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}


# Global storage instance
_storage: Optional[StorageLayer] = None

def get_storage() -> StorageLayer:
    """Get global storage instance"""
    global _storage
    if _storage is None:
        _storage = StorageLayer()
    return _storage
