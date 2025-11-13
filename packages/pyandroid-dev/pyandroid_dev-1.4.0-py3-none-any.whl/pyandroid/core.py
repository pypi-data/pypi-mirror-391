"""Core Android application components.

This module provides the fundamental classes for building Android applications
with Python, including App, Activity, and Intent management.
"""

import logging
from typing import Dict, Any, Optional, Callable, Type


class PyAndroidError(Exception):
    """Base exception for PyAndroid errors."""
    pass


class ActivityNotFoundError(PyAndroidError):
    """Raised when attempting to start an unregistered activity."""
    pass


class InvalidStateError(PyAndroidError):
    """Raised when an invalid state transition is attempted."""
    pass


class AndroidApp:
    """Main Android Application class.
    
    This class represents the main Android application and manages
    the application lifecycle and global state.
    
    Example:
        >>> app = AndroidApp("MyApp", "com.example.myapp", use_gui=False)
        >>> app.register_activity("main", MainActivity)
        >>> app.start_activity("main")
        >>> app.run()
    """
    
    def __init__(self, app_name: str, package_name: str, use_gui: bool = True) -> None:
        """Initialize Android application.
        
        Args:
            app_name: Human readable application name
            package_name: Android package name (e.g. com.example.myapp)
            use_gui: Whether to use GUI rendering (requires Kivy)
        """
        self.app_name = app_name
        self.package_name = package_name
        self.use_gui = use_gui
        self.activities: Dict[str, Type['Activity']] = {}
        self.current_activity: Optional['Activity'] = None
        self.logger = logging.getLogger(f"PyAndroid.{app_name}")
        self.renderer = None
        
        # Initialize renderer if GUI is enabled
        if self.use_gui:
            try:
                from .backend import KivyRenderer
                if KivyRenderer is not None:
                    self.renderer = KivyRenderer(self)
                    self.logger.info("Kivy renderer initialized")
                else:
                    self.logger.warning("Kivy not available. Running in console mode.")
                    self.use_gui = False
            except ImportError:
                self.logger.warning("Kivy not available. Running in console mode.")
                self.use_gui = False
        
    def register_activity(self, activity_name: str, activity_class: Type['Activity']) -> None:
        """Register an activity with the application.
        
        Args:
            activity_name: Name identifier for the activity
            activity_class: Activity class to register
            
        Example:
            >>> app.register_activity("main", MainActivity)
        """
        self.activities[activity_name] = activity_class
        self.logger.info(f"Registered activity: {activity_name}")
        
    def start_activity(self, activity_name: str, **kwargs) -> None:
        """Start a specific activity.
        
        Args:
            activity_name: Name of activity to start
            **kwargs: Arguments to pass to activity constructor
            
        Raises:
            ActivityNotFoundError: If activity_name is not registered
            
        Example:
            >>> app.start_activity("main", user_id=123)
        """
        if activity_name not in self.activities:
            raise ActivityNotFoundError(
                f"Activity '{activity_name}' not registered. "
                f"Available activities: {list(self.activities.keys())}"
            )
        
        # Stop current activity if exists
        if self.current_activity:
            self.current_activity.stop()
            self.current_activity.destroy()
        
        activity_class = self.activities[activity_name]
        self.current_activity = activity_class(activity_name, **kwargs)
        self.current_activity.start()
        self.logger.info(f"Started activity: {activity_name}")
            
    def run(self) -> None:
        """Run the Android application.
        
        Example:
            >>> app.run()
        """
        self.logger.info(f"Starting {self.app_name} application")
        if self.current_activity:
            self.current_activity.resume()
            
            # If GUI is enabled, start Kivy rendering
            if self.use_gui and self.renderer:
                self.logger.info("Starting GUI mode with Kivy")
                self.renderer.run()
            else:
                self.logger.info("Running in console mode (no GUI)")
        else:
            self.logger.warning("No activity to run. Use start_activity() first.")


