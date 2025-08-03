# beeftree: A database storage engine from scratch

> A hands-on journey into database internals, implementing a page-based storage manager, buffer pool, and B-Tree index in pure Python.

## Introduction & Motivation
This repository documents the creation of a simple database storage engine from the ground up. The primary goal is not to build a production-ready database, but to gain a deep, practical understanding of the components that power them.

This project serves as a personal study of core database concepts.

## Core Components Implemented
- **Page-Based Storage Manager:** A manager that abstracts a file on disk into fixed-size pages, handling reads and writes at specific offsets.
- **Buffer Pool:** An in-memory cache for disk pages (`PageManager`) that uses a second-chance eviction policy to minimize I/O and keep frequently accessed data in memory.
- **B-Tree Index:** A self-balancing tree structure that provides efficient key-based search, forming the primary indexing mechanism.
- **Serialization:** A simple JSON-based protocol to persist in-memory data structures (like nodes) to disk.

## Code Structure
- `src/btree.py`: The main B-Tree class, orchestrating search operations and managing the root node.
- `src/node.py`: Defines the structure of a B-Tree node, including keys and child pointers.
- `src/page.py`: Implements the `Page` and `PageManager` classes responsible for disk I/O and in-memory caching.

## My Learning Journey

This project follows a structured learning plan. My detailed notes, research, and progress are documented in the [Database Storage Engine - Learning Guide](./learnings/database-storage-engine.md). This document serves as the primary 'lab notebook' for the project.

## Future Goals
- Implement Insertion with Node Splitting
- Implement Deletion with Node Merging/Borrowing
- Concurrency Control
- Write-Ahead Logging (WAL) for recovery
