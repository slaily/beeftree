import math
import bisect


class Node:
    def __init__(
        self, max_keys_per_node: int, is_leaf: bool = False, page_id: int = None
    ):
        if max_keys_per_node < 3:
            raise ValueError("Node capacity must be at least 3.")

        self.page_id = page_id
        self.max_keys_per_node = max_keys_per_node
        self.is_leaf = is_leaf
        self._keys = []
        self._children = []

        # The minimum degree (t) is an internal property derived from the public capacity.
        # It defines the split point and minimum key requirements.
        # Formula: max_keys = 2t - 1  =>  t = (max_keys + 1) / 2
        self._min_degree_from_capacity = math.ceil(self.max_keys_per_node / 2)
        self._min_keys = self._min_degree_from_capacity - 1

    @property
    def keys(self):
        return self._keys

    @property
    def children(self):
        return self._children

    def is_full(self) -> bool:
        return len(self._keys) >= self.max_keys_per_node

    def has_minimum_keys(self) -> bool:
        # The root is allowed to have fewer than the minimum number of keys.
        # This check is typically for non-root nodes during deletion.
        return len(self._keys) >= self._min_keys

    def has_more_than_minimum_keys(self) -> bool:
        return len(self._keys) > self._min_keys

    def add_key(self, key: int):
        """Adds a key to the node while maintaining sorted order."""
        bisect.insort_left(self._keys, key)

    def add_child(self, child_id: int, index: int):
        """Inserts a child ID at a specific index."""
        self._children.insert(index, child_id)

    def split_into_two_nodes(self) -> (int, "Node"):
        """
        Splits this full node into two smaller nodes.
        - This node becomes the left node.
        - A new sibling node is created as the right node.
        - The key that gets moved up to the parent is returned.
        """
        split_point_index = self._min_degree_from_capacity - 1
        promoted_key = self._keys[split_point_index]

        # Create the new right sibling node
        right_sibling = Node(
            max_keys_per_node=self.max_keys_per_node, is_leaf=self.is_leaf
        )
        right_sibling._keys = self._keys[split_point_index + 1 :]
        if not self.is_leaf:
            right_sibling._children = self._children[split_point_index + 1 :]

        # This node becomes the left sibling, so truncate it
        self._keys = self._keys[:split_point_index]
        if not self.is_leaf:
            self._children = self._children[: split_point_index + 1]

        return promoted_key, right_sibling

    def serialize(self) -> dict:
        return {
            "page_id": self.page_id,
            "max_keys_per_node": self.max_keys_per_node,
            "is_leaf": self.is_leaf,
            "keys": self._keys,
            "children": self._children,
        }

    @staticmethod
    def deserialize(data: dict) -> "Node":
        node = Node(
            page_id=data["page_id"],
            max_keys_per_node=data["max_keys_per_node"],
            is_leaf=data["is_leaf"],
        )
        node._keys = data["keys"]
        node._children = data["children"]
        return node
