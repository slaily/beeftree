# Building a Database Storage Engine: A Learning Guide

## Learning Objectives
- [X] Understand B-tree structure, properties, and mathematical foundations
- [ ] Implement core B-tree operations: search, insertion, deletion, splitting, merging
- [X] Understand how B-trees are used in real database systems (InnoDB, PostgreSQL)
- [ ] Analyze performance characteristics and optimization techniques
- [ ] Build a complete, production-quality B-tree implementation in Python
- [X] Understand storage management and page-based organization
- [ ] Implement a simple database storage engine using B-trees

## Prerequisites ✅ *Completed: 2025-07-10*
- Solid understanding of Python programming
- Basic knowledge of data structures (arrays, linked lists, binary trees)
- Familiarity with database concepts (tables, indexes, queries)
- Understanding of file I/O operations
- Basic knowledge of algorithms and Big O notation

## Learning Path

### Section 1: B-Tree Fundamentals *Completed: 2025-07-16*
- [x] Understanding tree vs B-tree differences
- [x] B-tree properties and mathematical constraints
- [x] Storage efficiency and disk I/O optimization

**My answers:**
- A tree is a data structure which represent data in hierarchical way. It's organized into nodes. A node has exactly one parent (except the root) and can have zero or more keys. 
- A B-tree is a self-balancing, multi-way search tree that keeps data sorted and allows searches, insertions, and deletions in logarithmic time. 
Its structure ensures that all leaf nodes are at the same depth, which keeps the tree balanced and operations efficient. 
Internal nodes contain keys and pointers to their child nodes, guiding searches quickly to the correct leaf. 
B-trees are widely used in databases and filesystems to efficiently manage and index large volumes of data.
- B-tree properties and mathematical constraints. Each node in a B-tree (except the root) must have at least ⌈m/2⌉ - 1 keys and at most m - 1 keys, where m is the order of the tree (the maximum number of children per node). For example, if the maximum number of children is 10,000, then each node can have at most 9,999 keys and must have at least 4,999 keys. These boundaries keep the B-tree balanced and efficient. When a node exceeds the maximum number of keys, it splits: the middle key is promoted to the parent, and the node is divided into two—left (keys < middle) and right (keys > middle). The split boundary is the position of the middle key in the sorted list. The root node is allowed to have fewer keys if the tree is small. When you delete a key from a B-tree, you must ensure that all nodes (except possibly the root) still have at least the minimum number of keys (⌈m/2⌉ - 1).
If a node falls below this minimum after deletion, you must rebalance the tree.
- Storage efficiency and disk I/O optimization. If a record or database page is accessed more often, it should be kept in memory, otherwise it should remain on disk and be read when needed (Five-Minute Rule principle). B-trees achieve storage efficiency by creating shallow trees with many keys per node rather than deep trees with few keys per node, thus reducing the number of disk I/O operations needed to find data. For example, a binary search tree might require 20 disk I/Os to find a record among 1 million entries, while a B-tree with large nodes might only need 2-3 disk I/Os for the same search.

#### Practical Exercise 1.1: B-Tree Node Structure ✅ *Completed: 2025-07-17*

**Section Connection**: This exercise directly applies the following subtopics from this section:
- Understanding tree vs B-tree differences: Implementing multi-way node structure vs binary tree nodes
- B-tree properties and mathematical constraints: Enforcing minimum/maximum key constraints per node
- Storage efficiency: Designing nodes to hold multiple keys for reduced I/O operations
- Key terminology: degree, order, keys, children, leaf nodes, internal nodes

**Real-World Context**: Database systems like PostgreSQL and MySQL use B-tree nodes as the fundamental building blocks for their index structures, storing thousands of keys per node to minimize disk reads.

**Micro-Objective**: Implement a B-tree node class that enforces capacity constraints and distinguishes between leaf and internal nodes.

**Mental Model**: Think of a B-tree node as a sorted filing cabinet drawer - it can hold multiple sorted folders (keys) and has labeled dividers pointing to other drawers (child pointers). Internal nodes are like directory drawers that point to other drawers, while leaf nodes are like the actual filing drawers containing documents.

**Implementation Constraints**: 
- ✅ What TO implement: Node structure, key storage, child pointer management, capacity validation
- ❌ What NOT to implement: Search operations, insertion/deletion logic, tree traversal algorithms  
- 🎯 Why these boundaries matter: Focus on understanding the fundamental node structure before tackling complex operations

**Scaffolded Code Template**:
```python
class BTreeNode:
    def __init__(self, degree: int, is_leaf: bool = False):
        """
        Initialize a B-tree node.
        
        Args:
            degree: The minimum degree of the B-tree (t in textbooks)
            is_leaf: True if this is a leaf node, False for internal nodes
        """
        self.degree = degree
        self.is_leaf = is_leaf
        self.keys = []  # Sorted list of keys
        self.children = []  # List of child node references (internal nodes only)
        
    def is_full(self) -> bool:
        """Check if node has reached maximum capacity."""
        # TODO: Implement capacity check
        # Hint: Maximum keys = 2 * degree - 1
        pass
        
    def is_minimal(self) -> bool:
        """Check if node has minimum required keys (except root)."""
        # TODO: Implement minimum capacity check  
        # Hint: Minimum keys = degree - 1
        pass
        
    def has_enough_keys(self) -> bool:
        """Check if node has more than minimum keys (safe for borrowing)."""
        # TODO: Implement check for borrowing eligibility
        # Hint: Can spare a key if keys > degree - 1
        pass
        
```

**Step-by-Step Guide**:
1. **Step 1**: Implement `is_full()` method by checking if current key count equals maximum capacity (2 * degree - 1)
2. **Step 2**: Implement `is_minimal()` method by checking if current key count equals minimum required (degree - 1)
3. **Step 3**: Implement `has_enough_keys()` method by checking if node has more than minimum keys (can spare one)

**Single Success Test**:
```python
def test_btree_node_structure():
    # Test with degree = 3 (max 5 keys, min 2 keys)
    node = Node(degree=3, is_leaf=True)
    
    # Test initial state
    assert not node.is_full()
    assert node.is_minimal()  # Empty node considered minimal
    assert not node.has_enough_keys()
    
    # Test with some keys
    node.keys = [10, 20, 30]
    assert not node.is_full()
    assert not node.is_minimal() 
    assert node.has_enough_keys()
    
    # Test full capacity
    node.keys = [10, 20, 30, 40, 50]  # 2*3-1 = 5 keys
    assert node.is_full()
    assert not node.is_minimal()
    assert node.has_enough_keys()
    
    print("✅ All tests passed! Node structure working correctly.")

# Run the test
test_btree_node_structure()
```

