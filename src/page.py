import os

from typing import Optional
from json import dumps, loads, JSONDecodeError
from collections import OrderedDict

from .node import Node


class Page:
    def __init__(self, page_id: int, page_size: int = 4096):
        self.id = page_id
        self.size = page_size
        self.data = {}
        self.is_dirty = False
        self.access_count = 0

    def serialize(self) -> bytes:
        string_data = dumps(self.data)
        encoded_data = string_data.encode()

        return encoded_data

    def deserialize(self, data: bytes) -> dict:
        """Decodes bytes into a dictionary, handling potential errors."""
        try:
            # Strip trailing null bytes used for padding before decoding.
            decoded_data = data.decode().rstrip("\x00")
            return loads(decoded_data) if decoded_data else {}
        except (UnicodeDecodeError, JSONDecodeError):
            # If data is corrupted or not valid JSON, return an empty dict.
            return {}

    def can_fit(self, node_data: dict) -> bool:
        serialized_data = dumps(node_data).encode()

        return len(serialized_data) <= self.size


class PageManager:
    def __init__(
        self,
        data_file: str,
        buffer_pool_size: int = 100,
        page_size: int = 4096,
        next_page_id: int = 1,
    ):
        """
        Manages pages in memory and on disk.

        Args:
            data_file: Path to the database file.
            buffer_pool_size: Maximum number of pages to hold in memory.
            page_size: The size of each page in bytes.
            next_page_id: The next available page ID to allocate.
        """
        self.data_file = data_file
        self.buffer_pool_size = buffer_pool_size
        self.buffer_pool: OrderedDict[int, Page] = OrderedDict()
        self.page_size = page_size
        self.next_page_id = next_page_id

        if not os.path.exists(data_file):
            with open(data_file, "wb"):
                pass

    def get_page(self, page_id: int) -> Optional[Page]:
        """Get page from buffer pool or load from disk."""
        if page_id in self.buffer_pool:
            self.buffer_pool.move_to_end(page_id, last=True)

            return self.buffer_pool[page_id]

        if len(self.buffer_pool) >= self.buffer_pool_size:
            self._evict_page()

        page = self._read_page_from_disk(page_id)

        if page:
            self.buffer_pool[page_id] = page

        return page

    def store_node(self, node: Node) -> int:
        """Stores a B-tree node, allocating a new page ID if necessary."""
        if node.page_id is None:
            node.page_id = self.next_page_id
            self.next_page_id += 1

        self.store_page_data(node.page_id, node.serialize())
        return node.page_id

    def load_node(self, page_id: int) -> Optional[Node]:
        """Load a B-tree node from storage."""
        page_data = self.load_page_data(page_id)
        if page_data:
            return Node.deserialize(page_data)
        return None

    def store_page_data(self, page_id: int, data: dict) -> None:
        """Stores a generic dictionary into a page."""
        page = self.get_page(page_id)
        if page is None:
            page = Page(page_id)
            self.buffer_pool[page_id] = page

        page.data = data
        page.is_dirty = True

    def load_page_data(self, page_id: int) -> Optional[dict]:
        """Loads a generic dictionary from a page."""
        page = self.get_page(page_id)
        return page.data if page else None

    def flush_dirty_pages(self) -> None:
        """Write all dirty pages to disk."""
        for page in self.buffer_pool.values():
            if not page.is_dirty:
                continue

            self._write_page_to_disk(page)
            page.is_dirty = False

    def _write_page_to_disk(self, page: Page) -> None:
        """Write a single page to disk at the correct offset."""
        with open(self.data_file, "r+b") as file:
            offset = page.id * self.page_size
            page_data = page.serialize()

            # Pad the data to ensure it fills the entire page size.
            if len(page_data) < self.page_size:
                page_data = page_data.ljust(self.page_size, b"\x00")

            file.seek(offset)
            file.write(page_data)
            file.flush()
            os.fsync(file.fileno())

    def _read_page_from_disk(self, page_id: int) -> Optional[Page]:
        with open(self.data_file, "rb") as file:
            offset = page_id * self.page_size
            file.seek(offset)
            raw_data = file.read(self.page_size)

            if not raw_data:
                return None

            page = Page(page_id)
            page.data = page.deserialize(raw_data)

            return page

    def _evict_page(self) -> None:
        """
        Evicts a page using a second-chance algorithm variant.

        This loop prioritizes evicting clean pages to avoid disk I/O. Dirty
        pages are written to disk and given a 'second chance' by being moved
        to the end of the queue, making them less likely to be evicted soon.
        """
        for _ in range(len(self.buffer_pool)):
            page_id, page = self.buffer_pool.popitem(last=False)

            if page.is_dirty:
                self._write_page_to_disk(page)
                page.is_dirty = False
                self.buffer_pool[page_id] = page
            else:
                return  # Evict the clean page by not re-inserting it.

        # Fallback if all pages were dirty: evict the first one that was
        # processed, which has now been flushed to disk.
        if self.buffer_pool:
            self.buffer_pool.popitem(last=False)
