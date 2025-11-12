# SQL Types

> Custom type decorators for SQLModel/SQLAlchemy with Pydantic validation

## Installation

```bash
pip install sqltypes
```

## Quick Start

```python
from typing import Sequence
from pydantic import BaseModel
from sqlmodel import Field, SQLModel
from sqltypes import ValidatedJSON, SpaceDelimitedList

class User(BaseModel):
    name: str
    age: int

class Article(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tags: Sequence[str] = Field(sa_type=SpaceDelimitedList)
    author: User = Field(sa_type=ValidatedJSON(User))
```

## Available Types

### `ValidatedJSON(T, name?)`
Stores any Pydantic model or complex type as JSON with automatic validation.

```python
config: Config = Field(sa_type=ValidatedJSON(Config))
```

### `SpaceDelimitedList`
Stores sequences as space-delimited strings.

```python
tags: Sequence[str] = Field(sa_type=SpaceDelimitedList)
# Database: "python sql database"
# Python: ["python", "sql", "database"]
```

### `ValidatedStr(LiteralType)`
Validates strings against Pydantic literal types.

```python
from typing import Literal
Status = Literal["pending", "active", "completed"]
status: Status = Field(sa_type=ValidatedStr(Status))
```

## Custom Types

Use `CustomTypeMeta` to create your own types:

```python
from sqltypes import CustomTypeMeta
from sqlalchemy.types import String

CommaSeparatedList = CustomTypeMeta(
    'CommaSeparatedList',
    (), {},
    Impl=String,
    dump=lambda lst: ','.join(lst),
    parse=lambda s: s.split(',')
)
```

Or use `CustomStringMeta` for string-based types:

```python
from sqltypes import CustomStringMeta

class CommaSeparatedList(metaclass=CustomStringMeta,
                          dump=lambda lst: ','.join(lst),
                          parse=lambda s: s.split(',')):
    ...
```

## Links

- **PyPI**: https://pypi.org/project/sqltypes/
- **Repository**: https://github.com/marciclabas/sqltypes
