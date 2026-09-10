"""
Event System - Publish-subscribe pattern for component communication
"""

from typing import Dict, List, Callable, Any
from app.core.log import logger


class EventSystem:
    """Event system with publish-subscribe pattern."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_name: str, callback: Callable) -> None:
        """Subscribe to an event.
        
        Args:
            event_name: Name of the event to subscribe to
            callback: Function to call when event is published
        """
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)
    
    def unsubscribe(self, event_name: str, callback: Callable) -> None:
        """Unsubscribe from an event.
        
        Args:
            event_name: Name of the event to unsubscribe from
            callback: Function to remove from subscribers
        """
        if event_name in self._subscribers:
            try:
                self._subscribers[event_name].remove(callback)
            except ValueError:
                pass
    
    def publish(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        """Publish an event to all subscribers.

        Args:
            event_name: Name of the event to publish
            *args: Positional arguments to pass to subscribers
            **kwargs: Keyword arguments to pass to subscribers
        """
        if event_name in self._subscribers:
            for callback in self._subscribers[event_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}", exc_info=True)


# Global event system instance
event_system = EventSystem()
