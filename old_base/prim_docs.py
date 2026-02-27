"""
Prim Documentation
Provides documentation generation, API docs, user guides,
reference documentation, and doc tools.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class DocType(Enum):
    """Documentation types"""
    API = "api"
    GUIDE = "guide"
    REFERENCE = "reference"
    TUTORIAL = "tutorial"


@dataclass
class Document:
    """Document"""
    name: str
    type: DocType
    content: str


class DocumentationManager:
    """Documentation manager"""

    def __init__(self):
        self.documents: Dict[str, Document] = {}

    def add_document(self, document: Document):
        """Add document"""
        self.documents[document.name] = document

    def get_document(self, name: str) -> Optional[Document]:
        """Get document"""
        return self.documents.get(name)


def main():
    print("Testing Documentation...")
    manager = DocumentationManager()
    doc = Document(name="api", type=DocType.API, content="API documentation")
    manager.add_document(doc)
    print(f"Document: {doc.name}")
    print("Documentation initialized successfully")


if __name__ == "__main__":
    main()
