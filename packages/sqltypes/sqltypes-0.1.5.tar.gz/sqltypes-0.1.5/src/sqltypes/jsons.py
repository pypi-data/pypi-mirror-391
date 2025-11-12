from typing import TypeVar
from sqlalchemy.types import TypeDecorator, JSON
from pydantic import TypeAdapter
from .meta import CustomTypeMeta

T = TypeVar('T')

class ValidatedJSON(type):
  def __new__(cls, T: type[T], name: str | None = None) -> type[TypeDecorator[T]]:
    Type = TypeAdapter(T)
    def dump(x: T):
      return Type.dump_python(x, exclude_none=True, mode='json')
    def parse(x: dict) -> T:
      return Type.validate_python(x)
    return CustomTypeMeta(f'DB{name or T.__name__}', (), {}, JSON, dump=dump, parse=parse)