"""
Event Receiver Module
Accepts, validates, and routes all incoming events
"""

import json
import logging
from typing import Union, Optional
from datetime import datetime
from uuid import uuid4

from backend.schemas import (
    AccessEvent,
    HoneypotEvent,
    NetworkEvent,
    EndpointEvent,
    TeapotEvent,
    EventType,
    UnifiedEvent
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventReceiver:
    """
    Central event receiver that validates and routes incoming events
    """
    
    def __init__(self):
        self.event_handlers = {}
        self.event_stats = {
            "total_received": 0,
            "total_processed": 0,
            "total_errors": 0,
            "by_type": {}
        }
    
    def register_handler(self, event_type: EventType, handler_func):
        """
        Register a handler function for a specific event type
        
        Args:
            event_type: Type of event to handle
            handler_func: Callback function(event) to process the event
        """
        self.event_handlers[event_type] = handler_func
        logger.info(f"Registered handler for {event_type}")
    
    def receive_event(
        self, 
        event_data: dict, 
        event_type: Optional[EventType] = None
    ) -> Union[UnifiedEvent, None]:
        """
        Receive and validate an event
        
        Args:
            event_data: Raw event data as dictionary
            event_type: Optional event type (will be inferred if not provided)
        
        Returns:
            UnifiedEvent if successful, None if validation fails
        """
        try:
            self.event_stats["total_received"] += 1
            
            # Infer event type if not provided
            if event_type is None:
                event_type = EventType(event_data.get("event_type"))
            
            # Ensure event_id exists
            if "event_id" not in event_data:
                event_data["event_id"] = self._generate_event_id(event_type)
            
            # Validate and parse based on event type
            validated_event = self._validate_event(event_data, event_type)
            
            if validated_event is None:
                logger.error(f"Failed to validate event: {event_data}")
                self.event_stats["total_errors"] += 1
                return None
            
            # Create unified event container
            unified_event = UnifiedEvent(
                event_data=validated_event,
                received_at=datetime.utcnow(),
                processed=False
            )
            
            # Update statistics
            self.event_stats["by_type"][event_type] = \
                self.event_stats["by_type"].get(event_type, 0) + 1
            
            logger.info(f"Received {event_type} event: {validated_event.event_id}")
            
            return unified_event
            
        except Exception as e:
            logger.error(f"Error receiving event: {e}")
            self.event_stats["total_errors"] += 1
            return None
    
    def route_event(self, unified_event: UnifiedEvent) -> bool:
        """
        Route event to appropriate handler
        
        Args:
            unified_event: Validated unified event
        
        Returns:
            True if successfully routed, False otherwise
        """
        try:
            event_data = unified_event.event_data
            event_type = event_data.event_type
            
            # Check if handler exists for this event type
            if event_type not in self.event_handlers:
                logger.warning(f"No handler registered for {event_type}")
                return False
            
            # Call the handler
            handler = self.event_handlers[event_type]
            handler(event_data)
            
            # Mark as processed
            unified_event.processed = True
            self.event_stats["total_processed"] += 1
            
            logger.info(f"Routed event {event_data.event_id} to {event_type} handler")
            return True
            
        except Exception as e:
            logger.error(f"Error routing event: {e}")
            return False
    
    def process_event(
        self, 
        event_data: dict, 
        event_type: Optional[EventType] = None
    ) -> bool:
        """
        Convenience method: receive and route in one call
        
        Args:
            event_data: Raw event data
            event_type: Optional event type
        
        Returns:
            True if successfully processed, False otherwise
        """
        unified_event = self.receive_event(event_data, event_type)
        if unified_event is None:
            return False
        return self.route_event(unified_event)
    
    def _validate_event(
        self, 
        event_data: dict, 
        event_type: EventType
    ) -> Optional[Union[AccessEvent, HoneypotEvent, NetworkEvent, EndpointEvent, TeapotEvent]]:
        """
        Validate event data against appropriate schema
        
        Args:
            event_data: Raw event data
            event_type: Type of event
        
        Returns:
            Validated event object or None
        """
        try:
            if event_type == EventType.ACCESS:
                return AccessEvent(**event_data)
            elif event_type == EventType.HONEYPOT:
                return HoneypotEvent(**event_data)
            elif event_type == EventType.NETWORK:
                return NetworkEvent(**event_data)
            elif event_type == EventType.ENDPOINT:
                return EndpointEvent(**event_data)
            elif event_type == EventType.TEAPOT:
                return TeapotEvent(**event_data)
            else:
                logger.error(f"Unknown event type: {event_type}")
                return None
        except Exception as e:
            logger.error(f"Validation error for {event_type}: {e}")
            return None
    
    def _generate_event_id(self, event_type: EventType) -> str:
        """
        Generate unique event ID
        
        Args:
            event_type: Type of event
        
        Returns:
            Unique event ID string
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid4())[:8]
        prefix = {
            EventType.ACCESS: "acc",
            EventType.HONEYPOT: "hp",
            EventType.NETWORK: "net",
            EventType.ENDPOINT: "ep",
            EventType.TEAPOT: "tea"
        }.get(event_type, "evt")
        
        return f"{prefix}_{timestamp}_{unique_id}"
    
    def get_statistics(self) -> dict:
        """Get receiver statistics"""
        return {
            **self.event_stats,
            "success_rate": (
                self.event_stats["total_processed"] / self.event_stats["total_received"]
                if self.event_stats["total_received"] > 0 else 0
            )
        }
    
    def reset_statistics(self):
        """Reset statistics counters"""
        self.event_stats = {
            "total_received": 0,
            "total_processed": 0,
            "total_errors": 0,
            "by_type": {}
        }
        logger.info("Statistics reset")


# Global event receiver instance
_event_receiver: Optional[EventReceiver] = None

def get_event_receiver() -> EventReceiver:
    """Get global event receiver instance"""
    global _event_receiver
    if _event_receiver is None:
        _event_receiver = EventReceiver()
    return _event_receiver
