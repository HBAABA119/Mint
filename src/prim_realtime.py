"""
Prim Real-time Analytics
Provides streaming analytics, event processing, real-time dashboards,
alert systems, and performance monitoring.
"""

import time
import threading
import queue
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


class EventType(Enum):
    """Event types"""
    DATA = "data"
    ALERT = "alert"
    METRIC = "metric"
    STATUS = "status"
    ERROR = "error"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Event:
    """Event"""
    id: str
    type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Alert"""
    id: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    source: str = ""
    acknowledged: bool = False
    resolved: bool = False


class EventStream:
    """Event stream"""

    def __init__(self, name: str = "stream"):
        self.name = name
        self.events: List[Event] = []
        self.subscribers: List[Callable] = []
        self.buffer_size = 10000
        self.running = False

    def publish(self, event: Event):
        """Publish event to stream"""
        self.events.append(event)

        # Maintain buffer size
        if len(self.events) > self.buffer_size:
            self.events = self.events[-self.buffer_size:]

        # Notify subscribers
        for subscriber in self.subscribers:
            try:
                subscriber(event)
            except Exception as e:
                print(f"Subscriber error: {e}")

    def subscribe(self, callback: Callable):
        """Subscribe to events"""
        self.subscribers.append(callback)

    def unsubscribe(self, callback: Callable):
        """Unsubscribe from events"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    def get_events(self, event_type: Optional[EventType] = None,
                   since: Optional[datetime] = None) -> List[Event]:
        """Get events"""
        events = self.events

        if event_type:
            events = [e for e in events if e.type == event_type]

        if since:
            events = [e for e in events if e.timestamp >= since]

        return events


class EventProcessor:
    """Event processing"""

    def __init__(self):
        self.processors: List[Callable] = []
        self.filters: List[Callable] = []
        self.aggregations: List[Callable] = []

    def add_processor(self, processor: Callable):
        """Add event processor"""
        self.processors.append(processor)

    def add_filter(self, filter_func: Callable):
        """Add event filter"""
        self.filters.append(filter_func)

    def add_aggregation(self, aggregation: Callable):
        """Add aggregation function"""
        self.aggregations.append(aggregation)

    def process_event(self, event: Event) -> Optional[Event]:
        """Process event"""
        # Apply filters
        for filter_func in self.filters:
            if not filter_func(event):
                return None

        # Apply processors
        for processor in self.processors:
            try:
                event = processor(event)
            except Exception as e:
                print(f"Processor error: {e}")

        # Apply aggregations
        for aggregation in self.aggregations:
            try:
                aggregation(event)
            except Exception as e:
                print(f"Aggregation error: {e}")

        return event


class RealtimeDashboard:
    """Real-time dashboard"""

    def __init__(self, name: str = "dashboard"):
        self.name = name
        self.widgets: List[Dict[str, Any]] = []
        self.metrics: Dict[str, Any] = {}
        self.alerts: List[Alert] = []
        self.refresh_interval: int = 1
        self.running = False

    def add_widget(self, widget_type: str, config: Dict[str, Any]):
        """Add widget to dashboard"""
        self.widgets.append({
            "type": widget_type,
            "config": config
        })

    def update_metric(self, name: str, value: Any):
        """Update metric"""
        self.metrics[name] = value

    def add_alert(self, alert: Alert):
        """Add alert"""
        self.alerts.append(alert)

    def get_data(self) -> Dict[str, Any]:
        """Get dashboard data"""
        return {
            "name": self.name,
            "widgets": self.widgets,
            "metrics": self.metrics,
            "alerts": self.alerts[-10:],  # Last 10 alerts
            "timestamp": datetime.now().isoformat()
        }

    def to_json(self) -> str:
        """Convert dashboard to JSON"""
        return json.dumps(self.get_data(), indent=2)


class AlertManager:
    """Alert management"""

    def __init__(self):
        self.alerts: List[Alert] = []
        self.rules: List[Dict[str, Any]] = []
        self.subscribers: List[Callable] = []

    def add_rule(self, condition: Callable, severity: AlertSeverity, message_template: str):
        """Add alert rule"""
        self.rules.append({
            "condition": condition,
            "severity": severity,
            "message_template": message_template
        })

    def check_rules(self, data: Dict[str, Any]):
        """Check alert rules"""
        for rule in self.rules:
            try:
                if rule["condition"](data):
                    alert = Alert(
                        id=str(hash(f"{rule['severity']}_{time.time()}")),
                        severity=rule["severity"],
                        message=rule["message_template"].format(**data),
                        timestamp=datetime.now(),
                        source="alert_manager"
                    )
                    self.add_alert(alert)
            except Exception as e:
                print(f"Rule check error: {e}")

    def add_alert(self, alert: Alert):
        """Add alert"""
        self.alerts.append(alert)

        # Notify subscribers
        for subscriber in self.subscribers:
            try:
                subscriber(alert)
            except Exception as e:
                print(f"Subscriber error: {e}")

    def subscribe(self, callback: Callable):
        """Subscribe to alerts"""
        self.subscribers.append(callback)

    def acknowledge_alert(self, alert_id: str):
        """Acknowledge alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True

    def resolve_alert(self, alert_id: str):
        """Resolve alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True

    def get_active_alerts(self) -> List[Alert]:
        """Get active alerts"""
        return [a for a in self.alerts if not a.resolved]


