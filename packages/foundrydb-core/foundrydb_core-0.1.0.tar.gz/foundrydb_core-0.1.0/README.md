# FoundryDB

<p align="center">
  <img src="assets/banner.png" width="50%" />
</p>

![Version](https://img.shields.io/badge/version-0.1.0-orange)

**A tiny educational SQL engine written in pure Python.**

FoundryDB is a personal experimental project to explore how relational database systems actually work under the hood. From parsing SQL, to planning, to storage and tuple access.

This is not production-grade software. It's a playground.

---

## Goals

- Teach myself the internal moving parts of a DBMS
- Be small enough to understand in a single sitting
- Pure Python
- Transparent / readable code > performance

---

## Non-goals

- Competing with SQLite or Postgres
- Correctness for all SQL edge cases
- Maximizing speed

---

## Rough architecture (planned)

| Layer | Responsibility |
|---|---|
| **Lexer/Parser** | tokenize & parse SQL into AST |
| **Planner** | validate AST + generate logical plans |
| **Execution Engine** | run plans against storage |
| **Storage** | page format, files, catalog, indexes (maybe later) |

---

## Phases

- ~~Phase 1: Core Storage Engine (v0.1)~~
- Phase 2: Simple Query Language (v0.1)
- Phase 3: Data Types & Schema Management (v0.2)
- Phase 4: Basic Indexing (v0.2)
- Phase 5: INSERT, UPDATE, DELETE (v0.2)
- Phase 6: Page‑Based Storage (v0.3)
- Phase 7: Multi‑Table Queries (JOINs) (v0.4)
- Phase 8: Aggregations & Grouping (v0.4)
- Phase 9: Basic Transactions (v0.5)
- Phase 10: Query Optimization (v0.6)
- Phase 11: Advanced Indexes (v0.7)
- Phase 12: Concurrency Control (v0.7)
- Phase 13: Constraints & Foreign Keys (v0.8)
- Phase 14: Views & Subqueries (v0.8)
- Phase 15: Advanced Features (v0.9+)

---

## Roadmap ideas

- `SELECT` with projections + simple `WHERE` + other DDL and DML commands
- Disk-backed heap file manager
- Simple B-Tree index (stretch goal)
- Minimal transaction log + recovery (stretch goal)

---

## Requirements

- Python ≥ 3.11

---

## Testing

Run 
```
pip install -e .
pip install ruff
```

From the foundrydb folder to add the package to sys.path. This step is necessary before running tests.

At the project root, run:
```
pytest -v
```

You should see something like:
```
tests/test_database.py::test_database_initialization PASSED
tests/test_database.py::test_execute_returns_list PASSED
tests/test_storage.py::test_table_insert_and_persist PASSED
```

Run ruff to do some linting checks
```
ruff check .
ruff format .
```

---

## License

This project is licensed under the MIT License.

See [`LICENSE`](./LICENSE) for details.
