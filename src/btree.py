import bisect
from typing import List, Tuple

from .node import Node
from .page import DiskPage, StorageManager


class BTree:
    def __init__(self, file_path: str, max_keys_per_node: int = 5):
        """
        Initializes the B-Tree, using a user-friendly max_keys_per_node.
        """
        try:
            with open(file_path, "rb") as f:
                header_data_raw = f.read(4096)
            # Temporarily create a page to deserialize the header
            header_page = DiskPage(0)
            header_page.from_bytes(header_data_raw)
            header = header_page.content
        except (FileNotFoundError, IndexError):
            header = {}

        next_page_id = header.get("next_page_id", 1)
        self.storage = StorageManager(file_path, next_page_id=next_page_id)

        if not header:
            self.max_keys_per_node = max_keys_per_node
            self.root_page_id = None
            self.storage.store_page_content(
                0,
                {
                    "max_keys_per_node": self.max_keys_per_node,
                    "root_page_id": self.root_page_id,
                    "next_page_id": self.storage.next_page_id,
                },
            )
        else:
            self.max_keys_per_node = header.get("max_keys_per_node", max_keys_per_node)
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
            node = self.storage.load_node(current_page_id)

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

    def insert(self, key: int):
        """Inserts a key into the tree, handling splits as needed."""
        if self.root_page_id is None:
            # The tree is empty, create the first node.
            root_node = Node(max_keys_per_node=self.max_keys_per_node, is_leaf=True)
            root_node.add_key(key)
            self.root_page_id = self.storage.store_node(root_node)
            return

        root_node = self.storage.load_node(self.root_page_id)

        if root_node.is_full():
            # The root is full, so the tree grows in height.
            old_root_id = self.root_page_id
            new_root = Node(max_keys_per_node=self.max_keys_per_node, is_leaf=False)
            new_root.add_child(old_root_id, 0)
            self.root_page_id = self.storage.store_node(new_root)
            self._split_full_child_of_parent(
                parent_page_id=self.root_page_id, child_to_split_index=0
            )
            self._insert_into_node_with_space(self.root_page_id, key)
        else:
            self._insert_into_node_with_space(self.root_page_id, key)

    def _split_full_child_of_parent(
        self, parent_page_id: int, child_to_split_index: int
    ):
        """
        Takes a parent node and the index of its full child, splits the child,
        and updates the parent with the promoted key and new sibling.
        """
        parent_node = self.storage.load_node(parent_page_id)
        child_id = parent_node.children[child_to_split_index]
        child_node = self.storage.load_node(child_id)

        promoted_key, right_sibling_node = child_node.split_into_two_nodes()
        right_sibling_page_id = self.storage.store_node(right_sibling_node)

        parent_node.add_key(promoted_key)
        parent_node.add_child(right_sibling_page_id, child_to_split_index + 1)

        self.storage.store_node(parent_node)
        self.storage.store_node(child_node)
        self.storage.store_node(right_sibling_node)

    def _insert_into_node_with_space(self, page_id: int, key: int):
        """
        Recursively descends the tree to find the correct leaf node for insertion.
        It ensures that any node it descends into has space by splitting it if it's full.
        """
        node = self.storage.load_node(page_id)

        if node.is_leaf:
            node.add_key(key)
            self.storage.store_node(node)
        else:
            child_index_to_descend = bisect.bisect_right(node.keys, key)
            child_id = node.children[child_index_to_descend]
            child_node = self.storage.load_node(child_id)

            if child_node.is_full():
                self._split_full_child_of_parent(page_id, child_index_to_descend)
                # After splitting, the parent's keys have changed.
                # We must re-check which child to descend into.
                if key > node.keys[child_index_to_descend]:
                    child_id = node.children[child_index_to_descend + 1]

            self._insert_into_node_with_space(child_id, key)

    def close(self):
        """Saves metadata to the header and flushes all pages to disk."""
        # Get the latest next_page_id from the manager it's been using.
        header_data = {
            "max_keys_per_node": self.max_keys_per_node,
            "root_page_id": self.root_page_id,
            "next_page_id": self.storage.next_page_id,
        }
        self.storage.store_page_content(0, header_data)

        self.storage.save_all_unsaved_pages_to_disk()