class PerformanceMonitor:
    """Performance monitoring"""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.counters: Dict[str, int] = {}
        self.timers: Dict[str, List[float]] = {}
        self.start_times: Dict[str, float] = {}

    def record_metric(self, name: str, value: float):
        """Record metric value"""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)

        # Keep last 1000 values
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]

    def increment_counter(self, name: str, amount: int = 1):
        """Increment counter"""
        if name not in self.counters:
            self.counters[name] = 0
        self.counters[name] += amount

    def start_timer(self, name: str):
        """Start timer"""
        self.start_times[name] = time.time()

    def stop_timer(self, name: str) -> float:
        """Stop timer and return elapsed time"""
        if name not in self.start_times:
            return 0.0

        elapsed = time.time() - self.start_times[name]
        del self.start_times[name]

        if name not in self.timers:
            self.timers[name] = []
        self.timers[name].append(elapsed)

        return elapsed

    def get_metric_stats(self, name: str) -> Dict[str, float]:
        """Get metric statistics"""
        if name not in self.metrics or not self.metrics[name]:
            return {}

        values = self.metrics[name]
        return {
            "mean": np.mean(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values),
            "count": len(values)
        }

    def get_counter(self, name: str) -> int:
        """Get counter value"""
        return self.counters.get(name, 0)

    def get_timer_stats(self, name: str) -> Dict[str, float]:
        """Get timer statistics"""
        if name not in self.timers or not self.timers[name]:
            return {}

        values = self.timers[name]
        return {
            "mean": np.mean(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values),
            "count": len(values)
        }

    def get_all_stats(self) -> Dict[str, Any]:
        """Get all statistics"""
        return {
            "metrics": {name: self.get_metric_stats(name) for name in self.metrics},
            "counters": self.counters,
            "timers": {name: self.get_timer_stats(name) for name in self.timers}
        }


class StreamingAnalytics:
    """Streaming analytics engine"""

    def __init__(self, name: str = "analytics"):
        self.name = name
        self.stream = EventStream(name)
        self.processor = EventProcessor()
        self.dashboard = RealtimeDashboard(name)
        self.alert_manager = AlertManager()
        self.monitor = PerformanceMonitor()
        self.running = False

    def add_source(self, source: Callable):
        """Add data source"""
        self.stream.subscribe(source)

    def add_processor(self, processor: Callable):
        """Add event processor"""
        self.processor.add_processor(processor)

    def add_filter(self, filter_func: Callable):
        """Add event filter"""
        self.processor.add_filter(filter_func)

    def add_rule(self, condition: Callable, severity: AlertSeverity, message: str):
        """Add alert rule"""
        self.alert_manager.add_rule(condition, severity, message)

    def start(self):
        """Start streaming analytics"""
        self.running = True

        def process_loop():
            while self.running:
                # Process events
                events = self.stream.get_events()
                for event in events:
                    processed = self.processor.process_event(event)

                    if processed:
                        # Update metrics
                        self.monitor.increment_counter("events_processed")

                        # Check alert rules
                        self.alert_manager.check_rules(event.data)

                        # Update dashboard
                        if event.type == EventType.METRIC:
                            self.dashboard.update_metric(event.data.get("name", ""), event.data.get("value"))

                time.sleep(0.1)

        self.thread = threading.Thread(target=process_loop)
        self.thread.start()

    def stop(self):
        """Stop streaming analytics"""
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()

    def get_status(self) -> Dict[str, Any]:
        """Get analytics status"""
        return {
            "name": self.name,
            "running": self.running,
            "events_processed": self.monitor.get_counter("events_processed"),
            "active_alerts": len(self.alert_manager.get_active_alerts()),
            "metrics": self.monitor.get_all_stats(),
            "timestamp": datetime.now().isoformat()
        }


def create_analytics(name: str = "analytics") -> StreamingAnalytics:
    """Create streaming analytics engine"""
    return StreamingAnalytics(name)


def main():
    """Main entry point for testing"""
    print("Testing Real-time Analytics...")

    # Create analytics engine
    analytics = create_analytics("test_analytics")

    # Add event processor
    def processor(event):
        event.data["processed"] = True
        return event

    analytics.add_processor(processor)

    # Add filter
    def filter_func(event):
        return event.type != EventType.ERROR

    analytics.add_filter(filter_func)

    # Add alert rule
    def high_value_condition(data):
        return data.get("value", 0) > 100

    analytics.add_rule(high_value_condition, AlertSeverity.WARNING, "High value detected: {value}")

    # Publish some events
    event1 = Event(
        id="1",
        type=EventType.METRIC,
        timestamp=datetime.now(),
        data={"name": "cpu_usage", "value": 75.5}
    )

    event2 = Event(
        id="2",
        type=EventType.METRIC,
        timestamp=datetime.now(),
        data={"name": "memory_usage", "value": 150.0}
    )

    analytics.stream.publish(event1)
    analytics.stream.publish(event2)

    # Start analytics
    analytics.start()
    time.sleep(1)
    analytics.stop()

    # Get status
    status = analytics.get_status()
    print(f"Status: {status['events_processed']} events processed")
    print(f"Active alerts: {status['active_alerts']}")

    # Test dashboard
    dashboard = RealtimeDashboard("test_dashboard")
    dashboard.add_widget("metric", {"title": "CPU Usage", "value": 75})
    dashboard.update_metric("cpu", 80)
    print(f"Dashboard metrics: {dashboard.metrics}")

    # Test alert manager
    alert_manager = AlertManager()
    alert = Alert(
        id="test_alert",
        severity=AlertSeverity.WARNING,
        message="Test alert",
        timestamp=datetime.now()
    )
    alert_manager.add_alert(alert)
    print(f"Active alerts: {len(alert_manager.get_active_alerts())}")

    # Test performance monitor
    monitor = PerformanceMonitor()
    monitor.record_metric("response_time", 0.5)
    monitor.record_metric("response_time", 0.6)
    monitor.record_metric("response_time", 0.7)
    stats = monitor.get_metric_stats("response_time")
    print(f"Response time stats: {stats}")

    print("\nReal-time Analytics initialized successfully")


if __name__ == "__main__":
    main()
