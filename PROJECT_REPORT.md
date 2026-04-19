# AI-Based 3×3 Rubik's Cube Solver — Project Report

**Author:** Soumil Sawant  
**Repository:** [SoumilSawant/AI-based-3x3-rubik-s-cube-solver-](https://github.com/SoumilSawant/AI-based-3x3-rubik-s-cube-solver-)  
**Date:** April 2026  

---

## Table of Contents

| # | Section | Page |
|---|---------|------|
| 1 | [Abstract](#1-abstract) | 3 |
| 2 | [Introduction](#2-introduction) | 3 |
| 3 | [Project Overview](#3-project-overview) | 4 |
| 4 | [Technology Stack](#4-technology-stack) | 5 |
| 5 | [System Architecture](#5-system-architecture) | 6 |
| 6 | [Project Structure](#6-project-structure) | 7 |
| 7 | [Data Structures & Cube Representation](#7-data-structures--cube-representation) | 8 |
| 8 | [Algorithms](#8-algorithms) | 12 |
| 9 | [Application Flow](#9-application-flow) | 17 |
| 10 | [API Documentation](#10-api-documentation) | 20 |
| 11 | [Core Module Walkthrough](#11-core-module-walkthrough) | 22 |
| 12 | [Installation & Usage](#12-installation--usage) | 27 |
| 13 | [Validation & Error Handling](#13-validation--error-handling) | 28 |
| 14 | [Future Improvements](#14-future-improvements) | 29 |
| 15 | [Conclusion](#15-conclusion) | 30 |
| 16 | [References](#16-references) | 31 |

---

## 1. Abstract

This project is a web-based AI-powered 3×3 Rubik's Cube solver built with **Python** and **Flask**. It accepts a cube state described as colored facelets, validates the configuration, and returns an optimal solution using the **Kociemba two-phase algorithm** — one of the most efficient algorithms known for solving the Rubik's Cube.

In addition to the web API, the project includes a fully self-contained, pure-Python cube engine (`local_solver.py`) that models the cube at the **cubie level** (individual piece level), provides a **random scramble generator**, and implements an **IDA\* (Iterative Deepening A\*)** search solver with a corner-twist heuristic.

The system is designed as a RESTful API, making it easy to integrate with any front-end UI or external client.

---

## 2. Introduction

### 2.1 What is a Rubik's Cube?

The 3×3 Rubik's Cube is a classic combinatorial puzzle invented by Ernő Rubik in 1974. It consists of:

- **6 faces**, each with **9 coloured stickers** (54 stickers total)
- **26 visible physical pieces**: 8 corners, 12 edges, and 6 face-centres
- **~43 quintillion** (43,252,003,274,489,856,000) unique configurations
- A **solved state** where each face shows exactly one colour

```
         ┌──────────┐
         │ U  U  U  │
         │ U  U  U  │
         │ U  U  U  │
┌────────┼──────────┼────────┬────────┐
│ L  L  L│ F  F  F  │ R  R  R│ B  B  B│
│ L  L  L│ F  F  F  │ R  R  R│ B  B  B│
│ L  L  L│ F  F  F  │ R  R  R│ B  B  B│
└────────┼──────────┼────────┴────────┘
         │ D  D  D  │
         │ D  D  D  │
         │ D  D  D  │
         └──────────┘

  Face Labels:  U=Up  R=Right  F=Front
                D=Down  L=Left  B=Back
```

### 2.2 Problem Statement

Given a scrambled 3×3 Rubik's Cube configuration (the colour of all 54 stickers), find the sequence of face rotations that returns the cube to the solved state in the fewest possible moves.

### 2.3 Why AI / Search Algorithms?

Solving a Rubik's Cube optimally is a hard combinatorial search problem. Human methods (layer-by-layer, CFOP, etc.) are intuitive but inefficient (50–100 moves). AI/search-based approaches — particularly Kociemba's two-phase algorithm and IDA\* search — can solve any cube configuration in **20 moves or fewer** (God's Number), typically in milliseconds.

---

## 3. Project Overview

### 3.1 Goals

1. Accept any valid 3×3 cube state via a REST API.
2. Validate the input (colours, counts, physical feasibility).
3. Return a short move sequence (solution) using Kociemba.
4. Provide a random scramble generator for testing.
5. Include a self-contained pure-Python solver using IDA\*.

### 3.2 Key Features

| Feature | Description |
|---------|-------------|
| **REST API** | Flask-based endpoints; easily consumed by any UI |
| **Kociemba Solver** | Two-phase optimal solver; solves any state in ≤20 moves |
| **Input Validation** | Checks face count, colour count, center colours, duplicates |
| **Scramble Generator** | Generates a random 20-move scramble with the resulting face state |
| **Pure-Python Cube Engine** | Full CubieCube model: corners, edges, orientations, permutations |
| **IDA\* Solver** | Corner-twist pruning heuristic; threaded with timeout |

### 3.3 High-Level Component Map

```
┌─────────────────────────────────────────────────────────────────┐
│                         Web Client / API Consumer               │
└────────────────────────────┬────────────────────────────────────┘
                             │  HTTP (JSON)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Flask Application (app.py)               │
│  ┌──────────────┐  ┌───────────────────┐  ┌──────────────────┐ │
│  │  GET /        │  │  POST /solve       │  │  GET /scramble   │ │
│  │  (index.html) │  │  (validate + solve)│  │  (generate state)│ │
│  └──────────────┘  └─────────┬─────────┘  └────────┬─────────┘ │
└────────────────────────────────────────────────────┼────────────┘
                             │                        │
                             ▼                        ▼
              ┌──────────────────────┐  ┌─────────────────────────┐
              │  kociemba library    │  │  local_solver.py         │
              │  (C extension)       │  │  CubieCube model         │
              │  Two-phase algorithm │  │  IDA* solver             │
              │  solves in ≤20 moves │  │  generate_scramble()     │
              └──────────────────────┘  └─────────────────────────┘
```

---

## 4. Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Language** | Python | 3.8+ | Application logic |
| **Web Framework** | Flask | ≥3.0.0 | HTTP server & routing |
| **Cube Solver** | kociemba | 1.2.1 | Two-phase optimal solving |
| **Algorithm** | IDA\* (custom) | — | Pure-Python fallback solver |
| **Data Format** | JSON | — | API request/response |
| **Concurrency** | Python `threading` | stdlib | IDA\* timeout enforcement |
| **Collections** | Python `collections.Counter` | stdlib | Input validation |

### 4.1 Why Flask?

Flask is a lightweight WSGI micro-framework ideal for small APIs. It adds minimal overhead, is easy to extend, and pairs cleanly with JSON-based REST endpoints.

### 4.2 Why Kociemba?

The `kociemba` Python package wraps Herbert Kociemba's two-phase algorithm (a C implementation). It finds near-optimal or optimal solutions (God's Number = 20 moves) in milliseconds for any valid cube state — far faster than any pure-Python search.

---

## 5. System Architecture

### 5.1 Layered Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                            │
│          HTTP client / Browser / Any JSON-capable application          │
└─────────────────────────────────┬──────────────────────────────────────┘
                                  │ JSON over HTTP
┌─────────────────────────────────▼──────────────────────────────────────┐
│                           API / ROUTING LAYER                          │
│                           Flask  (app.py)                              │
│   Routes: GET /   POST /solve   GET /scramble                          │
└─────────────┬──────────────────────────────┬───────────────────────────┘
              │                              │
┌─────────────▼──────────┐     ┌────────────▼────────────────────────────┐
│   VALIDATION LAYER     │     │           SERVICE LAYER                 │
│                        │     │                                         │
│ • Face presence check  │     │  kociemba.solve(cube_string)            │
│ • 9 stickers per face  │     │  generate_scramble(num_moves)           │
│ • Unique center colors │     │  cubie_to_facelets(cc)                  │
│ • Each color × 9       │     │                                         │
│ • Unknown color check  │     └────────────┬────────────────────────────┘
└────────────────────────┘                  │
                                            │
┌───────────────────────────────────────────▼───────────────────────────┐
│                          DOMAIN / MODEL LAYER                          │
│                         local_solver.py                                │
│                                                                        │
│   CubieCube   │   18 Basic Moves   │   IDA* Solver   │   Pruning Table │
└────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Request Lifecycle

```
Client                    app.py                 kociemba / local_solver
  │                          │                            │
  │── POST /solve ──────────▶│                            │
  │   {U:[...], R:[...], ..} │                            │
  │                          │── validate faces ──▶       │
  │                          │── build color map ──▶      │
  │                          │── build cube_string ──▶    │
  │                          │── kociemba.solve() ───────▶│
  │                          │◀─ "R U R' U R U2 R'" ──────│
  │◀── {"solution": "..."} ──│                            │
```

---

## 6. Project Structure

```
AI-based-3x3-rubik-s-cube-solver-/
│
├── app.py                 # Flask application, route definitions, validation logic
├── local_solver.py        # Pure-Python cube model, IDA* solver, scramble generator
├── requirements.txt       # Python package dependencies
├── README.md              # Quick-start documentation
└── PROJECT_REPORT.md      # This comprehensive report
```

### 6.1 File Responsibilities

| File | Lines | Responsibility |
|------|-------|----------------|
| `app.py` | 69 | Web server, routes, request parsing, input validation, Kociemba call |
| `local_solver.py` | 311 | CubieCube class, 18-move definitions, pruning table, IDA* search, scramble generator, facelet converter |
| `requirements.txt` | 2 | Dependency pinning (Flask, kociemba) |

---

## 7. Data Structures & Cube Representation

### 7.1 Face & Sticker Indexing

The cube has 6 faces, each with 9 sticker positions numbered **0–8** left-to-right, top-to-bottom:

```
Face layout (positions):
  0 | 1 | 2
  ---------
  3 | 4 | 5      ← position 4 is always the fixed CENTER sticker
  ---------
  6 | 7 | 8
```

Face order used throughout: **U R F D L B** (indices 0–5).

The full cube is represented as a flat array of **54 integers** (or colour strings), concatenated in URFDLB order:

```
Index:  [0–8]   [9–17]   [18–26]   [27–35]   [36–44]   [45–53]
Face:     U        R        F         D         L         B
```

### 7.2 CubieCube Model

Instead of working at the sticker level, the domain model works at the **cubie** (physical piece) level — the standard representation in competitive Rubik's Cube programming.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CubieCube                                    │
│                                                                     │
│  cp[8]  – corner permutation  (which corner piece is in each slot)  │
│  co[8]  – corner orientation  (twist: 0, 1, or 2)                  │
│  ep[12] – edge permutation    (which edge piece is in each slot)    │
│  eo[12] – edge orientation    (flip: 0 or 1)                       │
└─────────────────────────────────────────────────────────────────────┘
```

**Corner slots** (8):

| Index | Label | Sticker positions (face×9+pos) |
|-------|-------|-------------------------------|
| 0 | URF | U8, R0, F2 |
| 1 | UFL | U6, F0, L2 |
| 2 | ULB | U0, L0, B2 |
| 3 | UBR | U2, B0, R2 |
| 4 | DFR | D2, F8, R6 |
| 5 | DLF | D0, L8, F6 |
| 6 | DBL | D6, B8, L6 |
| 7 | DRB | D8, R8, B6 |

**Edge slots** (12):

| Index | Label | Sticker positions |
|-------|-------|------------------|
| 0 | UR | U5, R1 |
| 1 | UF | U7, F1 |
| 2 | UL | U3, L1 |
| 3 | UB | U1, B1 |
| 4 | DR | D5, R7 |
| 5 | DF | D1, F7 |
| 6 | DL | D3, L7 |
| 7 | DB | D7, B7 |
| 8 | FR | F5, R3 |
| 9 | FL | F3, L5 |
| 10 | BL | B5, L3 |
| 11 | BR | B3, R5 |

### 7.3 Corner Orientation Encoding

Each corner has **3 possible orientations** (0, 1, 2). Orientation 0 means the U/D sticker of that corner is on the U or D face. A cube is valid only when `sum(co) % 3 == 0`.

```
Corner Orientation States:
  ┌────────────┬────────────┬────────────┐
  │  ori = 0   │  ori = 1   │  ori = 2   │
  │  (correct) │  (+1 twist)│  (+2 twist)│
  │   [U D]    │   [R L]    │   [F B]    │
  │  face up   │  face up   │  face up   │
  └────────────┴────────────┴────────────┘
```

### 7.4 Edge Orientation Encoding

Each edge has **2 possible orientations** (0 = correct, 1 = flipped). A cube is valid only when `sum(eo) % 2 == 0`.

### 7.5 18 Basic Moves

All cube moves are defined as CubieCube objects that encode the permutation and orientation changes. The 18 moves (6 faces × 3 variants) are:

```
For each face F ∈ {U, R, F, D, L, B}:
  F   = 90° clockwise
  F2  = 180°
  F'  = 90° counter-clockwise (= 3 × clockwise)
```

Move composition uses the `apply(b)` method:

```python
def apply(self, b):
    # Composition: apply move b on top of self
    cp2[i] = self.cp[b.cp[i]]         # corner permutation
    co2[i] = (self.co[b.cp[i]] + b.co[i]) % 3   # corner orientation
    ep2[i] = self.ep[b.ep[i]]         # edge permutation
    eo2[i] = (self.eo[b.ep[i]] + b.eo[i]) % 2   # edge orientation
```

### 7.6 Kociemba String Format

The Kociemba library requires a 54-character string where each character is the **face letter** that sticker belongs to in the solved state. This is derived from the colour → face mapping built from center stickers:

```
Example (solved cube):
UUUUUUUUU RRRRRRRRR FFFFFFFFF DDDDDDDDD LLLLLLLLL BBBBBBBBB
```

---

## 8. Algorithms

### 8.1 Kociemba Two-Phase Algorithm

The `kociemba` library (C extension) implements Herbert Kociemba's **two-phase algorithm**, which is the foundation of most modern speedcubing computers.

#### Phase 1 — Orient All Pieces

Reduce the cube from the full group G₀ (~43 quintillion states) to a subgroup G₁ where:
- All edges are **correctly oriented** (eo = 0 for all)
- All corners are **correctly oriented** (co = 0 for all)
- The UD-slice edges (FR, FL, BL, BR) are in the UD slice

```
G₀ (all 43 quintillion states)
        │
        │ Phase 1: orient + bring slice edges to slice
        ▼
G₁ (subgroup, ~2 billion states)
```

#### Phase 2 — Solve Within G₁

From the G₁ state, solve using only moves that **stay in G₁**:
`{U, U2, U', D, D2, D', R2, L2, F2, B2}`

```
G₁ (~2 billion states)
        │
        │ Phase 2: permute without leaving G₁
        ▼
Identity (solved)
```

#### Complexity

| Metric | Value |
|--------|-------|
| Max solution length | 20 moves (God's Number) |
| Average solution | ~19 moves |
| Time to solve | < 1 ms (C implementation) |
| State space explored | Millions, not quintillions |

### 8.2 IDA\* Search (local_solver.py)

The pure-Python IDA\* solver is an alternative approach. It is included for educational value and as a potential fallback.

#### How IDA\* Works

IDA\* (Iterative Deepening A\*) is a best-first search that uses depth-first traversal with a **cost bound** (like IDDFS) combined with a **heuristic** to prune branches that can't possibly lead to a solution within the bound.

```
Algorithm IDA*(start):
  bound ← heuristic(start)
  path  ← [start]
  loop:
    result ← SEARCH(path, g=0, bound)
    if result == FOUND: return path
    if result == ∞: return NOT_FOUND
    bound ← result

Function SEARCH(path, g, bound):
  node ← last element of path
  f ← g + heuristic(node)
  if f > bound: return f
  if is_solved(node): return FOUND
  minimum ← ∞
  for each move m:
    if move is not redundant:
      child ← apply(node, m)
      path.append(child)
      result ← SEARCH(path, g+1, bound)
      if result == FOUND: return FOUND
      if result < minimum: minimum ← result
      path.pop()
  return minimum
```

#### IDA\* Flowchart

```
                    ┌──────────────────────┐
                    │   Start: IDA* solve  │
                    │   bound = h(start)   │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   SEARCH(path,g,     │◀────────────────────┐
                    │         bound)       │                     │
                    └──────────┬───────────┘                     │
                               │                                 │
              ┌────────────────▼──────────────┐                  │
              │  f = g + h(current node)      │                  │
              └──────┬─────────────┬──────────┘                  │
                     │             │                             │
               f > bound      f ≤ bound                         │
                     │             │                             │
                     ▼             ▼                             │
               return f     is_solved()?                        │
                              │       │                          │
                            yes       no                         │
                              │       │                          │
                              ▼       ▼                          │
                           FOUND   for each move:               │
                                   apply move →                 │
                                   recurse ────────────────────▶│
                                   if FOUND: return FOUND
                                   update minimum
                                   return minimum
```

#### Corner-Twist Pruning Table

The heuristic used is a precomputed **twist distance table**:
- 2187 entries (= 3⁷, the number of distinct corner-orientation states for 7 of the 8 corners)
- Built at startup using BFS from the solved state
- `h(cube) = dist_table[cube.get_twist()]`

```
Twist table construction (BFS):
  dist[0] = 0          (solved twist state)
  queue = [solved_cube]
  while queue not empty:
    for each cube in queue:
      for each of 18 moves:
        if new_twist not visited:
          dist[new_twist] = dist[current_twist] + 1
          add to next_queue
```

#### IDA\* Redundancy Pruning

To avoid redundant move sequences (e.g., U followed by U', or U followed by D followed by U), consecutive moves on the **same face** or **opposite faces** in suboptimal order are skipped:

```python
if face == last_face: continue                        # e.g. U then U
if _OPPOSITE[last_face] == face and face < last_face: continue  # e.g. U then D then U
```

### 8.3 Algorithm Comparison

| Property | Kociemba (Phase 1+2) | IDA\* (local) |
|----------|---------------------|---------------|
| Implementation | C extension | Pure Python |
| Speed | < 1 ms | Seconds–minutes |
| Solution length | ≤ 20 moves | ≤ 25 moves (configurable) |
| Memory | ~MB (tables) | Low |
| Heuristic | Multi-coordinate | Corner twist only |
| Completeness | Yes | Yes (within depth) |
| Use in `/solve` | ✅ Primary solver | ❌ Not used (available) |
| Use in `/scramble` | ❌ Not needed | ✅ Generates cube state |

---

## 9. Application Flow

### 9.1 Overall System Flowchart

```
                         ┌──────────────────┐
                         │  Flask App Start  │
                         │  local_solver.py  │
                         │  builds pruning   │
                         │  table on import  │
                         └────────┬─────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │   Incoming HTTP Request      │
                    └──┬───────────┬──────────────┘
                       │           │
              ┌────────▼──┐   ┌────▼──────────┐
              │ POST/solve │   │ GET /scramble  │
              └────┬───────┘   └────────┬──────┘
                   │                    │
      ┌────────────▼────────┐  ┌────────▼────────────┐
      │  Parse JSON body    │  │  generate_scramble() │
      └────────┬────────────┘  │  (20 random moves)   │
               │               └────────┬────────────┘
      ┌────────▼────────────┐  ┌────────▼────────────┐
      │ Validate 6 faces,   │  │ cubie_to_facelets()  │
      │ 9 stickers each     │  │ convert to colors   │
      └────────┬────────────┘  └────────┬────────────┘
               │                        │
      ┌────────▼────────────┐  ┌────────▼────────────┐
      │ Build color→letter  │  │  Return JSON:        │
      │ map from centers    │  │  {faces, scramble}   │
      └────────┬────────────┘  └─────────────────────┘
               │
      ┌────────▼────────────┐
      │ Validate each color │
      │ is known & appears  │
      │ exactly 9 times     │
      └────────┬────────────┘
               │
      ┌────────▼────────────┐
      │  Build 54-char      │
      │  Kociemba string    │
      └────────┬────────────┘
               │
      ┌────────▼────────────┐
      │  kociemba.solve()   │
      └────────┬────────────┘
       ┌───────┴─────────┐
    success           exception
       │                   │
  ┌────▼────┐         ┌────▼──────────────────┐
  │ 200 OK  │         │ 400 Bad Request        │
  │solution │         │ "Invalid cube config." │
  └─────────┘         └────────────────────────┘
```

### 9.2 Scramble Generation Flow

```
generate_scramble(num_moves=20)
        │
        ▼
┌───────────────────────┐
│  Start: solved cube   │
│  cc = CubieCube()     │
│  moves_applied = []   │
│  last_face = None     │
└──────────┬────────────┘
           │
     ┌─────▼──────────────────────────────────┐
     │  for _ in range(num_moves):            │
     │                                        │
     │    Filter _MOVE_LIST:                  │
     │      exclude same face as last         │
     │      exclude opposite face in order    │
     │                                        │
     │    Pick random (name, mv)              │
     │    cc = cc.apply(mv)                   │
     │    moves_applied.append(name)          │
     │    last_face = name[0]                 │
     └─────┬──────────────────────────────────┘
           │  (repeated num_moves times)
           ▼
     return (cc, moves_applied)
           │
           ▼
     cubie_to_facelets(cc)
           │
           ▼
     {face: [9 color strings], ...}
```

### 9.3 Input Validation Flow

```
  Receive JSON body
         │
         ▼
  ┌──────────────────────────────┐
  │  For each face in URFDLB:   │
  │    face present in data?    │──── NO ──▶ 400: "Missing face X"
  │    len(data[face]) == 9?    │──── NO ──▶ 400: "Incomplete face X"
  └──────────────┬───────────────┘
                 │ YES (all 6 faces OK)
                 ▼
  ┌──────────────────────────────┐
  │  For each face, read center  │
  │  (index 4) as color.         │
  │  center_color in map?        │──── YES ──▶ 400: "Duplicate center color"
  │  Add to color_to_letter map  │
  └──────────────┬───────────────┘
                 │
                 ▼
  ┌──────────────────────────────┐
  │  len(color_to_letter) == 6? │──── NO ──▶ 400: "Centers not unique"
  └──────────────┬───────────────┘
                 │
                 ▼
  ┌──────────────────────────────┐
  │  For each sticker color:     │
  │    color in color_to_letter? │──── NO ──▶ 400: "Unknown color"
  └──────────────┬───────────────┘
                 │
                 ▼
  ┌──────────────────────────────┐
  │  Counter(facelets):          │
  │  each color count == 9?      │──── NO ──▶ 400: "Color appears N times"
  └──────────────┬───────────────┘
                 │ VALID
                 ▼
  Build Kociemba string → solve
```

### 9.4 Cubie ↔ Facelet Conversion Flow

```
Facelet array (54 colours)               CubieCube
         │                                    │
         │ facelet_to_cubie()                 │ cubie_to_facelets()
         ▼                                    ▼
  1. Map each colour string             1. Place center colours
     to face index (0-5)                   at f*9+4 for each face
         │                                    │
  2. For each of 8 corner slots:        2. For each corner slot i:
     Read 3 sticker colours                piece c = cp[i]
     Find matching solved corner           orient o = co[i]
     Record cp[i] & co[i]                 arr[CF[i][j]] = color
         │                                    of CF[c][(j+o)%3]
  3. For each of 12 edge slots:         3. For each edge slot i:
     Read 2 sticker colours                piece e = ep[i]
     Find matching solved edge             orient o = eo[i]
     Record ep[i] & eo[i]                 arr[EF[i][j]] = color
         │                                    of EF[e][(j+o)%2]
         ▼                                    ▼
     CubieCube object               {face: [9 colours], ...}
```

---

## 10. API Documentation

### 10.1 `GET /`

Returns the main HTML page (template `index.html`).

**Response:** `200 OK` — HTML page

---

### 10.2 `POST /solve`

Solve a given Rubik's Cube configuration.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "U": ["white","white","white","white","white","white","white","white","white"],
  "R": ["red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red" ],
  "F": ["green","green","green","green","green","green","green","green","green"],
  "D": ["yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow"],
  "L": ["orange","orange","orange","orange","orange","orange","orange","orange","orange"],
  "B": ["blue", "blue", "blue", "blue", "blue", "blue", "blue", "blue", "blue" ]
}
```

Each face is an array of **9 colour strings** in left-to-right, top-to-bottom order.

**Successful Response (200 OK):**
```json
{ "solution": "R U R' U R U2 R'" }
```

The solution is a space-separated sequence of **standard Rubik's Cube notation**:
- `U`, `R`, `F`, `D`, `L`, `B` = 90° clockwise
- `U'`, `R'`, etc. = 90° counter-clockwise
- `U2`, `R2`, etc. = 180°

**Error Responses (400 Bad Request):**

| Condition | Error Message |
|-----------|--------------|
| No JSON body | `"No data received."` |
| Missing/incomplete face | `"Missing or incomplete data for face X."` |
| Duplicate center colours | `"Two faces share the same center color."` |
| Centers not unique | `"Centers must all be different colors."` |
| Unknown sticker colour | `"Unknown color 'X'. Only use the 6 standard colors."` |
| Colour count ≠ 9 | `"Color 'X' appears N times — must be exactly 9."` |
| Physically impossible | `"Invalid cube configuration. Please check your colors."` |

---

### 10.3 `GET /scramble`

Generate a random 20-move scramble and return the resulting face state.

**Response (200 OK):**
```json
{
  "faces": {
    "U": ["white","orange","white","white","white","blue","yellow","white","red"],
    "R": ["blue","red","white","red","red","green","red","red","orange"],
    "F": ["red","green","orange","green","green","white","green","yellow","green"],
    "D": ["yellow","yellow","green","yellow","yellow","yellow","orange","yellow","yellow"],
    "L": ["orange","orange","yellow","orange","orange","red","orange","blue","orange"],
    "B": ["blue","blue","blue","white","blue","blue","blue","green","white"]
  },
  "scramble": "R U F2 L' B D2 R' U' F L2 B' D R2 U F' D' L B2 U'"
}
```

---

### 10.4 API Error Codes Summary

| HTTP Status | Meaning |
|------------|---------|
| 200 | Success |
| 400 | Bad Request — validation failed or cube unsolvable |
| 500 | Internal Server Error (unexpected exception) |

---

## 11. Core Module Walkthrough

### 11.1 `app.py` — Flask Application

```
app.py
  │
  ├── Imports
  │   ├── flask: Flask, render_template, request, jsonify
  │   ├── kociemba: the C-extension solver
  │   └── local_solver: generate_scramble, cubie_to_facelets
  │
  ├── FACE_ORDER = ['U','R','F','D','L','B']
  │   └── Canonical face order used throughout
  │
  ├── GET /  →  index()
  │   └── Returns templates/index.html
  │
  ├── POST /solve  →  solve_cube()
  │   ├── Parse JSON body
  │   ├── Validate each face (present, 9 stickers)
  │   ├── Build flat 54-element facelet list
  │   ├── Build color→face-letter map from centers
  │   ├── Validate all sticker colors (known, each ×9)
  │   ├── Build 54-char Kociemba string
  │   └── Call kociemba.solve() → return solution
  │
  └── GET /scramble  →  scramble_cube()
      ├── generate_scramble(num_moves=20)  → (cc, moves)
      ├── cubie_to_facelets(cc)            → face dict
      └── Return {faces, scramble}
```

### 11.2 `local_solver.py` — Cube Engine

```
local_solver.py
  │
  ├── Corner / Edge index constants
  │   ├── URF,UFL,ULB,UBR,DFR,DLF,DBL,DRB = range(8)
  │   └── UR,UF,UL,UB,DR,DF,DL,DB,FR,FL,BL,BR = range(12)
  │
  ├── Facelet position tables
  │   ├── CF[8][3]  – corner facelet indices (face*9+pos)
  │   └── EF[12][2] – edge facelet indices
  │
  ├── CubieCube class
  │   ├── __slots__ = ('cp','co','ep','eo')
  │   ├── copy()         – deep copy
  │   ├── apply(b)       – compose two cubes
  │   ├── get_twist()    – corner orientation coordinate (0–2186)
  │   ├── get_flip()     – edge orientation coordinate (0–2047)
  │   ├── corner_parity() – permutation parity of corners
  │   ├── edge_parity()   – permutation parity of edges
  │   └── verify()        – check cube validity
  │
  ├── _MOVES_RAW dict
  │   └── 6 face moves defined as (cp, co, ep, eo) tuples
  │
  ├── _MOVE_LIST  – 18 CubieCube moves (F, F2, F', etc.)
  │
  ├── facelet_to_cubie(facelets, color_to_face)
  │   └── Convert 54-colour list → CubieCube
  │
  ├── _build_twist_table()
  │   └── BFS to compute h(twist) for all 2187 corner-twist states
  │
  ├── _TWIST_DIST[2187]  – precomputed at import time
  │
  ├── IDA* Solver
  │   ├── _is_solved(cc)   – check if cube is solved
  │   ├── _heuristic(cc)   – look up twist distance
  │   ├── _search(...)     – recursive DFS with bound
  │   └── solve(cc, ...)   – entry point with threading timeout
  │
  ├── cubie_to_facelets(cc)
  │   └── Convert CubieCube → {face: [9 colour strings]}
  │
  └── generate_scramble(num_moves=20)
      └── Apply random moves to solved cube, return (cc, moves)
```

### 11.3 Move Composition Detail

The `apply` method implements **right-composition** of cube transformations:

```
For result = self.apply(b):

  Corner permutation:
    result.cp[i] = self.cp[b.cp[i]]
    # "b first moves piece b.cp[i] to slot i;
    #  self then acts on whatever was in slot b.cp[i]"

  Corner orientation (mod 3):
    result.co[i] = (self.co[b.cp[i]] + b.co[i]) % 3

  Edge permutation:
    result.ep[i] = self.ep[b.ep[i]]

  Edge orientation (mod 2):
    result.eo[i] = (self.eo[b.ep[i]] + b.eo[i]) % 2
```

### 11.4 Pruning Table Construction

```python
def _build_twist_table():
    dist = [-1] * 2187      # 3^7 possible twist values
    dist[0] = 0             # solved state has twist = 0
    queue = [CubieCube()]   # start from solved cube

    while queue:
        nxt = []
        for cur in queue:
            t = cur.get_twist()
            for _, mv in _MOVE_LIST:        # try all 18 moves
                nb = cur.apply(mv)
                nt = nb.get_twist()
                if dist[nt] == -1:          # not yet visited
                    dist[nt] = dist[t] + 1
                    nxt.append(nb)
        queue = nxt
    return dist
```

The table is built **once at module import** (taking a fraction of a second) and reused for all solve requests.

---

## 12. Installation & Usage

### 12.1 Prerequisites

- Python 3.8 or higher
- pip

### 12.2 Installation

```bash
# 1. Clone the repository
git clone https://github.com/SoumilSawant/AI-based-3x3-rubik-s-cube-solver-.git
cd AI-based-3x3-rubik-s-cube-solver-

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate.bat     # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### 12.3 Running the Server

```bash
python app.py
```

Output:
```
Building pruning table... done.
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 12.4 Example API Call (curl)

**Solve a scrambled cube:**
```bash
curl -X POST http://localhost:5000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "U":["white","white","white","white","white","white","white","white","white"],
    "R":["red","red","red","red","red","red","red","red","red"],
    "F":["green","green","green","green","green","green","green","green","green"],
    "D":["yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow"],
    "L":["orange","orange","orange","orange","orange","orange","orange","orange","orange"],
    "B":["blue","blue","blue","blue","blue","blue","blue","blue","blue"]
  }'
```

Response:
```json
{"solution": ""}
```
*(Empty — cube is already solved)*

**Get a random scramble:**
```bash
curl http://localhost:5000/scramble
```

### 12.5 Dependencies

```
Flask>=3.0.0
kociemba==1.2.1
```

---

## 13. Validation & Error Handling

### 13.1 Validation Checks (in order)

1. **Body exists** — JSON body must be present.
2. **All 6 faces present** — Keys U, R, F, D, L, B must all exist.
3. **Face length** — Each face array must have exactly 9 elements.
4. **Unique centers** — The center sticker (index 4) of each face must be a distinct colour.
5. **6 unique centres** — Exactly 6 distinct centre colours.
6. **Known colours** — Every sticker colour must be one of the 6 centre colours.
7. **Count invariant** — Each colour must appear exactly 9 times.
8. **Physical validity** — Kociemba raises an exception for physically impossible states (e.g., wrong parity, impossible edge flip).

### 13.2 Error Response Format

All errors follow a consistent JSON envelope:
```json
{ "error": "Human-readable error message." }
```

### 13.3 Exception Handling

```python
try:
    solution = kociemba.solve(cube_string)
    return jsonify({'solution': solution})
except Exception as e:
    return jsonify({'error': 'Invalid cube configuration. Please check your colors.'}), 400
```

The `kociemba` library raises an exception for any cube state it determines to be physically invalid (parity error, impossible orientation sum, etc.) that passed the basic colour-count checks.

---

## 14. Future Improvements

### 14.1 Front-End UI

- **Interactive facelet grid** — Allow users to click on each of the 54 stickers and select its colour visually.
- **3D cube renderer** — Use Three.js or a similar library to render an animated cube.
- **Move animation** — Show the solution being applied step by step.

### 14.2 Camera-Based Input

- **OpenCV integration** — Capture each face of the cube using a webcam.
- **Colour detection** — Use HSV thresholding or a trained classifier to detect sticker colours from camera frames.
- **Automatic face scanning** — Guide the user to present each face, then auto-extract the colour grid.

### 14.3 Solver Improvements

- **IDA\* as a fallback** — Use `local_solver.solve()` when `kociemba` fails or is unavailable.
- **Better heuristics** — Add edge-flip and combined corner+edge tables to the IDA\* solver for faster search.
- **Korf's optimal solver** — Add a fully optimal solver using the large pattern database approach.

### 14.4 API Enhancements

- **CORS support** — Add Flask-CORS to allow browser-based front-ends from different origins.
- **Move-by-move solution** — Return the solution as an array of individual moves rather than a single string, for easier animation.
- **Solve from Kociemba string** — Accept the 54-character Kociemba notation directly as an alternative input.
- **Solution length header** — Include move count in the response.

### 14.5 Deployment

- **Docker** — Containerise the application for portable deployment.
- **Gunicorn / uWSGI** — Run with a production WSGI server instead of Flask's development server.
- **CI/CD** — Add GitHub Actions to run tests and deploy on push.

---

## 15. Conclusion

This project successfully implements an AI-powered 3×3 Rubik's Cube solver as a clean REST API. The key achievements are:

1. **Complete REST API** — The Flask application provides a clean, well-validated `/solve` and `/scramble` interface consumable by any client.

2. **Optimal solving** — By integrating the Kociemba two-phase algorithm (via a C extension), the solver finds solutions in ≤ 20 moves for any valid cube state in under a millisecond.

3. **Rich local cube engine** — The `local_solver.py` module is a complete, self-contained Rubik's Cube framework: cubie-level state representation, all 18 basic moves, a precomputed pruning table, a full IDA\* search solver, and bidirectional facelet ↔ cubie conversion.

4. **Robust input validation** — The API validates all seven layers of correctness before attempting to solve, providing meaningful error messages for every failure mode.

5. **Educational value** — The project demonstrates several important computer science concepts: combinatorial search, heuristic functions, state-space reduction, group theory (G₀ → G₁), and concurrent programming (threaded IDA\* with timeout).

The codebase is minimal (< 400 lines), clean, and well-structured — making it an excellent foundation for the future improvements described above, particularly a visual front-end and camera-based colour detection.

---

## 16. References

1. **Kociemba, H.** (1992). *Two-Phase-Algorithm for solving a Rubik's Cube.*  
   http://kociemba.org/cube.htm

2. **God's Number is 20** — Rokicki, T. et al. (2010).  
   https://www.cube20.org/

3. **Korf, R.E.** (1985). *Depth-first Iterative-Deepening: An Optimal Admissible Tree Search.*  
   Artificial Intelligence, 27(1):97–109.

4. **kociemba Python package** — PyPI: https://pypi.org/project/kociemba/

5. **Flask Documentation** — https://flask.palletsprojects.com/

6. **Rubik's Cube notation** — World Cube Association:  
   https://www.worldcubeassociation.org/regulations/#article-12-notation

7. **CubieCube representation** — Rokicki, T. *Cube Explorer* documentation.  
   http://kociemba.org/cubexplorer.htm

---

*End of Report*

---

> **Document version:** 1.0  
> **Generated for:** AI-based 3×3 Rubik's Cube Solver  
> **Author:** Soumil Sawant | GitHub: [SoumilSawant](https://github.com/SoumilSawant)
