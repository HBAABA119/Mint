"""
Prim Data Processing
Provides DataFrame operations, statistical analysis functions, data visualization tools,
streaming data processing, and big data integration.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class DataType(Enum):
    """Data types"""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    TEXT = "text"
    BOOLEAN = "boolean"
    DATETIME = "datetime"


@dataclass
class Column:
    """DataFrame column"""
    name: str
    data: List[Any]
    dtype: DataType = DataType.NUMERIC

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def mean(self) -> float:
        """Calculate mean"""
        if self.dtype == DataType.NUMERIC:
            return np.mean(self.data)
        raise ValueError("Cannot calculate mean for non-numeric data")

    def std(self) -> float:
        """Calculate standard deviation"""
        if self.dtype == DataType.NUMERIC:
            return np.std(self.data)
        raise ValueError("Cannot calculate std for non-numeric data")

    def min(self) -> float:
        """Calculate minimum"""
        if self.dtype == DataType.NUMERIC:
            return np.min(self.data)
        raise ValueError("Cannot calculate min for non-numeric data")

    def max(self) -> float:
        """Calculate maximum"""
        if self.dtype == DataType.NUMERIC:
            return np.max(self.data)
        raise ValueError("Cannot calculate max for non-numeric data")

    def sum(self) -> float:
        """Calculate sum"""
        if self.dtype == DataType.NUMERIC:
            return np.sum(self.data)
        raise ValueError("Cannot calculate sum for non-numeric data")

    def count(self, value: Any) -> int:
        """Count occurrences of value"""
        return self.data.count(value)

    def unique(self) -> List[Any]:
        """Get unique values"""
        return list(set(self.data))


class DataFrame:
    """DataFrame for tabular data manipulation"""

    def __init__(self, name: str = "dataframe"):
        self.name = name
        self.columns: Dict[str, Column] = {}
        self.n_rows = 0

    def add_column(self, name: str, data: List[Any], dtype: DataType = DataType.NUMERIC):
        """Add a column to the DataFrame"""
        if len(data) != self.n_rows and self.n_rows > 0:
            raise ValueError("Column length must match DataFrame length")

        self.columns[name] = Column(name=name, data=data, dtype=dtype)
        self.n_rows = len(data)

    def __len__(self):
        return self.n_rows

    def __getitem__(self, column_name: str) -> Column:
        return self.columns[column_name]

    def __setitem__(self, column_name: str, data: List[Any]):
        if column_name in self.columns:
            self.columns[column_name].data = data
        else:
            self.add_column(column_name, data)

    def head(self, n: int = 5) -> 'DataFrame':
        """Get first n rows"""
        df = DataFrame(f"{self.name}_head")
        for name, column in self.columns.items():
            df.add_column(name, column.data[:n], column.dtype)
        return df

    def tail(self, n: int = 5) -> 'DataFrame':
        """Get last n rows"""
        df = DataFrame(f"{self.name}_tail")
        for name, column in self.columns.items():
            df.add_column(name, column.data[-n:], column.dtype)
        return df

    def filter(self, condition: Callable[[Dict[str, Any]], bool]) -> 'DataFrame':
        """Filter rows based on condition"""
        indices = []
        for i in range(self.n_rows):
            row = {name: col[i] for name, col in self.columns.items()}
            if condition(row):
                indices.append(i)

        df = DataFrame(f"{self.name}_filtered")
        for name, column in self.columns.items():
            df.add_column(name, [column.data[i] for i in indices], column.dtype)

        return df

    def select(self, *column_names: str) -> 'DataFrame':
        """Select specific columns"""
        df = DataFrame(f"{self.name}_selected")
        for name in column_names:
            if name in self.columns:
                df.add_column(name, self.columns[name].data, self.columns[name].dtype)
        return df

    def group_by(self, column_name: str) -> Dict[Any, 'DataFrame']:
        """Group by column"""
        groups = {}
        for i in range(self.n_rows):
            key = self.columns[column_name].data[i]
            if key not in groups:
                groups[key] = DataFrame(f"{self.name}_group_{key}")
                for name, column in self.columns.items():
                    groups[key].add_column(name, [], column.dtype)
            for name, column in self.columns.items():
                groups[key].columns[name].data.append(column.data[i])
                groups[key].n_rows += 1

        return groups

    def join(self, other: 'DataFrame', on: str, how: str = "inner") -> 'DataFrame':
        """Join with another DataFrame"""
        if on not in self.columns or on not in other.columns:
            raise ValueError(f"Column '{on}' not found in both DataFrames")

        result = DataFrame(f"{self.name}_joined")
        joined_data = {}

        if how == "inner":
            for i in range(self.n_rows):
                for j in range(other.n_rows):
                    if self.columns[on].data[i] == other.columns[on].data[j]:
                        for name, column in self.columns.items():
                            if name not in joined_data:
                                joined_data[name] = []
                            joined_data[name].append(column.data[i])
                        for name, column in other.columns.items():
                            if name != on and name not in joined_data:
                                joined_data[name] = []
                            if name != on:
                                joined_data[name].append(column.data[j])

        for name, data in joined_data.items():
            dtype = self.columns[name].dtype if name in self.columns else other.columns[name].dtype
            result.add_column(name, data, dtype)

        return result

    def sort_by(self, column_name: str, ascending: bool = True) -> 'DataFrame':
        """Sort by column"""
        if column_name not in self.columns:
            raise ValueError(f"Column '{column_name}' not found")

        indices = sorted(range(self.n_rows), key=lambda i: self.columns[column_name].data[i], reverse=not ascending)

        df = DataFrame(f"{self.name}_sorted")
        for name, column in self.columns.items():
            df.add_column(name, [column.data[i] for i in indices], column.dtype)

        return df

    def aggregate(self, aggregations: Dict[str, str]) -> Dict[str, float]:
        """Aggregate columns"""
        results = {}
        for column_name, agg_func in aggregations.items():
            if column_name not in self.columns:
                continue

            column = self.columns[column_name]
            if agg_func == "mean":
                results[f"{column_name}_mean"] = column.mean()
            elif agg_func == "std":
                results[f"{column_name}_std"] = column.std()
            elif agg_func == "min":
                results[f"{column_name}_min"] = column.min()
            elif agg_func == "max":
                results[f"{column_name}_max"] = column.max()
            elif agg_func == "sum":
                results[f"{column_name}_sum"] = column.sum()
            elif agg_func == "count":
                results[f"{column_name}_count"] = len(column)

        return results

    def to_dict(self) -> Dict[str, List[Any]]:
        """Convert to dictionary"""
        return {name: column.data for name, column in self.columns.items()}

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict())

    def describe(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all numeric columns"""
        stats = {}
        for name, column in self.columns.items():
            if column.dtype == DataType.NUMERIC:
                stats[name] = {
                    "mean": column.mean(),
                    "std": column.std(),
                    "min": column.min(),
                    "max": column.max(),
                    "count": len(column)
                }
        return stats


