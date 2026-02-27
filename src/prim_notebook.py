"""
Prim Notebook Interface
Provides interactive development environment with cell execution, rich output formatting,
collaboration features, version control integration, and notebook serialization.
"""

import json
import uuid
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class CellType(Enum):
    """Cell types"""
    CODE = "code"
    MARKDOWN = "markdown"
    RAW = "raw"


class CellStatus(Enum):
    """Cell execution status"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class OutputType(Enum):
    """Output types"""
    TEXT = "text"
    HTML = "html"
    MARKDOWN = "markdown"
    IMAGE = "image"
    JAVASCRIPT = "javascript"
    LATEX = "latex"


@dataclass
class Cell:
    """Notebook cell"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cell_type: CellType = CellType.CODE
    content: str = ""
    status: CellStatus = CellStatus.IDLE
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    execution_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_output(self, output_type: OutputType, data: str, metadata: Optional[Dict] = None):
        """Add output to cell"""
        self.outputs.append({
            "output_type": output_type.value,
            "data": data,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })

    def clear_outputs(self):
        """Clear cell outputs"""
        self.outputs = []


class Notebook:
    """Interactive notebook"""

    def __init__(self, name: str = "notebook"):
        self.name = name
        self.cells: List[Cell] = []
        self.metadata: Dict[str, Any] = {
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "version": "1.0"
        }
        self.current_cell_index = 0

    def add_cell(self, cell_type: CellType = CellType.CODE, content: str = "") -> Cell:
        """Add a cell to the notebook"""
        cell = Cell(cell_type=cell_type, content=content)
        self.cells.append(cell)
        return cell

    def insert_cell(self, index: int, cell: Cell):
        """Insert cell at index"""
        self.cells.insert(index, cell)

    def delete_cell(self, index: int):
        """Delete cell at index"""
        if 0 <= index < len(self.cells):
            del self.cells[index]

    def get_cell(self, index: int) -> Optional[Cell]:
        """Get cell at index"""
        if 0 <= index < len(self.cells):
            return self.cells[index]
        return None

    def move_cell_up(self, index: int):
        """Move cell up"""
        if index > 0:
            self.cells[index], self.cells[index - 1] = self.cells[index - 1], self.cells[index]

    def move_cell_down(self, index: int):
        """Move cell down"""
        if index < len(self.cells) - 1:
            self.cells[index], self.cells[index + 1] = self.cells[index + 1], self.cells[index]

    def execute_cell(self, index: int, executor: Optional[Callable] = None) -> Dict[str, Any]:
        """Execute a cell"""
        cell = self.get_cell(index)
        if not cell:
            return {"error": "Cell not found"}

        cell.status = CellStatus.RUNNING
        cell.execution_count += 1

        try:
            if executor and cell.cell_type == CellType.CODE:
                result = executor(cell.content)
                cell.add_output(OutputType.TEXT, str(result))
                cell.status = CellStatus.COMPLETED
                return {"success": True, "result": result}
            elif cell.cell_type == CellType.MARKDOWN:
                cell.status = CellStatus.COMPLETED
                return {"success": True, "rendered": cell.content}
            else:
                cell.status = CellStatus.COMPLETED
                return {"success": True}

        except Exception as e:
            cell.status = CellStatus.ERROR
            cell.add_output(OutputType.TEXT, f"Error: {str(e)}")
            return {"success": False, "error": str(e)}

    def execute_all(self, executor: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """Execute all cells"""
        results = []
        for i, cell in enumerate(self.cells):
            if cell.cell_type == CellType.CODE:
                result = self.execute_cell(i, executor)
                results.append(result)
        return results

    def execute_all_above(self, index: int, executor: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """Execute all cells above index"""
        results = []
        for i in range(index):
            cell = self.cells[i]
            if cell.cell_type == CellType.CODE:
                result = self.execute_cell(i, executor)
                results.append(result)
        return results

    def clear_outputs(self):
        """Clear all cell outputs"""
        for cell in self.cells:
            cell.clear_outputs()

    def to_dict(self) -> Dict[str, Any]:
        """Convert notebook to dictionary"""
        return {
            "name": self.name,
            "metadata": self.metadata,
            "cells": [
                {
                    "id": cell.id,
                    "cell_type": cell.cell_type.value,
                    "content": cell.content,
                    "status": cell.status.value,
                    "outputs": cell.outputs,
                    "execution_count": cell.execution_count,
                    "metadata": cell.metadata
                }
                for cell in self.cells
            ]
        }

    def to_json(self) -> str:
        """Convert notebook to JSON"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notebook':
        """Create notebook from dictionary"""
        notebook = cls(data.get("name", "notebook"))
        notebook.metadata = data.get("metadata", {})

        for cell_data in data.get("cells", []):
            cell = Cell(
                id=cell_data.get("id"),
                cell_type=CellType(cell_data.get("cell_type", CellType.CODE)),
                content=cell_data.get("content", ""),
                status=CellStatus(cell_data.get("status", CellStatus.IDLE)),
                execution_count=cell_data.get("execution_count", 0),
                metadata=cell_data.get("metadata", {})
            )
            cell.outputs = cell_data.get("outputs", [])
            notebook.cells.append(cell)

        return notebook

    @classmethod
    def from_json(cls, json_str: str) -> 'Notebook':
        """Create notebook from JSON"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def save(self, filepath: str):
        """Save notebook to file"""
        with open(filepath, 'w') as f:
            f.write(self.to_json())

    @classmethod
    def load(cls, filepath: str) -> 'Notebook':
        """Load notebook from file"""
        with open(filepath, 'r') as f:
            return cls.from_json(f.read())


class RichOutput:
    """Rich output formatting"""

    @staticmethod
    def format_html(html: str) -> str:
        """Format HTML output"""
        return f"<div class='output'>{html}</div>"

    @staticmethod
    def format_markdown(markdown: str) -> str:
        """Format Markdown output"""
        return f"<div class='markdown'>{markdown}</div>"

    @staticmethod
    def format_latex(latex: str) -> str:
        """Format LaTeX output"""
        return f"<div class='latex'>$$ {latex} $$</div>"

    @staticmethod
    def format_image(image_data: str, image_type: str = "png") -> str:
        """Format image output"""
        return f"<img src='data:image/{image_type};base64,{image_data}' />"

    @staticmethod
    def format_javascript(code: str) -> str:
        """Format JavaScript output"""
        return f"<script>{code}</script>"


class Collaboration:
    """Collaboration features"""

    def __init__(self):
        self.collaborators: Dict[str, Dict[str, Any]] = {}
        self.comments: List[Dict[str, Any]] = []
        self.changes: List[Dict[str, Any]] = []

    def add_collaborator(self, user_id: str, name: str, email: str):
        """Add collaborator"""
        self.collaborators[user_id] = {
            "name": name,
            "email": email,
            "joined": datetime.now().isoformat()
        }

    def remove_collaborator(self, user_id: str):
        """Remove collaborator"""
        if user_id in self.collaborators:
            del self.collaborators[user_id]

    def add_comment(self, cell_id: str, user_id: str, text: str):
        """Add comment to cell"""
        self.comments.append({
            "id": str(uuid.uuid4()),
            "cell_id": cell_id,
            "user_id": user_id,
            "text": text,
            "timestamp": datetime.now().isoformat()
        })

    def get_comments(self, cell_id: str) -> List[Dict[str, Any]]:
        """Get comments for cell"""
        return [c for c in self.comments if c["cell_id"] == cell_id]

    def track_change(self, user_id: str, cell_id: str, change_type: str, details: Any):
        """Track change"""
        self.changes.append({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "cell_id": cell_id,
            "change_type": change_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })


class VersionControl:
    """Version control integration"""

    def __init__(self):
        self.commits: List[Dict[str, Any]] = []
        self.branches: Dict[str, str] = {"main": ""}

    def commit(self, message: str, author: str, notebook: Notebook) -> str:
        """Create commit"""
        commit_id = str(uuid.uuid4())
        self.commits.append({
            "id": commit_id,
            "message": message,
            "author": author,
            "notebook": notebook.to_dict(),
            "timestamp": datetime.now().isoformat()
        })
        self.branches["main"] = commit_id
        return commit_id

    def get_commit(self, commit_id: str) -> Optional[Dict[str, Any]]:
        """Get commit by ID"""
        for commit in self.commits:
            if commit["id"] == commit_id:
                return commit
        return None

    def get_history(self) -> List[Dict[str, Any]]:
        """Get commit history"""
        return self.commits.copy()

    def create_branch(self, name: str, from_commit: Optional[str] = None) -> str:
        """Create branch"""
        commit_id = from_commit or self.branches.get("main", "")
        self.branches[name] = commit_id
        return name

    def checkout(self, branch_name: str) -> Optional[Notebook]:
        """Checkout branch"""
        if branch_name not in self.branches:
            return None

        commit_id = self.branches[branch_name]
        commit = self.get_commit(commit_id)
        if commit:
            return Notebook.from_dict(commit["notebook"])
        return None


def create_notebook(name: str = "notebook") -> Notebook:
    """Create a new notebook"""
    return Notebook(name)


def main():
    """Main entry point for testing"""
    print("Testing Notebook Interface...")

    # Create notebook
    notebook = create_notebook("test_notebook")

    # Add cells
    cell1 = notebook.add_cell(CellType.CODE, "print('Hello, World!')")
    cell2 = notebook.add_cell(CellType.MARKDOWN, "# Title\nThis is a markdown cell.")
    cell3 = notebook.add_cell(CellType.CODE, "x = 10\ny = 20\nprint(x + y)")

    print(f"Notebook created with {len(notebook.cells)} cells")

    # Execute cells
    def executor(code: str) -> str:
        """Simple executor for testing"""
        try:
            exec_globals = {}
            exec(code, exec_globals)
            return "Executed successfully"
        except Exception as e:
            return f"Error: {str(e)}"

    result = notebook.execute_cell(0, executor)
    print(f"Cell 0 execution: {result}")

    result = notebook.execute_all(executor)
    print(f"Executed {len(result)} code cells")

    # Test serialization
    json_str = notebook.to_json()
    print(f"Notebook JSON: {len(json_str)} characters")

    # Test deserialization
    loaded = Notebook.from_json(json_str)
    print(f"Loaded notebook: {loaded.name}")

    # Test saving/loading
    notebook.save("test_notebook.json")
    loaded_notebook = Notebook.load("test_notebook.json")
    print(f"Saved and loaded notebook: {loaded_notebook.name}")

    # Test collaboration
    collab = Collaboration()
    collab.add_collaborator("user1", "Alice", "alice@example.com")
    collab.add_comment(cell1.id, "user1", "This is a comment")
    print(f"Collaborators: {len(collab.collaborators)}")
    print(f"Comments: {len(collab.comments)}")

    # Test version control
    vc = VersionControl()
    commit_id = vc.commit("Initial commit", "user1", notebook)
    print(f"Created commit: {commit_id}")

    history = vc.get_history()
    print(f"Commit history: {len(history)} commits")

    print("\nNotebook Interface initialized successfully")


if __name__ == "__main__":
    main()
