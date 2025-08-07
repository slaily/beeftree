# beeftree: A database storage engine from scratch

> A hands-on journey into database internals, implementing a page-based storage manager, buffer pool, and B-Tree index in pure Python.

## Introduction & motivation
This repository documents the creation of a simple database storage engine from the ground up. The primary goal is not to build a production-ready database, but to gain a deep, practical understanding of the components that power them.

This project serves as a personal study of core database concepts.

## Core components implemented
- **Page-Based Storage Manager:** A manager that abstracts a file on disk into fixed-size pages, handling reads and writes at specific offsets.
- **Buffer Pool:** An in-memory cache for disk pages (`StorageManager`) that uses a second-chance eviction policy to minimize I/O.
- **B-Tree Index:** A self-balancing tree structure providing efficient key-based search, insertion, and deletion (`O(log N)`).
  - **Insertion:** Proactively splits nodes when they become full.
  - **Deletion:** Proactively rebalances nodes by borrowing from siblings or merging to handle underflow.
- **Serialization:** A simple JSON-based protocol to persist in-memory data structures to disk.

## Code structure
- `src/btree.py`: The main B-Tree class, orchestrating all CRUD operations and managing the tree structure.
- `src/node.py`: Defines the structure of a B-Tree node, including keys, children, and capacity logic.
- `src/storage.py`: Implements the `DiskPage` and `StorageManager` classes responsible for disk I/O and in-memory caching.

## My learning journey

This project follows a structured learning plan. My detailed notes, research, and progress are documented in the [Database Storage Engine - Learning Guide](./learnings/database-storage-engine.md). This document serves as the primary 'lab notebook' for the project.

## Future goals
- **Concurrency Control:** Implementing latches to allow for safe multi-threaded access.
- **Write-Ahead Logging (WAL):** Adding a WAL for crash recovery and durability.
