# beeftree: A b-tree implementation for learning database internals

## Introduction & Motivation
This repository contains a Python implementation of a B-Tree, built from scratch as a hands-on project to understand the internal workings of database systems. The primary goal is not to create a production-ready database, but to explore and implement core concepts like page-based storage, buffer management, and tree-based indexing.

## Core Concepts Implemented
- **B-Tree Structure:** Core logic for nodes and tree traversal.
- **Page-Based Storage:** Data is stored in fixed-size pages on disk.
- **Buffer Pool Management:** An in-memory cache (`PageManager`) to minimize disk I/O using a second-chance eviction policy.
- **Serialization:** Nodes are serialized to JSON for persistence to disk.

## Code Structure
- `src/btree.py`: The main B-Tree class, orchestrating search operations and managing the root node.
- `src/node.py`: Defines the structure of a B-Tree node, including keys and child pointers.
- `src/page.py`: Implements the `Page` and `PageManager` classes responsible for disk I/O and in-memory caching.

## My Learning Journey
This project follows a structured learning plan. My detailed notes, research, and progress are documented in the [B-Tree Database Internals - Learning Guide](./learnings/001-btree-database-internals.md). This document serves as the primary 'lab notebook' for the project.