import importlib
import typing
from functools import lru_cache

__lazy_attrs__ = {
    "BlockType": (".structs", "BlockType"),
    "ContentBlock": (".structs", "ContentBlock"),
    "PDFDocument": (".pdf_doc", "PDFDocument"),
    "DocStore": (".doc_store", "DocStore"),
    "DocClient": (".doc_client", "DocClient"),
    # interface
    "MetricInput": (".interface", "MetricInput"),
    "ValueInput": (".interface", "ValueInput"),
    "TaskInput": (".interface", "TaskInput"),
    "DocInput": (".interface", "DocInput"),
    "PageInput": (".interface", "PageInput"),
    "DocPageInput": (".interface", "DocPageInput"),
    "BlockInput": (".interface", "BlockInput"),
    "LayoutInput": (".interface", "LayoutInput"),
    "ContentInput": (".interface", "ContentInput"),
    "ContentBlockInput": (".interface", "ContentBlockInput"),
    "Element": (".interface", "Element"),
    "DocElement": (".interface", "DocElement"),
    "Doc": (".interface", "Doc"),
    "Page": (".interface", "Page"),
    "Layout": (".interface", "Layout"),
    "Block": (".interface", "Block"),
    "Content": (".interface", "Content"),
    "Value": (".interface", "Value"),
    "Task": (".interface", "Task"),
    "ElementNotFoundError": (".interface", "ElementNotFoundError"),
    "ElementExistsError": (".interface", "ElementExistsError"),
    "DocExistsError": (".interface", "DocExistsError"),
    "TaskMismatchError": (".interface", "TaskMismatchError"),
}

if typing.TYPE_CHECKING:
    from .doc_client import DocClient
    from .doc_store import DocStore
    from .interface import (
        Block,
        BlockInput,
        Content,
        ContentBlockInput,
        ContentInput,
        Doc,
        DocElement,
        DocExistsError,
        DocInput,
        DocPageInput,
        Element,
        ElementExistsError,
        ElementNotFoundError,
        Layout,
        LayoutInput,
        MetricInput,
        Page,
        PageInput,
        Task,
        TaskInput,
        TaskMismatchError,
        Value,
        ValueInput,
    )
    from .pdf_doc import PDFDocument
    from .structs import BlockType, ContentBlock

    store: DocStore


@lru_cache(maxsize=1)
def _store():
    from .doc_store import DocStore

    return DocStore()


def __getattr__(name: str):
    if name == "store":
        return _store()
    if name in __lazy_attrs__:
        module_name, attr_name = __lazy_attrs__[name]
        module = importlib.import_module(module_name, __name__)
        return getattr(module, attr_name)
    raise AttributeError(f"Module '{__name__}' has no attribute '{name}'")


__all__ = [
    "BlockType",
    "ContentBlock",
    "PDFDocument",
    "store",
    "DocStore",
    "DocClient",
    "MetricInput",
    "ValueInput",
    "TaskInput",
    "DocInput",
    "PageInput",
    "DocPageInput",
    "BlockInput",
    "LayoutInput",
    "ContentInput",
    "ContentBlockInput",
    "Element",
    "DocElement",
    "Doc",
    "Page",
    "Layout",
    "Block",
    "Content",
    "Value",
    "Task",
    "ElementNotFoundError",
    "ElementExistsError",
    "DocExistsError",
    "TaskMismatchError",
]
