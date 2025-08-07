import os

from typing import Optional
from json import dumps, loads, JSONDecodeError
from collections import OrderedDict

from .node import Node


class DiskPage:
    def __init__(self, page_number: int, byte_size: int = 4096):
        self.page_number = page_number
        self.byte_size = byte_size
        self.content = {}
        self.has_unsaved_changes = False

    def to_bytes(self) -> bytes:
        """Converts the page content to a byte string for disk storage."""
        string_content = dumps(self.content)
        return string_content.encode()

    def from_bytes(self, byte_data: bytes):
        """Loads page content from a byte string read from disk."""
        try:
            # Strip trailing null bytes used for padding before decoding.
            decoded_data = byte_data.decode().rstrip("\x00")
            self.content = loads(decoded_data) if decoded_data else {}
        except (UnicodeDecodeError, JSONDecodeError):
            # If data is corrupted or not valid JSON, treat it as empty.
            self.content = {}

    def can_fit(self, data_to_write: dict) -> bool:
        """Checks if the serialized data can fit within the page's byte size."""
        return len(dumps(data_to_write).encode()) <= self.byte_size


class StorageManager:
    def __init__(
        self,
        database_file_path: str,
        max_cached_pages: int = 100,
        page_size: int = 4096,
        next_page_id: int = 1,
    ):
        """
        Manages reading and writing pages to a database file, with an in-memory cache.
        """
        self.database_file_path = database_file_path
        self.max_cached_pages = max_cached_pages
        self.page_cache: OrderedDict[int, DiskPage] = OrderedDict()
        self.page_size = page_size
        self.next_page_id = next_page_id

        if not os.path.exists(database_file_path):
            with open(database_file_path, "wb"):
                pass

    def fetch_page_from_cache_or_disk(self, page_number: int) -> Optional[DiskPage]:
        """
        Retrieves a page, first checking the cache and then loading from disk if necessary.
        """
        if page_number in self.page_cache:
            self.page_cache.move_to_end(page_number, last=True)
            return self.page_cache[page_number]

        if len(self.page_cache) >= self.max_cached_pages:
            self._evict_page_from_cache()

        page = self._read_page_from_disk(page_number)
        if page:
            self.page_cache[page_number] = page
        return page

    def store_node(self, node: Node) -> int:
        """Stores a B-tree node, allocating a new page number if necessary."""
        if node.page_id is None:
            node.page_id = self.next_page_id
            self.next_page_id += 1

        self.store_page_content(node.page_id, node.serialize())
        return node.page_id

    def load_node(self, page_number: int) -> Optional[Node]:
        """Loads a B-tree node from a specific page."""
        page_content = self.load_page_content(page_number)
        if page_content:
            return Node.deserialize(page_content)
        return None

    def store_page_content(self, page_number: int, content: dict) -> None:
        """Writes content to a specific page."""
        page = self.fetch_page_from_cache_or_disk(page_number)
        if page is None:
            page = DiskPage(page_number)
            self.page_cache[page_number] = page

        page.content = content
        page.has_unsaved_changes = True

    def load_page_content(self, page_number: int) -> Optional[dict]:
        """Reads content from a specific page."""
        page = self.fetch_page_from_cache_or_disk(page_number)
        return page.content if page else None

    def save_all_unsaved_pages_to_disk(self) -> None:
        """Writes all pages with unsaved changes from the cache to disk."""
        for page in self.page_cache.values():
            if page.has_unsaved_changes:
                self._write_page_to_disk(page)
                page.has_unsaved_changes = False

    def _write_page_to_disk(self, page: DiskPage) -> None:
        """Writes a single page's content to the correct location in the database file."""
        with open(self.database_file_path, "r+b") as file:
            offset = page.page_number * self.page_size
            page_bytes = page.to_bytes()

            # Pad the data to ensure it fills the entire page size.
            if len(page_bytes) < self.page_size:
                page_bytes = page_bytes.ljust(self.page_size, b"\x00")

            file.seek(offset)
            file.write(page_bytes)
            file.flush()
            os.fsync(file.fileno())

    def _read_page_from_disk(self, page_number: int) -> Optional[DiskPage]:
        """Reads a single page from the database file."""
        with open(self.database_file_path, "rb") as file:
            offset = page_number * self.page_size
            file.seek(offset)
            raw_data = file.read(self.page_size)

            if not raw_data:
                return None

            page = DiskPage(page_number)
            page.from_bytes(raw_data)
            return page

    def _evict_page_from_cache(self) -> None:
        """
        Removes a page from the cache to make space, using a second-chance algorithm.
        Clean pages are evicted first. Dirty pages are written to disk and kept.
        """
        for _ in range(len(self.page_cache)):
            page_number, page = self.page_cache.popitem(last=False)

            if page.has_unsaved_changes:
                self._write_page_to_disk(page)
                page.has_unsaved_changes = False
                self.page_cache[page_number] = page  # Give it a second chance
            else:
                return  # Evict the clean page by not re-inserting it.

        # Fallback if all pages were dirty: evict the first one processed.
        if self.page_cache:
            self.page_cache.popitem(last=False)
