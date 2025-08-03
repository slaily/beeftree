# In a new file: src/btree.py
import bisect
from typing import List, Tuple

from .node import Node
from .page import Page, PageManager


class BTree:
    def __init__(self, file_path: str):
        """
        Initializes the B-Tree, acting as the main database interface.
        It discovers metadata from the header page (Page 0) or creates it
        if the database file is new.
        """
        # First, we check the header without creating a full PageManager
        # to see if we need to initialize the file.
        try:
            with open(file_path, "rb") as f:
                header_data_raw = f.read(4096)
            header = Page(0).deserialize(header_data_raw)
        except (FileNotFoundError, IndexError):
            header = {}

        # Now, initialize the PageManager with the correct next_page_id
        next_page_id = header.get("next_page_id", 1)
        self.pm = PageManager(file_path, next_page_id=next_page_id)

        if not header:
            # The file is new or empty, so create the header.
            self.root_page_id = None
            # The PageManager was already initialized with next_page_id = 1.
            # We immediately store the initial header to reserve Page 0.
            self.pm.store_page_data(
                0,
                {
                    "root_page_id": self.root_page_id,
                    "next_page_id": self.pm.next_page_id,
                },
            )
        else:
            # The file exists, load state from the header.
            self.root_page_id = header.get("root_page_id")

    def search(self, key: int) -> Tuple[bool, List[Tuple[int, int]]]:
        """
        Search for a key in the B-Tree.

        Args:
            key: The key to search for.

        Returns:
            A tuple containing:
            - bool: True if the key is found, False otherwise.
            - List[Tuple[int, int]]: The traversal path from root to leaf.
              Each tuple in the list is (page_id, key_index).
        """
        if self.root_page_id is None:
            return False, []

        path = []
        current_page_id = self.root_page_id

        while current_page_id is not None:
            node = self.pm.load_node(current_page_id)

            if node is None:
                break

            key_index = bisect.bisect_left(node.keys, key)
            path.append((current_page_id, key_index))

            if key_index < len(node.keys) and node.keys[key_index] == key:
                return True, path

            if node.is_leaf:
                break

            current_page_id = node.children[key_index]

        return False, path

    def close(self):
        """Saves metadata to the header and flushes all pages to disk."""
        # Get the latest next_page_id from the manager it's been using.
        header_data = {
            "root_page_id": self.root_page_id,
            "next_page_id": self.pm.next_page_id,
        }
        self.pm.store_page_data(0, header_data)

        self.pm.flush_dirty_pages()