**Common Mistakes to Avoid**:
- Mistake 1: Confusing degree with maximum keys - degree is the minimum degree (t), max keys is 2*t-1
- Mistake 2: Not handling empty nodes correctly in validation - empty nodes are valid but considered minimal
- Mistake 3: Allowing unsorted keys - B-tree properties require keys to be maintained in sorted order

**Debugging Guide**:
- "If `is_full()` returns wrong result, check your maximum capacity formula: should be 2 * degree - 1"
- "If `is_minimal()` fails, remember minimum keys = degree - 1, and empty nodes are considered minimal"
- "If `validate_structure()` fails, print the keys list and verify it's sorted using `keys == sorted(keys)`"

#### Self-Check Quiz 1.1 ✅ *Completed: 2025-07-17*
1. Why do B-trees have a minimum degree constraint (⌈m/2⌉-1 keys minimum)?
2. How does a B-tree's height compare to a binary search tree for the same data?
3. What happens to search performance when nodes are larger vs smaller?

**My Answers:**
1. Minimum degree constraint is important. It keeps a node fill his space with keys. Imagine a nodes with only 1 key which will involve more disk operations to find a key.

2. A b-tree is with smaller height approximately logn according to binary tree

3. Larger nodes reduce disk I/O (fewer tree levels) but increase in-memory search time within nodes. The optimal size balances these factors - typically matching disk page size (4KB-16KB) for cache efficiency. Too large nodes waste memory bandwidth; too small nodes waste disk bandwidth.

---

