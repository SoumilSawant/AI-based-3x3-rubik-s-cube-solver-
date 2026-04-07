import random
import threading
"""
Pure-Python Rubik's Cube Solver
Uses IDA* search with a corner-twist pruning heuristic.
No C extensions required.
"""

# ── Corner / Edge indices ─────────────────────────────────────────────────────
URF,UFL,ULB,UBR,DFR,DLF,DBL,DRB = range(8)
UR,UF,UL,UB,DR,DF,DL,DB,FR,FL,BL,BR = range(12)

# ── Facelet positions for each cubie ─────────────────────────────────────────
# Faces: U=0 R=1 F=2 D=3 L=4 B=5   (each face: 9 facelets, 0-8 left-to-right top-to-bottom)
CF = [  # corner facelets [face*9+pos]
    [0*9+8, 1*9+0, 2*9+2],  # URF
    [0*9+6, 2*9+0, 4*9+2],  # UFL
    [0*9+0, 4*9+0, 5*9+2],  # ULB
    [0*9+2, 5*9+0, 1*9+2],  # UBR
    [3*9+2, 2*9+8, 1*9+6],  # DFR
    [3*9+0, 4*9+8, 2*9+6],  # DLF
    [3*9+6, 5*9+8, 4*9+6],  # DBL
    [3*9+8, 1*9+8, 5*9+6],  # DRB
]
EF = [  # edge facelets
    [0*9+5, 1*9+1],  # UR
    [0*9+7, 2*9+1],  # UF
    [0*9+3, 4*9+1],  # UL
    [0*9+1, 5*9+1],  # UB
    [3*9+5, 1*9+7],  # DR
    [3*9+1, 2*9+7],  # DF
    [3*9+3, 4*9+7],  # DL
    [3*9+7, 5*9+7],  # DB
    [2*9+5, 1*9+3],  # FR
    [2*9+3, 4*9+5],  # FL
    [5*9+5, 4*9+3],  # BL
    [5*9+3, 1*9+5],  # BR
]

# ── CubieCube ─────────────────────────────────────────────────────────────────
class CubieCube:
    __slots__ = ('cp','co','ep','eo')
    def __init__(self, cp=None, co=None, ep=None, eo=None):
        self.cp = list(cp) if cp else list(range(8))
        self.co = list(co) if co else [0]*8
        self.ep = list(ep) if ep else list(range(12))
        self.eo = list(eo) if eo else [0]*12

    def copy(self):
        return CubieCube(self.cp, self.co, self.ep, self.eo)

    def apply(self, b):
        cp2=[0]*8; co2=[0]*8
        for i in range(8):
            cp2[i] = self.cp[b.cp[i]]
            co2[i] = (self.co[b.cp[i]] + b.co[i]) % 3
        ep2=[0]*12; eo2=[0]*12
        for i in range(12):
            ep2[i] = self.ep[b.ep[i]]
            eo2[i] = (self.eo[b.ep[i]] + b.eo[i]) % 2
        return CubieCube(cp2, co2, ep2, eo2)

    def get_twist(self):
        r=0
        for i in range(URF, DRB): r=3*r+self.co[i]
        return r

    def get_flip(self):
        r=0
        for i in range(UR, BR): r=2*r+self.eo[i]
        return r

    def corner_parity(self):
        s=0
        for i in range(DRB,URF,-1):
            for j in range(i-1,URF-1,-1):
                if self.cp[j]>self.cp[i]: s+=1
        return s%2

    def edge_parity(self):
        s=0
        for i in range(BR,UR,-1):
            for j in range(i-1,UR-1,-1):
                if self.ep[j]>self.ep[i]: s+=1
        return s%2

    def verify(self):
        if sorted(self.cp)!=list(range(8)): return "Corner permutation invalid."
        if sorted(self.ep)!=list(range(12)): return "Edge permutation invalid."
        if sum(self.co)%3!=0: return "Corner orientation sum is not 0 mod 3."
        if sum(self.eo)%2!=0: return "Edge orientation sum is not 0 mod 2."
        if self.corner_parity()!=self.edge_parity(): return "Parity error (impossible cube)."
        return None