class Statistics:
    """Statistical analysis functions"""

    @staticmethod
    def mean(data: List[float]) -> float:
        """Calculate mean"""
        return np.mean(data)

    @staticmethod
    def median(data: List[float]) -> float:
        """Calculate median"""
        return np.median(data)

    @staticmethod
    def mode(data: List[Any]) -> Any:
        """Calculate mode"""
        from collections import Counter
        return Counter(data).most_common(1)[0][0]

    @staticmethod
    def std(data: List[float]) -> float:
        """Calculate standard deviation"""
        return np.std(data)

    @staticmethod
    def variance(data: List[float]) -> float:
        """Calculate variance"""
        return np.var(data)

    @staticmethod
    def percentile(data: List[float], p: float) -> float:
        """Calculate percentile"""
        return np.percentile(data, p)

    @staticmethod
    def correlation(x: List[float], y: List[float]) -> float:
        """Calculate correlation coefficient"""
        return np.corrcoef(x, y)[0, 1]

    @staticmethod
    def covariance(x: List[float], y: List[float]) -> float:
        """Calculate covariance"""
        return np.cov(x, y)[0, 1]


class DataVisualizer:
    """Data visualization tools"""

    @staticmethod
    def histogram(data: List[float], bins: int = 10, title: str = "Histogram"):
        """Generate histogram data"""
        hist, bin_edges = np.histogram(data, bins=bins)
        return {
            "type": "histogram",
            "title": title,
            "hist": hist.tolist(),
            "bins": bin_edges.tolist()
        }

    @staticmethod
    def scatter(x: List[float], y: List[float], title: str = "Scatter Plot"):
        """Generate scatter plot data"""
        return {
            "type": "scatter",
            "title": title,
            "x": x,
            "y": y
        }

    @staticmethod
    def line(x: List[float], y: List[float], title: str = "Line Plot"):
        """Generate line plot data"""
        return {
            "type": "line",
            "title": title,
            "x": x,
            "y": y
        }

    @staticmethod
    def bar(categories: List[str], values: List[float], title: str = "Bar Chart"):
        """Generate bar chart data"""
        return {
            "type": "bar",
            "title": title,
            "categories": categories,
            "values": values
        }


