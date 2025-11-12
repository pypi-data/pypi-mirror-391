from typing import TypeVar, Callable
from pydantic import TypeAdapter
from sqlalchemy.types import TypeDecorator, String
from .meta import CustomTypeMeta

T = TypeVar('T')

class CustomStringMeta(type):
  def __new__(cls, name: str, bases, dct, dump: Callable[[T], str], parse: Callable[[str], T]) -> type[TypeDecorator[T]]:
    return CustomTypeMeta(name, bases, dct, String, dump=dump, parse=parse)
  
class SpaceDelimitedList(metaclass=CustomStringMeta, dump=' '.join, parse=str.split):
  ...

class ValidatedStr(type):
  def __new__(cls, LiteralType) -> type[TypeDecorator[str]]:
    Type = TypeAdapter(LiteralType)
    def dump(x) -> str:
      Type.validate_python(x)
      return x
    def parse(x: str):
      Type.validate_python(x)
      return x # type: ignore
    return CustomTypeMeta(LiteralType.__name__, (), {}, String, dump=dump, parse=parse)