# ── 18 basic moves (cubie-level) ─────────────────────────────────────────────
_MOVES_RAW = {
'U': ([UBR,URF,UFL,ULB,DFR,DLF,DBL,DRB],[0]*8,
      [UB,UR,UF,UL,DR,DF,DL,DB,FR,FL,BL,BR],[0]*12),
'R': ([DFR,UFL,ULB,URF,DRB,DLF,DBL,UBR],[2,0,0,1,1,0,0,2],
      [FR,UF,UL,UB,BR,DF,DL,DB,DR,FL,BL,UR],[0]*12),
'F': ([UFL,DLF,ULB,UBR,URF,DFR,DBL,DRB],[1,2,0,0,2,1,0,0],
      [UR,FL,UL,UB,DR,FR,DL,DB,UF,DF,BL,BR],[0,1,0,0,0,1,0,0,1,1,0,0]),
'D': ([URF,UFL,ULB,UBR,DLF,DBL,DRB,DFR],[0]*8,
      [UR,UF,UL,UB,DF,DL,DB,DR,FR,FL,BL,BR],[0]*12),
'L': ([URF,ULB,DBL,UBR,DFR,UFL,DLF,DRB],[0,1,2,0,0,2,1,0],
      [UR,UF,BL,UB,DR,DF,FL,DB,FR,UL,DL,BR],[0]*12),
'B': ([URF,UFL,UBR,DRB,DFR,DLF,ULB,DBL],[0,0,1,2,0,0,2,1],
      [UR,UF,UL,BR,DR,DF,DL,BL,FR,FL,UB,DB],[0,0,0,1,0,0,0,1,0,0,1,1]),
}

_MOVE_LIST = []   # list of (name, CubieCube)
for _face, (cp,co,ep,eo) in _MOVES_RAW.items():
    _m = CubieCube(cp,co,ep,eo)
    _m2= _m.apply(_m)
    _m3= _m2.apply(_m)
    _MOVE_LIST += [(_face,_m),(_face+"2",_m2),(_face+"'",_m3)]

# ── Facelet → CubieCube ───────────────────────────────────────────────────────
# Maps color name → face index (U=0 R=1 F=2 D=3 L=4 B=5)
_CENTER_IDX = {f*9+4: f for f in range(6)}

