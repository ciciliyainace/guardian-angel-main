import math
from typing import TypeVar, List, Tuple, Any

T = TypeVar("T")


def paginate_query(cursor_or_items: Any, page: int = 1, page_size: int = 50) -> Tuple[List[Any], int, int, int]:
    """
    Paginate a MongoDB cursor, list, or sequence.
    Returns (items, total, page, pages).
    """
    page = max(1, page)
    page_size = max(1, min(page_size, 500))  # Max 500 items per page
    offset = (page - 1) * page_size

    # Handle MongoDB Cursor
    if hasattr(cursor_or_items, "skip") and hasattr(cursor_or_items, "limit"):
        try:
            total = cursor_or_items.collection.count_documents(getattr(cursor_or_items, "_filter", {}))
        except Exception:
            total = len(list(cursor_or_items.clone()))
        items = list(cursor_or_items.skip(offset).limit(page_size))
    elif isinstance(cursor_or_items, (list, tuple)):
        total = len(cursor_or_items)
        items = cursor_or_items[offset:offset + page_size]
    else:
        items = list(cursor_or_items)
        total = len(items)
        items = items[offset:offset + page_size]

    pages = math.ceil(total / page_size) if total > 0 else 1
    return items, total, page, pages
