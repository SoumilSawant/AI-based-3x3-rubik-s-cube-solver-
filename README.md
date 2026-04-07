# AI-based 3x3 Rubik’s Cube Solver

A web-based 3x3 Rubik’s Cube solver built with **Flask**. The app accepts a cube state (colors on each face), validates the input, and returns a solution using the **Kociemba** two-phase algorithm. It also includes a local pure‑Python cube representation and scramble generator.

---

## ✨ Features

- **Solve any valid 3x3 cube state** via the Kociemba solver.
- **Random scramble generator** for testing.
- Input validation (colors, counts, centers, etc.).
- Clean API endpoints for easy UI or API integration.

---

## 🧠 How It Works

### 1. Input Format (URFDLB)
The solver expects the cube in **URFDLB** face order:

- **U** = Up  
- **R** = Right  
- **F** = Front  
- **D** = Down  
- **L** = Left  
- **B** = Back  

Each face contains **9 stickers**, provided as color strings (e.g., `"white"`).

### 2. Color Mapping
The solver builds the **color → face mapping** using the **center sticker** of each face (index 4).  
That means **center colors define the cube’s orientation**.

### 3. Solving
Once validated, the cube is converted into the 54‑character Kociemba string (URFDLB notation) and solved using the `kociemba` library.

### 4. Scrambling
The `local_solver.py` file includes a **pure‑Python CubieCube model**, a random scramble generator, and a full IDA* solver (currently not used by the Flask route, but available).

---

## 📦 Requirements

```
Flask>=3.0.0
kociemba==1.2.1
```

Install with:

```bash
pip install -r requirements.txt
```

---

## 🚀 Run the App

```bash
python app.py
```

The server starts at:

```
http://localhost:5000
```

---

## 🔌 API Endpoints

### `POST /solve`
Solve a cube state.

**Request Body (JSON):**
```json
{
  "U": ["white","white","white","white","white","white","white","white","white"],
  "R": ["red","red","red","red","red","red","red","red","red"],
  "F": ["green","green","green","green","green","green","green","green","green"],
  "D": ["yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow"],
  "L": ["orange","orange","orange","orange","orange","orange","orange","orange","orange"],
  "B": ["blue","blue","blue","blue","blue","blue","blue","blue","blue"]
}
```

**Response:**
```json
{ "solution": "R U R' U R U2 R'" }
```

### `GET /scramble`
Returns a random scramble and face colors.

**Response:**
```json
{
  "faces": {
    "U": [...],
    "R": [...],
    "F": [...],
    "D": [...],
    "L": [...],
    "B": [...]
  },
  "scramble": "R U R' F2 ..."
}
```

---

## 📂 Project Structure

```
.
├── app.py              # Flask web app + API endpoints
├── local_solver.py     # CubieCube model, scramble generator, IDA* solver
├── requirements.txt
└── README.md
```

---

## ⚠️ Notes

- The app uses **Kociemba** for solving (fast and optimal).
- The local solver (`local_solver.py`) includes an IDA* search solver but is **not currently called** in `/solve`.
- Importing `local_solver.py` builds a pruning table on startup, which may take a few seconds.

---

## ✅ Future Improvements (Optional Ideas)

- Add a front‑end UI (facelet grid input).
- Support camera-based color detection.
- Use local Python solver as a fallback when Kociemba fails.

---

## 👤 Author

**Soumil Sawant**  
GitHub: [SoumilSawant](https://github.com/SoumilSawant)
