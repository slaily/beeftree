class Node:
    def __init__(self, degree, is_leaf=False, page_id=None):
        self.page_id = page_id
        self.degree = degree
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []
        self._min_keys = degree - 1
        self._max_keys = 2 * degree - 1

    def is_full(self) -> bool:
        return len(self.keys) == self._max_keys

    def has_minimum_keys(self) -> bool:
        if self.is_leaf:
            return True

        return len(self.keys) >= self._min_keys

    def has_more_than_minimum_keys(self) -> bool:
        return len(self.keys) > self._min_keys

    def serialize(self) -> dict:
        return {
            "page_id": self.page_id,
            "degree": self.degree,
            "is_leaf": self.is_leaf,
            "keys": self.keys,
            "children": self.children,
        }

    @staticmethod
    def deserialize(data: dict) -> "Node":
        node = Node(
            page_id=data["page_id"], degree=data["degree"], is_leaf=data["is_leaf"]
        )
        node.keys = data["keys"]
        node.children = data["children"]

        return node