def facelet_to_cubie(facelets: list, color_to_face: dict) -> CubieCube:
    """
    facelets: list of 54 color strings in URFDLB face order.
    color_to_face: dict mapping color → face index (0-5).
    """
    arr = [color_to_face[c] for c in facelets]   # 54 ints 0-5

    # Corner cubies
    cp=[0]*8; co=[0]*8
    for i,(f0,f1,f2) in enumerate(CF):
        col=(arr[f0],arr[f1],arr[f2])
        # find which corner and orientation
        found=False
        for c,(g0,g1,g2) in enumerate(CF):
            ref=(g0//9, g1//9, g2//9)   # face indices of solved corner
            for ori in range(3):
                rotated=(col[ori%3],col[(ori+1)%3],col[(ori+2)%3])
                if rotated == ref:
                    cp[i]=c; co[i]=ori; found=True; break
            if found: break
        if not found:
            raise ValueError("Invalid corner cubie.")

    # Edge cubies
    ep=[0]*12; eo=[0]*12
    for i,(f0,f1) in enumerate(EF):
        col=(arr[f0],arr[f1])
        found=False
        for e,(g0,g1) in enumerate(EF):
            ref=(g0//9, g1//9)
            for ori in range(2):
                rotated=(col[ori%2],col[(ori+1)%2])
                if rotated==ref:
                    ep[i]=e; eo[i]=ori; found=True; break
            if found: break
        if not found:
            raise ValueError("Invalid edge cubie.")

    return CubieCube(cp,co,ep,eo)

# ── Pruning table: corner twist ───────────────────────────────────────────────
def _build_twist_table():
    dist = [-1]*2187
    dist[0] = 0
    queue = [CubieCube()]
    while queue:
        nxt=[]
        for cur in queue:
            t = cur.get_twist()
            for _,mv in _MOVE_LIST:
                nb = cur.apply(mv)
                nt = nb.get_twist()
                if dist[nt]==-1:
                    dist[nt]=dist[t]+1
                    nxt.append(nb)
        queue=nxt
    return dist

print("Building pruning table...", end=" ", flush=True)
_TWIST_DIST = _build_twist_table()
print("done.")

# ── IDA* solver ───────────────────────────────────────────────────────────────
_SOLVED_TWIST = 0
_SOLVED_FLIP  = 0

def _is_solved(cc: CubieCube) -> bool:
    return (cc.cp==list(range(8)) and cc.co==[0]*8
            and cc.ep==list(range(12)) and cc.eo==[0]*12)

def _heuristic(cc: CubieCube) -> int:
    return _TWIST_DIST[cc.get_twist()]

# Avoid redundant moves: last face → forbidden next faces
_OPPOSITE = {'U':'D','D':'U','R':'L','L':'R','F':'B','B':'F'}

def _search(path, cc, g, bound, last_face):
    h = _heuristic(cc)
    f = g + h
    if f > bound: return f
    if h == 0 and _is_solved(cc): return -1   # found
    minimum = float('inf')
    for name, mv in _MOVE_LIST:
        face = name[0]
        if face == last_face: continue
        if last_face and _OPPOSITE.get(last_face)==face and face<last_face: continue
        nb = cc.apply(mv)
        path.append(name)
        t = _search(path, nb, g+1, bound, face)
        if t == -1: return -1
        if t < minimum: minimum = t
        path.pop()
    return minimum

def solve(cc: CubieCube, max_depth=25, timeout_seconds=12) -> str:
    err = cc.verify()
    if err:
        raise ValueError(err)
    if _is_solved(cc):
        return "(already solved)"
    bound = _heuristic(cc)
    path = []
    result = [None]   # shared across thread
    timed_out = [False]

    def _run():
        nonlocal bound, path
        while bound <= max_depth:
            t = _search(path, cc, 0, bound, None)
            if t == -1:
                result[0] = ' '.join(path)
                return
            if t == float('inf'):
                result[0] = None
                return
            bound = t
        result[0] = None

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    thread.join(timeout=timeout_seconds)

    if thread.is_alive():
        timed_out[0] = True
        raise ValueError(
            f"Solver timed out after {timeout_seconds}s. "
            "The scramble is too complex for the pure-Python solver. "
            "Try the Random Scramble button to get a fresh (simpler) state."
        )
    if result[0] is None:
        raise ValueError("No solution found within depth limit.")
    return result[0]

# ── Cubie → Facelets (reverse mapping) ───────────────────────────────────────
# Canonical color for each face index (U R F D L B)
FACE_INDEX_TO_COLOR = ['white', 'red', 'green', 'yellow', 'orange', 'blue']
FACE_NAMES          = ['U', 'R', 'F', 'D', 'L', 'B']

def cubie_to_facelets(cc: CubieCube) -> dict:
    """
    Convert a CubieCube to a dict of {face: [9 color strings]}.
    Face order: U R F D L B.
    """
    arr = [None] * 54

    # Centers are always at their solved face
    for f in range(6):
        arr[f * 9 + 4] = FACE_INDEX_TO_COLOR[f]

    # Corners: slot i holds piece cc.cp[i] with orientation cc.co[i]
    for i in range(8):
        c = cc.cp[i]
        o = cc.co[i]
        for j in range(3):
            arr[CF[i][j]] = FACE_INDEX_TO_COLOR[CF[c][(j + o) % 3] // 9]

    # Edges: slot i holds piece cc.ep[i] with orientation cc.eo[i]
    for i in range(12):
        e = cc.ep[i]
        o = cc.eo[i]
        for j in range(2):
            arr[EF[i][j]] = FACE_INDEX_TO_COLOR[EF[e][(j + o) % 2] // 9]

    return {FACE_NAMES[f]: arr[f * 9: f * 9 + 9] for f in range(6)}


# ── Random Scramble Generator ─────────────────────────────────────────────────
def generate_scramble(num_moves: int = 20):
    """
    Apply *num_moves* random moves to a solved cube.
    Returns (CubieCube, [move_name, ...]).
    """
    cc = CubieCube()
    moves_applied = []
    last_face = None
    opposite = {'U':'D','D':'U','R':'L','L':'R','F':'B','B':'F'}

    for _ in range(num_moves):
        choices = [
            (name, mv) for name, mv in _MOVE_LIST
            if name[0] != last_face
            and not (last_face and opposite.get(last_face) == name[0] and name[0] < last_face)
        ]
        name, mv = random.choice(choices)
        cc = cc.apply(mv)
        moves_applied.append(name)
        last_face = name[0]

    return cc, moves_applied