class StreamProcessor:
    """Streaming data processing"""

    def __init__(self, name: str = "stream"):
        self.name = name
        self.buffer: List[Dict[str, Any]] = []
        self.buffer_size = 1000

    def process(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process incoming data"""
        self.buffer.append(data)

        if len(self.buffer) > self.buffer_size:
            self.buffer.pop(0)

        return data

    def aggregate_window(self, window_size: int, agg_func: Callable) -> List[Any]:
        """Aggregate over sliding window"""
        results = []
        for i in range(len(self.buffer) - window_size + 1):
            window = self.buffer[i:i + window_size]
            results.append(agg_func(window))
        return results

    def filter_stream(self, condition: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
        """Filter stream"""
        return [item for item in self.buffer if condition(item)]

    def transform_stream(self, transform: Callable[[Dict[str, Any]], Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform stream"""
        return [transform(item) for item in self.buffer]

    def get_buffer(self) -> List[Dict[str, Any]]:
        """Get current buffer"""
        return self.buffer.copy()


def read_csv(filepath: str) -> DataFrame:
    """Read CSV file into DataFrame"""
    df = DataFrame(filepath)
    with open(filepath, 'r') as f:
        lines = f.readlines()
        if lines:
            headers = lines[0].strip().split(',')
            for header in headers:
                df.add_column(header.strip(), [])

            for line in lines[1:]:
                values = line.strip().split(',')
                for i, value in enumerate(values):
                    df.columns[df.columns.keys()[i]].data.append(value)
                df.n_rows += 1

    return df


def create_dataframe(name: str = "dataframe") -> DataFrame:
    """Create a new DataFrame"""
    return DataFrame(name)


def main():
    """Main entry point for testing"""
    print("Testing Data Processing...")

    # Create DataFrame
    df = create_dataframe("test_data")
    df.add_column("id", [1, 2, 3, 4, 5])
    df.add_column("value", [10, 20, 30, 40, 50])
    df.add_column("category", ["A", "B", "A", "B", "A"])

    print(f"DataFrame created with {len(df)} rows")

    # Test operations
    print(f"Head:\n{df.head().to_json()}")
    print(f"Statistics: {df.describe()}")

    # Test filtering
    filtered = df.filter(lambda row: row["value"] > 25)
    print(f"Filtered: {len(filtered)} rows")

    # Test grouping
    groups = df.group_by("category")
    print(f"Groups: {list(groups.keys())}")

    # Test statistics
    stats = Statistics()
    print(f"Mean: {stats.mean([10, 20, 30, 40, 50])}")
    print(f"Correlation: {stats.correlation([1, 2, 3, 4, 5], [10, 20, 30, 40, 50])}")

    # Test visualization
    viz = DataVisualizer()
    histogram = viz.histogram([1, 2, 3, 4, 5, 5, 5, 6, 6, 7])
    print(f"Histogram: {histogram['type']}")

    # Test streaming
    stream = StreamProcessor()
    for i in range(10):
        stream.process({"id": i, "value": i * 10})
    print(f"Stream buffer: {len(stream.get_buffer())}")

    print("\nData Processing initialized successfully")


if __name__ == "__main__":
    main()
