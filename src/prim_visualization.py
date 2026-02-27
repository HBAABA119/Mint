"""
Prim Data Visualization
Provides interactive charting, 3D visualization, real-time dashboards,
geospatial visualization, and custom visualization components.
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ChartType(Enum):
    """Chart types"""
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    PIE = "pie"
    AREA = "area"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    SUNBURST = "sunburst"


class PlotType(Enum):
    """Plot types"""
    TWO_D = "2d"
    THREE_D = "3d"
    POLAR = "polar"
    GEOGRAPHIC = "geographic"


@dataclass
class DataPoint:
    """Data point"""
    x: Any
    y: Any
    z: Optional[Any] = None
    label: Optional[str] = None
    color: Optional[str] = None
    size: Optional[float] = None


@dataclass
class Axis:
    """Chart axis"""
    label: str
    min: Optional[float] = None
    max: Optional[float] = None
    type: str = "linear"
    scale: str = "linear"


class Chart:
    """Base chart class"""

    def __init__(self, chart_type: ChartType, title: str = ""):
        self.chart_type = chart_type
        self.title = title
        self.data: List[DataPoint] = []
        self.x_axis = Axis("X")
        self.y_axis = Axis("Y")
        self.z_axis: Optional[Axis] = None
        self.legend: bool = True
        self.grid: bool = True
        self.annotations: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}

    def add_data(self, data_points: List[DataPoint]):
        """Add data points to chart"""
        self.data.extend(data_points)

    def set_axis(self, axis: str, label: str, min_val: Optional[float] = None,
                max_val: Optional[float] = None, scale: str = "linear"):
        """Set axis properties"""
        axis_obj = Axis(label, min_val, max_val, scale=scale)
        if axis == "x":
            self.x_axis = axis_obj
        elif axis == "y":
            self.y_axis = axis_obj
        elif axis == "z":
            self.z_axis = axis_obj

    def add_annotation(self, x: Any, y: Any, text: str):
        """Add annotation"""
        self.annotations.append({"x": x, "y": y, "text": text})

    def to_dict(self) -> Dict[str, Any]:
        """Convert chart to dictionary"""
        return {
            "type": self.chart_type.value,
            "title": self.title,
            "data": [
                {
                    "x": dp.x,
                    "y": dp.y,
                    "z": dp.z,
                    "label": dp.label,
                    "color": dp.color,
                    "size": dp.size
                }
                for dp in self.data
            ],
            "x_axis": {
                "label": self.x_axis.label,
                "min": self.x_axis.min,
                "max": self.x_axis.max,
                "scale": self.x_axis.scale
            },
            "y_axis": {
                "label": self.y_axis.label,
                "min": self.y_axis.min,
                "max": self.y_axis.max,
                "scale": self.y_axis.scale
            },
            "z_axis": {
                "label": self.z_axis.label,
                "min": self.z_axis.min,
                "max": self.z_axis.max,
                "scale": self.z_axis.scale
            } if self.z_axis else None,
            "legend": self.legend,
            "grid": self.grid,
            "annotations": self.annotations,
            "metadata": self.metadata
        }

    def to_json(self) -> str:
        """Convert chart to JSON"""
        return json.dumps(self.to_dict(), indent=2)


class LineChart(Chart):
    """Line chart"""

    def __init__(self, title: str = ""):
        super().__init__(ChartType.LINE, title)
        self.line_width: float = 2.0
        self.curve: str = "linear"
        self.fill_area: bool = False

    def set_line_style(self, width: float = 2.0, curve: str = "linear", fill: bool = False):
        """Set line style"""
        self.line_width = width
        self.curve = curve
        self.fill_area = fill


class BarChart(Chart):
    """Bar chart"""

    def __init__(self, title: str = ""):
        super().__init__(ChartType.BAR, title)
        self.orientation: str = "vertical"
        self.bar_width: float = 0.8
        self.stack_groups: bool = False

    def set_bar_style(self, orientation: str = "vertical", width: float = 0.8,
                      stack: bool = False):
        """Set bar style"""
        self.orientation = orientation
        self.bar_width = width
        self.stack_groups = stack


class ScatterChart(Chart):
    """Scatter chart"""

    def __init__(self, title: str = ""):
        super().__init__(ChartType.SCATTER, title)
        self.marker_size: float = 6.0
        self.marker_shape: str = "circle"
        self.trend_line: bool = False

    def set_marker_style(self, size: float = 6.0, shape: str = "circle",
                         trend_line: bool = False):
        """Set marker style"""
        self.marker_size = size
        self.marker_shape = shape
        self.trend_line = trend_line


class ThreeDPlot(Chart):
    """3D plot"""

    def __init__(self, title: str = ""):
        super().__init__(ChartType.SCATTER, title)
        self.plot_type = PlotType.THREE_D
        self.rotation: Tuple[float, float, float] = (0, 0, 0)
        self.z_axis = Axis("Z")

    def set_rotation(self, x: float, y: float, z: float):
        """Set 3D rotation"""
        self.rotation = (x, y, z)


class Dashboard:
    """Real-time dashboard"""

    def __init__(self, title: str = "Dashboard"):
        self.title = title
        self.charts: List[Chart] = []
        self.layout: str = "grid"
        self.refresh_interval: int = 5
        self.theme: str = "light"
        self.widgets: List[Dict[str, Any]] = []

    def add_chart(self, chart: Chart):
        """Add chart to dashboard"""
        self.charts.append(chart)

    def add_widget(self, widget_type: str, config: Dict[str, Any]):
        """Add widget to dashboard"""
        self.widgets.append({
            "type": widget_type,
            "config": config
        })

    def set_layout(self, layout: str = "grid"):
        """Set dashboard layout"""
        self.layout = layout

    def set_theme(self, theme: str = "light"):
        """Set dashboard theme"""
        self.theme = theme

    def to_dict(self) -> Dict[str, Any]:
        """Convert dashboard to dictionary"""
        return {
            "title": self.title,
            "charts": [chart.to_dict() for chart in self.charts],
            "layout": self.layout,
            "refresh_interval": self.refresh_interval,
            "theme": self.theme,
            "widgets": self.widgets
        }


class GeospatialVisualization:
    """Geospatial visualization"""

    def __init__(self):
        self.map_type: str = "world"
        self.center: Tuple[float, float] = (0, 0)
        self.zoom: int = 2
        self.markers: List[Dict[str, Any]] = []
        self.regions: List[Dict[str, Any]] = []
        self.heatmap_data: List[Dict[str, Any]] = []

    def add_marker(self, lat: float, lon: float, label: str = "", popup: str = ""):
        """Add marker"""
        self.markers.append({
            "lat": lat,
            "lon": lon,
            "label": label,
            "popup": popup
        })

    def add_region(self, name: str, coordinates: List[Tuple[float, float]],
                   color: str = "blue"):
        """Add region"""
        self.regions.append({
            "name": name,
            "coordinates": coordinates,
            "color": color
        })

    def set_heatmap(self, data: List[Tuple[float, float, float]]):
        """Set heatmap data"""
        self.heatmap_data = [
            {"lat": lat, "lon": lon, "value": value}
            for lat, lon, value in data
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "map_type": self.map_type,
            "center": self.center,
            "zoom": self.zoom,
            "markers": self.markers,
            "regions": self.regions,
            "heatmap_data": self.heatmap_data
        }


class CustomVisualization:
    """Custom visualization components"""

    def __init__(self):
        self.components: List[Dict[str, Any]] = []
        self.interactions: List[Dict[str, Any]] = []
        self.animations: List[Dict[str, Any]] = []

    def add_component(self, component_type: str, config: Dict[str, Any]):
        """Add custom component"""
        self.components.append({
            "type": component_type,
            "config": config
        })

    def add_interaction(self, event: str, action: str, target: str):
        """Add interaction"""
        self.interactions.append({
            "event": event,
            "action": action,
            "target": target
        })

    def add_animation(self, animation_type: str, duration: float, config: Dict[str, Any]):
        """Add animation"""
        self.animations.append({
            "type": animation_type,
            "duration": duration,
            "config": config
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "components": self.components,
            "interactions": self.interactions,
            "animations": self.animations
        }


class VisualizationEngine:
    """Visualization engine"""

    @staticmethod
    def create_line_chart(title: str = "", data: Optional[List[DataPoint]] = None) -> LineChart:
        """Create line chart"""
        chart = LineChart(title)
        if data:
            chart.add_data(data)
        return chart

    @staticmethod
    def create_bar_chart(title: str = "", data: Optional[List[DataPoint]] = None) -> BarChart:
        """Create bar chart"""
        chart = BarChart(title)
        if data:
            chart.add_data(data)
        return chart

    @staticmethod
    def create_scatter_chart(title: str = "", data: Optional[List[DataPoint]] = None) -> ScatterChart:
        """Create scatter chart"""
        chart = ScatterChart(title)
        if data:
            chart.add_data(data)
        return chart

    @staticmethod
    def create_3d_plot(title: str = "", data: Optional[List[DataPoint]] = None) -> ThreeDPlot:
        """Create 3D plot"""
        chart = ThreeDPlot(title)
        if data:
            chart.add_data(data)
        return chart

    @staticmethod
    def create_dashboard(title: str = "Dashboard") -> Dashboard:
        """Create dashboard"""
        return Dashboard(title)

    @staticmethod
    def create_geospatial() -> GeospatialVisualization:
        """Create geospatial visualization"""
        return GeospatialVisualization()

    @staticmethod
    def create_custom() -> CustomVisualization:
        """Create custom visualization"""
        return CustomVisualization()


def main():
    """Main entry point for testing"""
    print("Testing Data Visualization...")

    # Test Line Chart
    engine = VisualizationEngine()
    line_data = [DataPoint(i, i * 2) for i in range(10)]
    line_chart = engine.create_line_chart("Test Line Chart", line_data)
    print(f"Line chart: {len(line_chart.data)} points")

    # Test Bar Chart
    bar_data = [DataPoint(i, i * 3) for i in range(5)]
    bar_chart = engine.create_bar_chart("Test Bar Chart", bar_data)
    print(f"Bar chart: {len(bar_chart.data)} points")

    # Test Scatter Chart
    scatter_data = [DataPoint(i, i * i) for i in range(10)]
    scatter_chart = engine.create_scatter_chart("Test Scatter Chart", scatter_data)
    print(f"Scatter chart: {len(scatter_chart.data)} points")

    # Test 3D Plot
    plot3d_data = [DataPoint(i, i * 2, i * 3) for i in range(10)]
    plot3d = engine.create_3d_plot("Test 3D Plot", plot3d_data)
    print(f"3D plot: {len(plot3d.data)} points")

    # Test Dashboard
    dashboard = engine.create_dashboard("Test Dashboard")
    dashboard.add_chart(line_chart)
    dashboard.add_chart(bar_chart)
    dashboard.add_widget("metric", {"value": 100, "label": "Test Metric"})
    print(f"Dashboard: {len(dashboard.charts)} charts, {len(dashboard.widgets)} widgets")

    # Test Geospatial
    geo = engine.create_geospatial()
    geo.add_marker(40.7128, -74.0060, "New York", "The Big Apple")
    geo.add_marker(51.5074, -0.1278, "London", "Capital of UK")
    print(f"Geospatial: {len(geo.markers)} markers")

    # Test Custom Visualization
    custom = engine.create_custom()
    custom.add_component("custom_element", {"text": "Hello, World!"})
    custom.add_interaction("click", "highlight", "element1")
    print(f"Custom: {len(custom.components)} components")

    print("\nData Visualization initialized successfully")


if __name__ == "__main__":
    main()