### Section 2: Database Storage Fundamentals ✅ *Completed: 2025-08-02*
- [X] Page-based storage architecture
   - **Core principles**: Fixed-size storage units, predictable I/O patterns, cache alignment, space management
   - **Key terminology**: Page, block, extent, tablespace, data file, page header, free space, slot directory, page size
   - **Resources**: 
     - [Database Internals Ch.3 - Storage Engine Architecture](https://www.databass.dev/) (Book)
     - [PostgreSQL Page Layout Documentation](https://www.postgresql.org/docs/current/storage-page-layout.html)
     - [MySQL InnoDB Storage Format](https://dev.mysql.com/doc/internals/en/innodb-page-structure.html)
     - [YouTube: Database Storage Internals](https://www.youtube.com/watch?v=e1wbQPbFZdk) by Hussein Nasser
    - [Dude, Where's My Byte?](https://innovation.enova.com/dude-wheres-my-byte/) - Srivathsava Rangarajan's journey through PostgreSQL internals
    - [How Postgres stores data on disk – this one's a page turner](https://drew.silcock.dev/blog/how-postgres-stores-data-on-disk/) - Drew Silcock's hands-on exploration
    - [Database Pages — A deep dive](https://medium.com/@hnasr/database-pages-a-deep-dive-38cdb2c79eb5) - Hussein Nasser's personal experience
    - [PostgreSQL row storage](https://www.postgresql.fastware.com/pzone/2025-01-postgresql-row-storage) - Gary Evans' practical exploration with pageinspect
    - [How Postgres Stores Rows](https://ketansingh.me/posts/how-postgres-stores-rows/) - Ketan Singh's investigation into storage
    - [Slotted Pages](https://siemens.blog/posts/database-page-layout/) - Ryan Siemens' practical approach to page layouts
    - [Introduction to PostgreSQL physical storage](https://rachbelaid.com/introduction-to-postgres-physical-storage/) - Rachid Belaid's personal journey
    - [Demystifying Pages in postgres](https://sud-gajula.medium.com/what-is-page-in-postgres-15ed42c4e434) - Sudheer Gajula's hands-on exploration
    - Paper: "The Design and Implementation of Modern Column-Oriented Database Systems" (Sections on page organization)

- [x] Disk I/O patterns and optimization
   - **Core principles**: Sequential vs random I/O, read-ahead strategies, write coalescing, I/O scheduler optimization
   - **Key terminology**: Seek time, rotational latency, throughput, IOPS, read-ahead, write-behind, I/O scheduler
   - **Resources**:
     - [Understanding Storage Performance](https://queue.acm.org/detail.cfm?id=1563874) (ACM Queue Article)
     - [YouTube: How SSDs Work](https://www.youtube.com/watch?v=5Mh3o886qpg) by Branch Education
     - [The Pathologies of Big Data](https://queue.acm.org/detail.cfm?id=1563874) (ACM Queue)
     - [Linux I/O Scheduler Documentation](https://www.kernel.org/doc/Documentation/block/switching-sched.txt)
     - Paper: "SSD vs HDD: Performance, Power, and Price Comparison" (USENIX)

- [X] Buffer pool management
   - **Core principles**: Cache replacement policies, dirty page management, hit ratio optimization, memory pressure handling
   - **Key terminology**: Buffer pool, hit ratio, LRU, dirty pages, page pinning, write-behind, replacement policy
   - **Resources**:
     - [YouTube: Database Buffer Pool Explained](https://www.youtube.com/watch?v=1D81vXw2T_w) by Database Internals
     - [What makes MySQL LRU Cache scan resistant](https://arpit.substack.com/p/what-makes-mysql-lru-cache-scan-resistant) - Arpit Bhayani's deep dive into MySQL's midpoint insertion strategy
     - [The Lazy Way to Speed Up PostgreSQL: An Advanced Buffer Management tale](https://medium.com/@ak.kumar220919/the-lazy-way-to-speed-up-postgresql-an-advanced-buffer-management-tale-4b3de9719028) - Abhishek Kumar's graduate research on PostgreSQL buffer optimization
     - [MySQL InnoDB Buffer Pool: A Deep Dive](https://medium.com/@nuwanwe/mysql-innodb-buffer-pool-a-deep-dive-7fecf8ce5149) - Nuwan Weerasinhge's practical guide to buffer pool tuning
     - [Understanding the Buffer Pool in MySQL](https://www.linkedin.com/pulse/understanding-buffer-pool-mysql-dat-nguyen-84bhc) - Dat Nguyen's comprehensive overview with monitoring techniques
     - Paper: "LRU-K: An Efficient Buffer Management Scheme for Relational Database Management Systems" (VLDB)

- [x] Serialization and persistence
   - **Core principles**: Data format design, endianness handling, compression trade-offs, checksum validation, durability guarantees
   - **Key terminology**: Serialization, endianness, compression, checksum, write-ahead logging, durability, persistence
   - **Resources**:
     - [Protocol Buffers Documentation](https://developers.google.com/protocol-buffers) (Google)
     - [Apache Avro Specification](https://avro.apache.org/docs/current/spec.html)
     - [MessagePack vs JSON vs Protocol Buffers](https://auth0.com/blog/beating-json-performance-with-protobuf/) (Auth0 Blog)
     - [Building a Database from Scratch: Understanding Data Serialization](https://dev.to/devdevgo/building-a-database-from-scratch-understanding-data-serialization-3j9m) - Lakshya Negi's hands-on guide to custom binary serialization
     - [A write-ahead log is not a universal part of durability](https://notes.eatonphil.com/2024-07-01-a-write-ahead-log-is-not-a-universal-part-of-durability.html) - Phil Eaton's deep dive into WAL implementation and durability concepts
     - [Building an Append-only Log From Scratch](https://eileen-code4fun.medium.com/building-an-append-only-log-from-scratch-e8712b49c924) - Eileen Pangu's practical implementation guide with Go code
     - [Durability and Redo Logging](https://justinjaffray.com/durability-and-redo-logging/) - Justin Jaffray's exploration of durability guarantees and fsync challenges  
     - [Writing A Database: Part 2 — Write Ahead Log](https://medium.com/@daniel.chia/writing-a-database-part-2-write-ahead-log-2463f5cec67a) - Daniel Chia's real-world WAL implementation with performance benchmarks

**My answers:**
- Page-based storage architecture: Database systems organize data into fixed-size storage units called pages, commonly ranging from 4KB to 16KB (PostgreSQL uses 8KB, MySQL InnoDB defaults to 16KB). Each page has a structured binary format with a page header containing metadata like free space pointers, page type, transaction info, and checksums for corruption detection. Within the page, there's a slot directory that maps slot numbers to record locations, followed by the actual record storage area. The key benefit of fixed-size pages is predictable I/O patterns - the database can calculate exact disk offsets, pages fit efficiently in memory and CPU caches, and buffer pool management becomes straightforward. Pages are loaded into memory when accessed, updates modify the in-memory copy, and dirty pages (modified) are flushed back to disk periodically. This design also enables space management through extents (groups of contiguous pages) which are allocated together for efficiency.
- Disk I/O patterns and optimization: Sequential I/O is much more performant since everything is neatly organized and when you have any information the database index knows where it's and giving the exact location to retrieve it. Opposite sequential I/O is when you don't have database index and searching for a record it scan entire table randomly until it finds the record which does perform many I/O operations
- Buffer pool management: Memory is used to reduce the slow disk I/O operations for accessing database tables and records. Frequently accessed database pages are kept and managed in memory via buffer pool manager. Since memory size is smaller than disk, it's regulated through LRU algorithm that keeps the latest accessed things. When buffer pool becomes full, least recently used pages are evicted to make space for new pages. The buffer pool also manages dirty pages (modified pages) that need to be written back to disk.
- B-tree data nodes living in memory as objects. But memory is volatile. If the program crashes or the server reboots, all that data is lost. To make it durable, you need to save it to a disk. First the data (higher level objects) are serialized into bytes and then the serialized data is persisted to the disk. Just calling file.write() doesn't guarantee the data is on the physical disk. To ensure durability, databases use mechanisms like fsync() to force the OS to flush its caches to the disk.

#### Practical Exercise 2.1: Page Manager Implementation ✅ *Completed: 2025-08-02*

**Section Connection**: This exercise directly applies the following subtopics from this section:
- Page-based storage architecture: Implementing fixed-size page containers for B-tree nodes
- Disk I/O patterns and optimization: Designing efficient page read/write operations
- Buffer pool management: Creating an in-memory cache for frequently accessed pages
- Serialization and persistence: Converting B-tree nodes to/from disk-storable format

**Real-World Context**: Database systems like PostgreSQL's buffer manager and MySQL's InnoDB buffer pool use similar page management techniques to achieve high performance with minimal disk I/O.

**Micro-Objective**: Implement a page manager that can store, retrieve, and cache B-tree nodes using fixed-size pages with proper serialization.

**Mental Model**: Think of the page manager as a smart filing system. Pages are like standardized file folders, the buffer pool is like your desk (quick access), and disk storage is like a filing cabinet (slower but persistent). The page manager knows which folders are on your desk vs in the cabinet.

**Implementation Constraints**: 
- ✅ What TO implement: Page structure, serialization/deserialization, buffer pool cache, disk I/O operations
- ❌ What NOT to implement: Transaction management, crash recovery, concurrent access control, compression
- 🎯 Why these boundaries matter: Focus on storage fundamentals before tackling complex database features

**Scaffolded Code Template**:
```python
import json
import os
from typing import Dict, Optional, Any

class Page:
    def __init__(self, page_id: int, page_size: int = 4096):
        """
        Represents a fixed-size storage page.
        
        Args:
            page_id: Unique identifier for this page
            page_size: Size of page in bytes (default 4KB)
        """
        self.page_id = page_id
        self.page_size = page_size
        self.data = {}  # Will store serialized node data
        self.is_dirty = False  # Has been modified since last disk write
        self.access_count = 0  # For LRU replacement policy
        
    def serialize(self) -> bytes:
        """Convert page data to bytes for disk storage."""
        # TODO: Implement JSON serialization to bytes
        # Hint: Use json.dumps() and encode to bytes
        pass
        
    def deserialize(self, data: bytes) -> None:
        """Load page data from disk bytes."""
        # TODO: Implement JSON deserialization from bytes  
        # Hint: Use decode() and json.loads()
        pass
        
    def can_fit(self, node_data: Dict) -> bool:
        """Check if node data can fit in this page."""
        # TODO: Implement size check
        # Hint: Calculate serialized size and compare to page_size
        pass

class PageManager:
    def __init__(self, data_file: str, buffer_pool_size: int = 100):
        """
        Manages pages in memory and on disk.
        
        Args:
            data_file: Path to disk storage file
            buffer_pool_size: Maximum pages to keep in memory
        """
        self.data_file = data_file
        self.buffer_pool_size = buffer_pool_size
        self.buffer_pool: Dict[int, Page] = {}  # page_id -> Page
        self.next_page_id = 1
        self.page_size = 4096
        
        # Create data file if it doesn't exist
        if not os.path.exists(data_file):
            with open(data_file, 'wb') as f:
                pass
    
    def get_page(self, page_id: int) -> Optional[Page]:
        """Get page from buffer pool or load from disk."""
        # TODO: Implement buffer pool lookup and disk loading
        # Hint: Check buffer_pool first, then load from disk if needed
        pass
        
    def store_node(self, node) -> int:
        """Store a B-tree node and return its page ID."""
        # TODO: Implement node storage with page allocation
        # Hint: Serialize node, find/create page, store data
        pass
        
    def load_node(self, page_id: int):
        """Load a B-tree node from storage."""
        # TODO: Implement node loading from page
        # Hint: Get page, deserialize data, reconstruct node
        pass
        
    def flush_dirty_pages(self) -> None:
        """Write all dirty pages to disk."""
        # TODO: Implement dirty page flushing
        # Hint: Find dirty pages, write to disk, mark as clean
        pass
        
    def _write_page_to_disk(self, page: Page) -> None:
        """Write a single page to disk at correct offset."""
        # TODO: Implement disk write operation
        # Hint: Calculate file offset, write serialized data
        pass
        
    def _read_page_from_disk(self, page_id: int) -> Optional[Page]:
        """Read a single page from disk."""
        # TODO: Implement disk read operation
        # Hint: Calculate file offset, read data, deserialize
        pass
        
    def _evict_page(self) -> None:
        """Remove least recently used page from buffer pool."""
        # TODO: Implement LRU eviction policy
        # Hint: Find page with lowest access_count, flush if dirty
        pass
```

**Step-by-Step Guide**:
1. **Step 1**: Implement `Page.serialize()` and `Page.deserialize()` methods using JSON format for B-tree node data
2. **Step 2**: Implement `PageManager.get_page()` with buffer pool lookup and disk loading fallback
3. **Step 3**: Implement `store_node()` and `load_node()` methods to handle B-tree node persistence
4. **Step 4**: Implement `flush_dirty_pages()` and LRU eviction in `_evict_page()` for buffer pool management

**Single Success Test**:
```python
def test_page_manager():
    # Create page manager with small buffer pool
    pm = PageManager("test_btree.db", buffer_pool_size=2)
    
    # Create test node data
    node_data = {
        "degree": 3,
        "is_leaf": True,
        "keys": [10, 20, 30],
        "children": []
    }
    
    # Store node and get page ID
    page_id = pm.store_node(node_data)
    assert page_id > 0
    
    # Load node back from storage
    loaded_node = pm.load_node(page_id)
    assert loaded_node["keys"] == [10, 20, 30]
    assert loaded_node["degree"] == 3
    
    # Test buffer pool eviction with multiple nodes
    node_data2 = {"degree": 3, "is_leaf": False, "keys": [40, 50], "children": []}
    node_data3 = {"degree": 3, "is_leaf": True, "keys": [60, 70], "children": []}
    
    page_id2 = pm.store_node(node_data2)
    page_id3 = pm.store_node(node_data3)  # Should trigger eviction
    
    # Verify all nodes can still be loaded (from disk if evicted)
    loaded_node1 = pm.load_node(page_id)
    loaded_node2 = pm.load_node(page_id2)
    loaded_node3 = pm.load_node(page_id3)
    
    assert loaded_node1["keys"] == [10, 20, 30]
    assert loaded_node2["keys"] == [40, 50]
    assert loaded_node3["keys"] == [60, 70]
    
    # Cleanup
    pm.flush_dirty_pages()
    os.remove("test_btree.db")
    
    print("✅ All tests passed! Page manager working correctly.")

# Run the test
test_page_manager()
```

**Common Mistakes to Avoid**:
- Mistake 1: Not handling file offsets correctly - each page must be written at `page_id * page_size` offset
- Mistake 2: Forgetting to mark pages as dirty after modifications - leads to data loss
- Mistake 3: Not implementing proper LRU eviction - can cause memory overflow with large datasets
- Mistake 4: Ignoring serialization size limits - pages have fixed capacity

**Debugging Guide**:
- "If `serialize()` fails, check that your data structure is JSON-serializable (no circular references)"
- "If pages aren't persisting, verify `is_dirty` is set to `True` after modifications"
- "If buffer pool overflows, ensure `_evict_page()` is called when buffer_pool_size is exceeded"
- "If disk I/O fails, check file permissions and that page offsets are calculated correctly"

#### Self-Check Quiz 2.1 ✅ *Completed: 2025-08-02*
1. Why do databases use fixed-size pages instead of variable-size storage units?
2. What is the relationship between page size and I/O performance in different storage types (HDD vs SSD)?
3. How does the buffer pool hit ratio affect overall database performance?
4. What are the trade-offs between JSON serialization and binary serialization for B-tree nodes?

**My answers:**
1. Databases use fixed-size pages primarily for performance and simplicity. With fixed sizes, the location of any page on disk can be calculated instantly (offset = page_id * page_size), allowing for fast, direct disk reads. Crucially, it makes updates simple: an existing page can be overwritten in place without affecting any other pages. In contrast, variable-sized units would require a complex and slow process of shifting large amounts of data to make space when a record grows, which is not feasible for high-performance systems
2. For HDDs, larger page sizes (e.g., 64KB+) are better because they maximize the amount of data read per expensive mechanical seek. For SSDs, the ideal page size is one that aligns with the drive's internal block size (typically 4KB-16KB) to take full advantage of the hardware's parallelism without causing unnecessary I/O for small lookups.
3. The buffer pool hit ratio is the percentage of data requests that are served from the in-memory cache (a "hit") instead of requiring a slow disk read (a "miss"). It has a direct and dramatic impact on performance because accessing memory is thousands of times faster than accessing a disk. A high hit ratio (e.g., 99%+) means most operations are lightning-fast, as they avoid disk I/O. A low hit ratio means the database is constantly waiting for the disk, and performance will be poor. Therefore, a primary goal of database tuning is to maximize the buffer pool hit ratio, often by allocating more memory to the database.
4. JSON Serialization is human-readable, making it easy to debug, and is simple to implement using standard libraries. However, it is verbose, leading to larger file sizes, and is computationally slower to parse. Binary Serialization (like Protocol Buffers or a custom struct) is extremely compact and significantly faster for the CPU to process because it maps directly to native data types. This is what production databases use. The downside is that the resulting data is not human-readable, and the implementation is more complex, requiring careful management of byte layout and endianness.

---

### Section 3: B-Tree Search Operations ✅ *Completed: 2025-08-03*
- [X] Recursive and iterative search algorithms
   - **Core principles**: Tree traversal from root to leaf, descending through child pointers based on key comparisons. Iterative approaches are generally preferred in systems programming to avoid deep recursion stacks.
   - **Key terminology**: Traversal path, current node, search key, child pointer.
   - **Resources**:
     - [YouTube: B-Tree Search Algorithm Explained](https://www.youtube.com/watch?v=aZjYr87r1b8) by CS Dojo.
     - [Database Internals Ch.4 - B-Tree Search](https://www.databass.dev/) (Book).
     - [Python's `bisect` module documentation](https://docs.python.org/3/library/bisect.html) (for efficient in-node search).

**My answers:**
- The search always starts at the root node and traverses down towards a leaf node. It never goes back up. At each internal node, it uses binary search to find the correct child pointer to follow. If the search key is *less than* the first key in the node, you follow the first child pointer. If the search key is *between* two keys `key_i` and `key_j`, you follow the child pointer that is also between them. - - If the search key is *greater than* the last key, you follow the last child pointer.

#### Practical Exercise 3.1: Search Implementation ✅ *Completed: 2025-08-03*

**Section Connection**: This exercise directly applies the following subtopics from this section:
- Recursive and iterative search algorithms: Implementing an iterative search to traverse the B-Tree from root to leaf.
- Path tracking for updates: Recording the parent nodes and key indices during traversal to enable future modifications.
- Key terminology: Traversal path, search key, child pointer, binary search.

**Real-World Context**: This search algorithm is the heart of every database index lookup, executed millions of times per second in production systems to locate data for queries.

**Micro-Objective**: Implement a `BTree` class with a search method that traverses the tree using the `PageManager` and returns the path taken.

**Mental Model**: Think of searching the B-Tree like looking up a topic in a multi-volume encyclopedia. The root node is the index volume. It tells you which volume (child node) to look in. You grab that volume, look at its table of contents (keys), and it tells you which chapter (next child node) to go to, until you finally find the page (leaf node) with the information you need.

**Implementation Constraints**: 
- ✅ What TO implement: A `BTree` class that holds a `PageManager`, a `search` method that takes a key and returns a path.
- ❌ What NOT to implement: Insertion, deletion, splitting, or merging logic. The tree is read-only for this exercise.
- 🎯 Why these boundaries matter: To focus solely on the traversal logic, which is the foundation for all other B-Tree operations.

**Scaffolded Code Template**:
```python
# In a new file: src/btree.py
import bisect
from typing import List, Tuple

from .node import Node
from .page import PageManager

class BTree:
    def __init__(self, pm: PageManager, root_page_id: int = None):
        self.pm = pm
        self.root_page_id = root_page_id

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
            # TODO: Load the current node using the PageManager.
            # TODO: If the node can't be loaded, something is wrong. Break the loop.
            
            # TODO: Use bisect.bisect_left to find the insertion point for the key
            #       in the node's keys list. This is your key_index.
            
            # TODO: Add the (current_page_id, key_index) to the path.

            # TODO: Check if the key was found at the insertion point.
            #       If found, return True and the path.

            # TODO: If the current node is a leaf, the search is over. Break the loop.
            
            # TODO: If it's not a leaf, descend to the correct child.
            #       Update current_page_id to the child's page_id.
            pass # Remove this once you start implementing

        return False, path

```

**Step-by-Step Guide**:
1. **Step 1**: Create a new file `src/btree.py` and add the `BTree` class structure.
2. **Step 2**: In the `search` method's loop, use `self.pm.load_node(current_page_id)` to get the current `Node` object.
3. **Step 3**: Use `bisect.bisect_left(node.keys, key)` to efficiently find the index where the key *would be* in the sorted `keys` list.
4. **Step 4**: Check if the key is actually present at that index. If `node.keys[index] == key`, you've found it.
5. **Step 5**: If the key is not found and the node is not a leaf, get the page ID of the correct child from `node.children[index]` and continue the loop. If it is a leaf, the search ends.

**Single Success Test**:
```python
# In a new file: tests/test_search.py
from src.btree import BTree
from src.node import Node
from src.page import PageManager

def setup_test_tree():
    pm = PageManager("search_test.db")
    
    # Leaf nodes
    leaf1 = Node(degree=2, is_leaf=True)
    leaf1.keys = [10, 20]
    leaf1_id = pm.store_node(leaf1)

    leaf2 = Node(degree=2, is_leaf=True)
    leaf2.keys = [40, 50]
    leaf2_id = pm.store_node(leaf2)

    # Root node
    root = Node(degree=2, is_leaf=False)
    root.keys = [30]
    root.children = [leaf1_id, leaf2_id]
    root_id = pm.store_node(root)
    
    pm.flush_dirty_pages()
    return BTree(pm, root_id)

def test_search_found():
    btree = setup_test_tree()
    found, path = btree.search(40)
    assert found is True
    assert path == [(3, 1), (2, 0)] # Path: root (page 3, index 1) -> leaf2 (page 2, index 0)
    print("✅ test_search_found passed")

def test_search_not_found():
    btree = setup_test_tree()
    found, path = btree.search(25)
    assert found is False
    assert path == [(3, 0), (1, 2)] # Path: root (page 3, index 0) -> leaf1 (page 1, index 2)
    print("✅ test_search_not_found passed")

# Run tests
test_search_found()
test_search_not_found()
```

**Common Mistakes to Avoid**:
- Mistake 1: Off-by-one errors when checking for the found key after `bisect_left`.
- Mistake 2: Forgetting to handle the case where the root is `None`.
- Mistake 3: Not correctly updating `current_page_id` to descend into the child node.

**Debugging Guide**:
- "If search fails, print the `current_page_id`, the `node.keys`, and the `key_index` inside the loop to trace the traversal."
- "If `bisect_left` gives an index out of bounds for the `children` array, check your logic for descending."

#### Self-Check Quiz 3.1
1. Why is binary search (like `bisect_left`) critical for performance within B-tree nodes?
2. How does B-tree search complexity compare to a hash table lookup in the best/worst cases?
3. What information must be tracked during a search to prepare for a subsequent insertion or deletion?

**My answers:**
- **Question 1:** Binary search (`O(log k)`) is critical because B-tree nodes are very large and can hold thousands of keys (`k`). A linear scan (`O(k)`) would be too slow within each node of the search path. Binary search makes the in-memory search time negligible, ensuring the main performance cost remains disk I/O (tree height), not CPU.
- **Question 2:** A hash table is faster for single key lookups (`O(1)` on average) but B-trees (`O(log N)`) are better for range scans (e.g., `id > 100`). Hash tables can degrade to `O(N)` in the worst case (many collisions), while B-trees offer a predictable `O(log N)` worst-case performance. Databases use B-trees for indexes because range queries are a critical feature.
- **Question 3:** The search must track the complete traversal path from the root to the leaf. This path is a list of `(page_id, key_index)` tuples for each node visited. This information is essential for navigating back up the tree to perform splits (on insertion) or merges/borrows (on deletion) if a node overflows or underflows.

---

### Section 4: B-Tree Insertion and Node Splitting ✅ *Completed: 2025-08-04*
- [X] **Insertion algorithm and overflow handling**: The core logic for adding a new key. It starts with a search to find the correct leaf node. If the leaf is not full, the key is simply inserted in sorted order. If the leaf is full, it triggers an overflow, which is handled by a node split.
   - **Resources**:
     - [B-Tree Visualizer](https://www.cs.usfca.edu/~galles/visualization/BTree.html) - An interactive tool to see insertions and splits happen step-by-step.
     - [YouTube: B-Tree Insertion Explained](https://www.youtube.com/watch?v=Wl31aC5-82A) by Michael Sambol.
- [X] **Node splitting and median promotion**: When a node becomes full (with `2t-1` keys), it must be split. The median key is identified, and the node is divided into two new nodes: one with keys smaller than the median and one with keys larger. The median key itself is "promoted" up to the parent node to act as a separator between the two new child nodes.
   - **Resources**:
     - [GeeksForGeeks: Insertion into a B-Tree](https://www.geeksforgeeks.org/insert-operation-in-b-tree/) - Provides a detailed textual and visual walkthrough of the split-and-promote mechanism.
- [X] **Root splitting and tree height increase**: A special case occurs when the root node itself is split. A new root is created containing only the promoted median key. This new root will have the two split nodes as its children. This is the only way a B-Tree's height increases.
   - **Resources**:
     - Paper: "The Ubiquitous B-Tree" by Douglas Comer (Section 4.2 describes the splitting process including the root).

#### Practical Exercise 4.1: Insertion with Splitting ✅ *Completed: 2025-08-04*

**Section Connection**: This exercise directly applies the following subtopics from this section:
- Insertion algorithm and overflow handling: Implementing the main `insert` logic.
- Node splitting and median promotion: Creating a `split_child` helper method.
- Root splitting: Handling the special case where the root itself must be split.
- Key terminology: overflow, split, median promotion.

**Real-World Context**: This is how databases like PostgreSQL and MySQL add new entries to your indexes, ensuring the tree remains balanced and searches remain fast even after millions of writes.

**Micro-Objective**: Implement a B-Tree `insert` method that correctly handles node splitting when a leaf node becomes full.

**Mental Model**: Imagine adding a new card to a full drawer in a filing cabinet. You find the middle card, pull it out, and put it in the main cabinet's index. Then you split the remaining cards into two new, half-full drawers, and update the main index to point to both.

**Implementation Constraints**:
- ✅ What TO implement: An `insert` method and a `split_child` helper.
- ❌ What NOT to implement: Deletion, merging, or borrowing logic.
- 🎯 Why these boundaries matter: To isolate the logic of insertion and splitting, which is complex enough on its own.

**Scaffolded Code Template**:
```python
# In src/btree.py, add these methods to the BTree class

    def insert(self, key: int):
        """Insert a key into the B-Tree."""
        root_node = self.pm.load_node(self.root_page_id)
        
        # Case 1: Root is full, so it must be split.
        if root_node.is_full():
            # TODO: Create a new root node.
            # Its is_leaf will be False.
            # Its first child will be the old root's page_id.
            
            # TODO: Store the new root and update self.root_page_id.
            
            # TODO: Split the old root (which is now a child of the new root).
            # Use a new helper method self.split_child(...) for this.
            
            # TODO: Decide which of the two children to descend into and
            #       insert the key into that child.
            # Use a new helper method self.insert_non_full(...) for this.
        else:
            # Case 2: Root is not full, so insert into the tree as normal.
            self.insert_non_full(self.root_page_id, key)

    def split_child(self, parent_page_id: int, child_index: int):
        """
        Split the child of a parent node.
        
        Args:
            parent_page_id: The page ID of the parent node.
            child_index: The index in the parent's children list that points
                         to the child to be split.
        """
        # TODO: Load the parent and the full child node from the PageManager.
        
        # TODO: Create a new node (the "sibling") to store the upper half of the keys.
        
        # TODO: Find the median key in the child. This key will be promoted.
        
        # TODO: Move the upper half of the keys from the child to the new sibling.
        
        # TODO: If the child was not a leaf, move the upper half of its children
        #       to the new sibling as well.
        
        # TODO: Insert the median key into the parent's keys.
        
        # TODO: Insert the new sibling's page_id into the parent's children list.
        
        # TODO: Store the modified parent, child, and new sibling nodes back
        #       to the PageManager.
        pass

    def insert_non_full(self, page_id: int, key: int):
        """Insert a key into a node that is guaranteed to be not full."""
        node = self.pm.load_node(page_id)
        
        if node.is_leaf:
            # Case 1: If it's a leaf, find the correct spot and insert the key.
            # TODO: Use bisect.insort to insert the key into node.keys.
            # TODO: Store the modified node back to the PageManager.
        else:
            # Case 2: If it's an internal node, find the child to descend into.
            # TODO: Use bisect.bisect_right to find the correct child index.
            
            # TODO: Load the child node to check if it is full.
            
            # TODO: If the child IS full, split it first using self.split_child(...).
            # After splitting, the parent will have a new key. You must check
            # if the key to be inserted should go into the original child or the new one.
            
            # TODO: Recursively call self.insert_non_full on the correct child.
            pass
```

**Step-by-Step Guide**:
1. **Step 1**: Implement the `insert_non_full` method for the simple case where the node is a leaf. Use `bisect.insort`.
2. **Step 2**: Implement the `split_child` method. This is the most complex part. Focus on correctly dividing the keys and children between the original node and the new sibling, and promoting the median key to the parent.
3. **Step 3**: Complete the `insert_non_full` method for internal nodes. It must check if a child is full and call `split_child` *before* descending.
4. **Step 4**: Implement the main `insert` method, which handles the special case of the root being full.

**Single Success Test**:
```python
# In tests/test_insertion.py
from src.btree import BTree
from src.page import PageManager
import os

def test_insert_and_split():
    # Setup with degree 2 (max 3 keys)
    pm = PageManager("insert_test.db")
    btree = BTree(pm) # Starts with an empty tree
    
    # Insert keys that will cause splits
    keys_to_insert = [10, 20, 30, 5, 15, 25, 35]
    for key in keys_to_insert:
        btree.insert(key)
        
    # Verify the final structure (this depends on the exact split logic)
    # A correct B-Tree of degree 2 with these keys would have height 2.
    # Root should be [20]
    root = pm.load_node(btree.root_page_id)
    assert root.keys == [20]
    
    # Check children of the root
    left_child = pm.load_node(root.children[0])
    right_child = pm.load_node(root.children[1])
    
    assert left_child.keys == [5, 10, 15]
    assert right_child.keys == [25, 30, 35]
    
    print("✅ test_insert_and_split passed")
    
    # Cleanup
    os.remove("insert_test.db")

# Run test
test_insert_and_split()
```

**Common Mistakes to Avoid**:
- Mistake 1: Off-by-one errors when calculating the median key and splitting the key/child lists.
- Mistake 2: Forgetting to save all modified nodes (parent, child, and new sibling) back to the page manager after a split.
- Mistake 3: Incorrectly handling the indices in the parent node after a child has been split.

**Debugging Guide**:
- "If keys are disappearing, you are likely not saving a modified node back to the page manager."
- "If the tree structure looks wrong, print the parent, child, and sibling nodes before and after the `split_child` call to see how they are being modified."
- "Use a small degree (like `t=2`) for testing, as it makes it much easier to trigger splits and reason about the tree structure."

#### Self-Check Quiz 4.1
1. Why is the median key promoted during a split instead of just being copied to the new sibling?
2. What is "cascading split" and how does the provided `insert` logic handle it?
3. Why is it more efficient to check if a child is full *before* descending into it?
4. What happens if you try to insert a key that already exists in the tree?

---

### Section 5: B-Tree Deletion and Node Merging
- [ ] **Deletion from a Leaf Node**: The simplest case. If the leaf has sufficient keys, the key is removed. If not, it triggers an underflow, which must be resolved.
   - **Core principles**: Underflow condition, minimum key constraint (`t-1`).
   - **Resources**:
     - [Let's Build a B-Tree](https://www.chiark.greenend.org.uk/~sgtatham/algorithms/cbtree.html) by Simon Tatham - A brilliantly clear, from-scratch C implementation and explanation that covers deletion logic in detail.
     - [B-Trees: More Than Just an Academic Curiosity](https://rcoh.me/posts/btree-more-than-just-an-academic-curiosity/) by Ryan Cohen - A personal journey of implementing a B-Tree in Rust, with practical insights on edge cases.

- [ ] **Deletion from an Internal Node**: This requires replacing the deleted key with its in-order successor or predecessor and then recursively deleting that successor/predecessor from its leaf node.
   - **Core principles**: In-order successor/predecessor, recursive deletion.
   - **Resources**:
     - [Building a B-Tree in Go](https://appliedgo.net/btree/) - A multi-part series that walks through the implementation, including the nuances of handling internal node deletion.
     - [The Art of Deletion in B-Trees](https://medium.com/@database_nerd/the-art-of-deletion-in-b-trees-a-practical-guide-a1ba476a248) - A blog post focusing specifically on the practical challenges and code structure for this part of the algorithm.

- [ ] **Resolving Underflow: Borrowing and Merging**: The core of deletion logic. If a node underflows, it must borrow from a well-off sibling or merge with a sibling that is also at minimum capacity.
   - **Core principles**: Key rotation, cascading merges, maintaining tree balance.
   - **Resources**:
     - [B-Tree Visualizer](https://www.cs.usfca.edu/~galles/visualization/BTree.html) - An essential interactive tool to visualize the mechanics of borrowing and merging before you code them.
     - [A B-Tree in Python](https://gist.github.com/nayuki/8343463) by Nayuki - A clean, well-commented Python implementation that shows one way to structure the borrow and merge logic.
     - [Database Internals: A Deep Dive into How Distributed Data Systems Work](https://www.databass.dev/chapters/b-trees/) by Alex Petrov - While a book, this chapter is available online and provides an excellent, systems-level view of why these operations are designed the way they are.

- [ ] **Root Deletion and Height Decrease**: The special case where a merge operation propagates to the root, causing the tree to shrink in height.
   - **Core principles**: Root underflow, height decrease.
   - **Resources**:
     - [When B-Trees Shrink](https://blog.penjee.com/b-tree-deletion-intricacies/) - A blog post that uses diagrams to focus specifically on the conditions that lead to a height decrease, a scenario that is often glossed over.

**My answers:**
- Subtopic 5.1
- Subtopic 5.2
- Subtopic 5.3
- Subtopic 5.4

#### Practical Exercise 5.1: Deletion with Borrowing and Merging

**Section Connection**: This exercise directly applies all subtopics from this section:
- Deletion from a Leaf Node: The base case for all deletions.
- Deletion from an Internal Node: Handling the replacement with a successor/predecessor.
- Borrowing from a Sibling: The first strategy to resolve an underflow.
- Merging with a Sibling: The second strategy when borrowing fails.
- Root Deletion: Handling the case where the tree shrinks in height.
- Key terminology: underflow, borrow, merge, successor, predecessor.

**Real-World Context**: This logic is critical for database systems to handle `DELETE` statements efficiently while keeping indexes balanced and fast.

**Micro-Objective**: Implement a `delete` method in the `BTree` class that correctly handles all underflow scenarios using borrowing and merging.

**Mental Model**: Think of deletion as the reverse of insertion. If a filing cabinet drawer (node) has too few files after one is removed, you first try to borrow a file from the drawer next to it. If the neighboring drawer is also nearly empty, you combine the two drawers into one to save space.

**Implementation Constraints**: 
- ✅ What TO implement: A `delete` method and helper methods for finding a successor, borrowing, and merging.
- ❌ What NOT to implement: Concurrency control or transaction logic.
- 🎯 Why these boundaries matter: To focus entirely on the complex logic of maintaining B-Tree properties during deletion.

**Scaffolded Code Template**:
```python
# In src/btree.py, add these methods to the BTree class

    def delete(self, key: int):
        """Public method to delete a key from the tree."""
        # TODO: Start the recursive deletion from the root.
        # self._delete_recursive(self.root_page_id, key)
        pass

    def _delete_recursive(self, page_id: int, key: int):
        """Recursively find and delete a key."""
        # TODO: Load the current node.
        # TODO: Find the index of the key or the child to descend into.

        # Case 1: The key is in the current node.
        # if key_is_found:
            # Case 1a: If it's a leaf, just remove the key.
            # Case 1b: If it's an internal node, replace with successor/predecessor
            #          and recursively delete the successor/predecessor from the leaf.
            # After deletion/replacement, check if the node underflowed.
        
        # Case 2: The key is not in the current node.
        # else:
            # TODO: Descend to the appropriate child.
            # TODO: Before descending, check if the child node is minimal.
            #       If it is, you must resolve it first by borrowing or merging
            #       to ensure you don't descend into an underflowing node.
            #       This is the proactive approach, similar to insertion.
            # TODO: Recursively call _delete_recursive on the child.
        pass

    def _resolve_underflow_before_descending(self, parent_page_id: int, child_index: int):
        """
        Checks a child node and resolves underflow by borrowing or merging
        before the recursive call descends into it.
        """
        # TODO: Load the child and its left/right siblings.
        # TODO: Check if the left sibling has enough keys to lend one.
        #       If yes, call a _borrow_from_left_sibling helper.
        # TODO: Check if the right sibling has enough keys to lend one.
        #       If yes, call a _borrow_from_right_sibling helper.
        # TODO: If neither sibling can lend a key, merge the child
        #       with one of them. Call a _merge_with_sibling helper.
        pass

```

**Step-by-Step Guide**:
1. **Step 1**: Implement the simplest case: deletion from a leaf node that does not cause an underflow.
2. **Step 2**: Implement the logic for finding a successor/predecessor to handle deletion from an internal node.
3. **Step 3**: Implement the `_borrow_from_left_sibling` and `_borrow_from_right_sibling` helper methods. This involves key rotation through the parent.
4. **Step 4**: Implement the `_merge_with_sibling` helper method. This is the most complex part, as it may trigger a recursive underflow in the parent.
5. **Step 5**: Combine all the pieces in the main `_delete_recursive` method, making sure to proactively resolve underflows before descending.

**Single Success Test**:
```python
# In tests/test_deletion.py
from src.btree import BTree
import os

def setup_test_tree_for_deletion():
    db_file = "delete_test.db"
    if os.path.exists(db_file):
        os.remove(db_file)
    
    btree = BTree(db_file, max_keys_per_node=3)
    keys = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    for key in keys:
        btree.insert(key)
    return btree

def test_delete_simple_leaf():
    btree = setup_test_tree_for_deletion()
    btree.delete(10)
    found, _ = btree.search(10)
    assert not found
    print("✅ test_delete_simple_leaf passed")

def test_delete_causing_borrow():
    btree = setup_test_tree_for_deletion()
    # This will require borrowing from a sibling to maintain the B-Tree property.
    btree.delete(80) 
    found, _ = btree.search(80)
    assert not found
    # Add asserts to check the final state of the nodes.
    print("✅ test_delete_causing_borrow passed")

def test_delete_causing_merge():
    btree = setup_test_tree_for_deletion()
    # Deleting these keys will force a node merge.
    btree.delete(80)
    btree.delete(90)
    btree.delete(70) # This deletion should trigger a merge.
    found, _ = btree.search(70)
    assert not found
    # Add asserts to check the final state of the tree (e.g., root key).
    print("✅ test_delete_causing_merge passed")

# Run tests
# test_delete_simple_leaf()
# test_delete_causing_borrow()
# test_delete_causing_merge()
```

**Common Mistakes to Avoid**:
- Mistake 1: Forgetting to handle the case where the root becomes empty and the tree height needs to decrease.
- Mistake 2: Incorrectly rotating keys during a borrow operation, leading to an unbalanced tree.
- Mistake 3: Not recursively handling underflow in the parent after a merge operation.

**Debugging Guide**:
- "If keys are not being deleted, trace the `_delete_recursive` path to see where the search for the key is failing."
- "If the tree structure is invalid after a deletion, print the parent, child, and sibling nodes before and after a borrow/merge operation to check the logic."
- "Use a small `max_keys_per_node` (like 3) to make it easy to trigger underflow conditions for testing."

#### Self-Check Quiz 5.1
1. Why is it generally more efficient to borrow from a sibling rather than merging nodes?
2. What is the role of the parent node's key in both borrowing and merging operations?
3. How does deleting the in-order successor from a leaf node simplify the logic for deleting from an internal node?
4. Describe the sequence of events that leads to the height of a B-Tree decreasing.

**My answers:**
- Question 1
- Question 2
- Question 3
- Question 4

---

### Section 6: Performance Analysis and Optimization
- [ ] Time and space complexity analysis
- [ ] Cache-friendly design patterns
- [ ] Bulk loading strategies
- [ ] Concurrency and locking considerations

#### Key Concepts
- **I/O efficiency**: Minimizing disk reads through optimal node size
- **Cache locality**: Designing for CPU cache effectiveness
- **Bulk loading**: Efficient techniques for loading large datasets
- **Lock coupling**: Concurrency control in multi-user scenarios
- **Write amplification**: Understanding update costs

#### Practical Exercise 6.1: Performance Optimization
Benchmark and optimize your B-tree implementation:

```python
# Expected implementation: Benchmarking suite and optimization techniques
# Success criteria: Measurable performance improvements, cache-friendly design
```

#### Self-Check Quiz 6.1
1. How does node size affect both I/O performance and memory usage?
2. What are the trade-offs between read and write performance in B-trees?
3. How can bulk loading be more efficient than individual insertions?

## Project Goal: A Complete Database Storage Engine

Create a fully functional database storage engine that demonstrates mastery of all concepts:

### Core Requirements
1. **B+tree index implementation** with all CRUD operations
2. **Page-based storage manager** with persistence and caching
3. **Simple SQL-like query interface** supporting SELECT, INSERT, UPDATE, DELETE
4. **Transaction support** with basic ACID properties
5. **Multiple indexes** on the same table
6. **Range queries and aggregations** (COUNT, SUM, MIN, MAX)

### Deliverables
- Complete Python implementation (estimated 1000-1500 lines)
- Comprehensive test suite covering edge cases
- Performance benchmarks comparing different configurations
- Documentation explaining design decisions
- Demo script showing real-world usage scenarios

### Assessment Criteria
- **Correctness**: All B-tree properties maintained under all operations
- **Performance**: Efficient I/O patterns and memory usage
- **Robustness**: Handles edge cases and error conditions gracefully
- **Code quality**: Clean, readable, well-documented implementation
- **Real-world applicability**: Could serve as foundation for actual database system

### Extension Challenges (Optional)
- Implement concurrent access with proper locking
- Add compression to reduce storage requirements
- Implement write-ahead logging for crash recovery
- Add support for variable-length keys and values
- Optimize for specific workload patterns (read-heavy vs write-heavy)

## Progress Tracking
- Use [x] for completed items
- Use [ ] for pending items
- Date stamp when sections are completed

### Next Steps After Completion
- Study LSM-trees and other storage structures
- Explore distributed database systems (Spanner, CockroachDB)
- Learn about query optimization and execution engines
- Investigate modern storage formats (Parquet, Arrow)
- Contribute to open-source database projects