class Activity:
    """Android Activity base class.
    
    Represents a single screen in an Android application.
    
    Activity Lifecycle States:
        created -> started -> resumed -> paused -> stopped -> destroyed
    
    Example:
        >>> class MainActivity(Activity):
        ...     def on_start(self):
        ...         print("Activity started!")
        >>> activity = MainActivity("main")
        >>> activity.start()
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        "created": ["started"],
        "started": ["resumed", "stopped"],
        "resumed": ["paused"],
        "paused": ["resumed", "stopped"],
        "stopped": ["started", "destroyed"],
        "destroyed": []
    }
    
    def __init__(self, name: str, **kwargs) -> None:
        """Initialize activity.
        
        Args:
            name: Activity name identifier
            **kwargs: Additional activity arguments
        """
        self.name = name
        self.state = "created"
        self.views: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"PyAndroid.Activity.{name}")
        self.extras = kwargs
        
    def _validate_transition(self, new_state: str) -> None:
        """Validate if state transition is allowed.
        
        Args:
            new_state: Target state
            
        Raises:
            InvalidStateError: If transition is invalid
        """
        if new_state not in self.VALID_TRANSITIONS.get(self.state, []):
            raise InvalidStateError(
                f"Cannot transition from '{self.state}' to '{new_state}'"
            )
        
    def start(self) -> None:
        """Start the activity.
        
        Raises:
            InvalidStateError: If activity is not in 'created' state
        """
        self._validate_transition("started")
        self.state = "started"
        self.on_start()
        self.logger.info(f"Activity {self.name} started")
        
    def resume(self) -> None:
        """Resume the activity.
        
        Raises:
            InvalidStateError: If activity cannot be resumed from current state
        """
        self._validate_transition("resumed")
        self.state = "resumed"
        self.on_resume()
        self.logger.info(f"Activity {self.name} resumed")
        
    def pause(self) -> None:
        """Pause the activity.
        
        Raises:
            InvalidStateError: If activity is not in 'resumed' state
        """
        self._validate_transition("paused")
        self.state = "paused"
        self.on_pause()
        self.logger.info(f"Activity {self.name} paused")
        
    def stop(self) -> None:
        """Stop the activity.
        
        Raises:
            InvalidStateError: If activity cannot be stopped from current state
        """
        self._validate_transition("stopped")
        self.state = "stopped"
        self.on_stop()
        self.logger.info(f"Activity {self.name} stopped")
        
    def destroy(self) -> None:
        """Destroy the activity.
        
        Raises:
            InvalidStateError: If activity is not in 'stopped' state
        """
        self._validate_transition("destroyed")
        self.state = "destroyed"
        self.on_destroy()
        self.logger.info(f"Activity {self.name} destroyed")
        
    def on_start(self) -> None:
        """Called when activity starts. Override in subclasses."""
        pass
        
    def on_resume(self) -> None:
        """Called when activity resumes. Override in subclasses."""
        pass
        
    def on_pause(self) -> None:
        """Called when activity pauses. Override in subclasses."""
        pass
        
    def on_stop(self) -> None:
        """Called when activity stops. Override in subclasses."""
        pass
        
    def on_destroy(self) -> None:
        """Called when activity is destroyed. Override in subclasses."""
        pass
        
    def add_view(self, view_id: str, view: Any) -> None:
        """Add a view to this activity.
        
        Args:
            view_id: Unique identifier for the view
            view: View instance to add
            
        Example:
            >>> activity.add_view("text1", TextView("text1", "Hello"))
        """
        self.views[view_id] = view
        
    def get_view(self, view_id: str) -> Optional[Any]:
        """Get a view by ID.
        
        Args:
            view_id: View identifier
            
        Returns:
            View instance or None if not found
            
        Example:
            >>> text_view = activity.get_view("text1")
        """
        return self.views.get(view_id)
    
    def remove_view(self, view_id: str) -> bool:
        """Remove a view from this activity.
        
        Args:
            view_id: View identifier to remove
            
        Returns:
            True if view was removed, False if not found
        """
        if view_id in self.views:
            del self.views[view_id]
            return True
        return False


class Intent:
    """Android Intent for inter-component communication.
    
    Represents an intention to perform an action.
    
    Example:
        >>> intent = Intent("ACTION_VIEW", "DetailActivity")
        >>> intent.put_extra("user_id", 123)
        >>> intent.put_extra("username", "alice")
        >>> user_id = intent.get_extra("user_id")
    """
    
    def __init__(self, action: str, target: Optional[str] = None) -> None:
        """Initialize intent.
        
        Args:
            action: Action to perform (e.g., ACTION_VIEW, ACTION_EDIT)
            target: Target component (optional activity name)
        """
        self.action = action
        self.target = target
        self.extras: Dict[str, Any] = {}
        
    def put_extra(self, key: str, value: Any) -> None:
        """Add extra data to intent.
        
        Args:
            key: Data key
            value: Data value (any serializable type)
        """
        self.extras[key] = value
        
    def get_extra(self, key: str, default: Any = None) -> Any:
        """Get extra data from intent.
        
        Args:
            key: Data key
            default: Default value if key not found
            
        Returns:
            Data value or default
        """
        return self.extras.get(key, default)
    
    def has_extra(self, key: str) -> bool:
        """Check if intent has a specific extra.
        
        Args:
            key: Data key to check
            
        Returns:
            True if extra exists, False otherwise
        """
        return key in self.extras
    
    def get_all_extras(self) -> Dict[str, Any]:
        """Get all extras as a dictionary.
        
        Returns:
            Dictionary of all extras
        """
        return self.extras.copy()
