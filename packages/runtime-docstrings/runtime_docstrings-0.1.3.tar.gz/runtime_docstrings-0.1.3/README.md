
# runtime-docstrings

Runtime access to Python class attribute docstrings (PEP 224)

## Installation

```bash
pip install runtime-docstrings
```

## Usage

### Class

```python
from runtime_docstrings import docstrings, get_docstrings

@docstrings
class Person:
    """A person with various attributes."""
    
    name: str
    """The person's full name."""

    email: str
    """Contact email address."""

    age: int = 0
    """The person's age in years."""

# Access docstrings map directly on class (IDE style)
docs = get_docstrings(Person)
print(docs["name"])    # "The person's full name."
print(docs["age"])     # "The person's age in years."
print(docs["email"])   # "Contact email address."

# Access via PEP 224 style attributes (uses Python MRO lookup)
print(Person.__doc_name__)   # "The person's full name."
print(Person.__doc_age__)    # "The person's age in years."
print(Person.__doc_email__)  # "Contact email address."
```

### Enum

```python
from enum import Enum
from runtime_docstrings import docstrings

@docstrings
class Status(Enum):
    """Status enumeration for task tracking."""
    
    PENDING = "pending"
    """Task is waiting to be processed."""
    
    RUNNING = "running"
    """Task is currently being executed."""
    
    COMPLETED = "completed"
    """Task has finished successfully."""
    
    FAILED = "failed"
    """Task encountered an error."""

# Supports all the standard class access patterns

# Access via enum member __doc__ attribute
print(Status.PENDING.__doc__)    # "Task is waiting to be processed."
print(Status.COMPLETED.__doc__)  # "Task has finished successfully."

# Iterate through all members with their documentation
for member in Status:
    if member.__doc__:
        print(f"{member.name}: {member.__doc__}")
```

### Dataclass

```python
from dataclasses import dataclass, fields
from runtime_docstrings import docstrings, get_docstrings

@docstrings
@dataclass
class Product:
    """A product in an e-commerce system."""
    
    name: str
    """Product name."""
    
    price: float
    """Price in USD."""

    category: str = ""
    """Product category."""
    
    description: str = ""
    """Detailed product description."""

# Supports all the standard class access patterns

# Access via dataclass field metadata
for field in fields(Product):
    if field.metadata.get("__doc__"):
        print(f"{field.name}: {field.metadata['__doc__']}")
```
