import bisect
from typing import List, Tuple

from .node import Node
from .storage import DiskPage, StorageManager


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

    def delete(self, key: int):
        """Public method to delete a key."""
        if self.root_page_id is None:
            return

        self._delete_recursively(self.root_page_id, key)

        # After deletion, the root might become an empty internal node with one child.
        # If so, the tree height shrinks.
        root_node = self.storage.load_node(self.root_page_id)
        if not root_node.is_leaf and len(root_node.keys) == 0:
            self.root_page_id = root_node.children[0]

    def _delete_recursively(self, current_page_id: int, key: int):
        """
        Recursively traverses the tree to find and delete a key.
        This implementation uses the proactive approach, ensuring that any node
        we descend into has more than the minimum number of keys.
        """
        current_node = self.storage.load_node(current_page_id)

        # Find the index of the key or the child to descend into.
        try:
            key_index = current_node.keys.index(key)
            key_found = True
        except ValueError:
            key_index = bisect.bisect_right(current_node.keys, key)
            key_found = False

        if key_found:
            if current_node.is_leaf:
                # Case 1: Key is in a leaf node. Simply remove it.
                current_node.keys.pop(key_index)
                self.storage.store_node(current_node)
            else:
                # Case 2: Key is in an internal node.
                # We find the successor, replace the key, and then recursively
                # delete the successor from the child subtree.
                child_page_id = current_node.children[key_index + 1]
                child_node = self.storage.load_node(child_page_id)

                if child_node.is_at_minimum_capacity():
                    # If the child where the successor lives is minimal, we must
                    # resolve it first before descending.
                    self._resolve_minimal_child(current_node, key_index + 1)

                # After resolution, find the successor again as the tree may have changed.
                successor = self._find_smallest_key_in_subtree(
                    current_node.children[key_index + 1]
                )
                current_node.keys[key_index] = successor
                self.storage.store_node(current_node)
                self._delete_recursively(
                    current_node.children[key_index + 1], successor
                )
        else:
            # Case 3: Key is not in the current node. Descend to a child.
            child_to_descend_id = current_node.children[key_index]
            child_node = self.storage.load_node(child_to_descend_id)

            if child_node.is_at_minimum_capacity():
                # Proactive step: Resolve the minimal child before descending.
                self._resolve_minimal_child(current_node, key_index)
                # After a merge, the key might have moved into the current node.
                # We need to re-run the deletion logic from the current node.
                self._delete_recursively(current_page_id, key)
            else:
                self._delete_recursively(child_to_descend_id, key)

    def _resolve_minimal_child(self, parent_node, child_index):
        """
        Ensures a child at a given index has more than the minimum number of keys,
        performing a borrow or merge operation if necessary.
        """
        child_node = self.storage.load_node(parent_node.children[child_index])

        # Try to borrow from the left sibling first.
        if child_index > 0:
            left_sibling_id = parent_node.children[child_index - 1]
            left_sibling_node = self.storage.load_node(left_sibling_id)
            if left_sibling_node.has_more_than_minimum_keys():
                self._borrow_from_left_sibling(
                    parent_node, child_node, left_sibling_node, child_index
                )
                return

        # If not, try to borrow from the right sibling.
        if child_index < len(parent_node.children) - 1:
            right_sibling_id = parent_node.children[child_index + 1]
            right_sibling_node = self.storage.load_node(right_sibling_id)
            if right_sibling_node.has_more_than_minimum_keys():
                self._borrow_from_right_sibling(
                    parent_node, child_node, right_sibling_node, child_index
                )
                return

        # If borrowing is not possible, merge.
        if child_index > 0:
            # Merge with the left sibling.
            left_sibling_id = parent_node.children[child_index - 1]
            left_sibling_node = self.storage.load_node(left_sibling_id)
            self._merge_with_left_sibling(
                parent_node, child_node, left_sibling_node, child_index
            )
        else:
            # Merge with the right sibling.
            right_sibling_id = parent_node.children[child_index + 1]
            right_sibling_node = self.storage.load_node(right_sibling_id)
            self._merge_with_right_sibling(
                parent_node, child_node, right_sibling_node, child_index
            )

    def _borrow_from_left_sibling(
        self, parent_node, current_node, left_sibling_node, child_index
    ):
        """Rotates a key from a rich left sibling through the parent to the current node."""
        # The separator key from the parent comes down to the current node.
        separator_key_index = child_index - 1
        separator_key = parent_node.keys.pop(separator_key_index)
        current_node.keys.insert(0, separator_key)

        # The richest key from the sibling goes up to the parent.
        borrowed_key = left_sibling_node.keys.pop()
        parent_node.keys.insert(separator_key_index, borrowed_key)

        # If the nodes are internal, the sibling's child pointer also moves.
        if not left_sibling_node.is_leaf:
            borrowed_child_id = left_sibling_node.children.pop()
            current_node.children.insert(0, borrowed_child_id)

        # Save all modified nodes.
        self.storage.store_node(parent_node)
        self.storage.store_node(current_node)
        self.storage.store_node(left_sibling_node)

    def _borrow_from_right_sibling(
        self, parent_node, current_node, right_sibling_node, child_index
    ):
        """Rotates a key from a rich right sibling through the parent to the current node."""
        # The separator key from the parent comes down to the current node.
        separator_key_index = child_index
        separator_key = parent_node.keys.pop(separator_key_index)
        current_node.keys.append(separator_key)

        # The richest key from the sibling goes up to the parent.
        borrowed_key = right_sibling_node.keys.pop(0)
        parent_node.keys.insert(separator_key_index, borrowed_key)

        # If the nodes are internal, the sibling's child pointer also moves.
        if not right_sibling_node.is_leaf:
            borrowed_child_id = right_sibling_node.children.pop(0)
            current_node.children.append(borrowed_child_id)

        # Save all modified nodes.
        self.storage.store_node(parent_node)
        self.storage.store_node(current_node)
        self.storage.store_node(right_sibling_node)

    def _merge_with_left_sibling(
        self, parent_node, current_node, left_sibling_node, child_index
    ):
        """Merges the current node with its left sibling."""
        # The separator key from the parent comes down into the left sibling.
        separator_key_index = child_index - 1
        separator_key = parent_node.keys.pop(separator_key_index)
        left_sibling_node.keys.append(separator_key)

        # All keys and children from the current node are moved to the left sibling.
        left_sibling_node.keys.extend(current_node.keys)
        if not current_node.is_leaf:
            left_sibling_node.children.extend(current_node.children)

        # The parent loses the separator key and the pointer to the current node.
        parent_node.children.pop(child_index)

        # Save the modified nodes. The current_node is now empty and abandoned.
        self.storage.store_node(parent_node)
        self.storage.store_node(left_sibling_node)

    def _merge_with_right_sibling(
        self, parent_node, current_node, right_sibling_node, child_index
    ):
        """Merges the current node with its right sibling."""
        # The separator key from the parent comes down into the current node.
        separator_key_index = child_index
        separator_key = parent_node.keys.pop(separator_key_index)
        current_node.keys.append(separator_key)

        # All keys and children from the right sibling are moved to the current node.
        current_node.keys.extend(right_sibling_node.keys)
        if not current_node.is_leaf:
            current_node.children.extend(right_sibling_node.children)

        # The parent loses the separator key and the pointer to the right sibling.
        parent_node.children.pop(child_index + 1)

        # Save the modified nodes. The right_sibling_node is now empty and abandoned.
        self.storage.store_node(parent_node)
        self.storage.store_node(current_node)

    def _find_smallest_key_in_subtree(self, page_id: int) -> int:
        """Finds the smallest key in the subtree rooted at the given page_id."""
        current_node = self.storage.load_node(page_id)
        while not current_node.is_leaf:
            child_id = current_node.children[0]
            current_node = self.storage.load_node(child_id)
        return current_node.keys[0]

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
