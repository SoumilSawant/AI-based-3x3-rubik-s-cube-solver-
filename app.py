from flask import Flask, render_template, request, jsonify
import kociemba
from local_solver import generate_scramble, cubie_to_facelets

app = Flask(__name__)

FACE_ORDER = ['U', 'R', 'F', 'D', 'L', 'B']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve_cube():
    data = request.json
    if not data:
        return jsonify({'error': 'No data received.'}), 400

    # Validate each face has exactly 9 stickers
    for face in FACE_ORDER:
        if face not in data or len(data[face]) != 9:
            return jsonify({'error': f'Missing or incomplete data for face {face}.'}), 400

    # Build flat 54-element list in U R F D L B order
    facelets = []
    for face in FACE_ORDER:
        facelets.extend(data[face])

    # Build color → face-letter mapping from center stickers (index 4 of each face)
    color_to_letter = {}
    for face in FACE_ORDER:
        center_color = data[face][4]
        if center_color in color_to_letter:
            return jsonify({'error': 'Two faces share the same center color.'}), 400
        color_to_letter[center_color] = face   # e.g. 'white' → 'U'

    if len(color_to_letter) != 6:
        return jsonify({'error': 'Centers must all be different colors.'}), 400

    # Validate sticker colors & count
    from collections import Counter
    counts = Counter(facelets)
    for color in facelets:
        if color not in color_to_letter:
            return jsonify({'error': f"Unknown color '{color}'. Only use the 6 standard colors."}), 400
    for color, count in counts.items():
        if count != 9:
            return jsonify({'error': f"Color '{color}' appears {count} times — must be exactly 9."}), 400

    # Build the 54-character Kociemba string (URFDLB notation)
    cube_string = ''.join(color_to_letter[c] for c in facelets)

    try:
        solution = kociemba.solve(cube_string)
        return jsonify({'solution': solution})
    except Exception as e:
        return jsonify({'error': 'Invalid cube configuration. Please check your colors.'}), 400

@app.route('/scramble', methods=['GET'])
def scramble_cube():
    cc, moves = generate_scramble(num_moves=20)   # back to 20 — kociemba handles any depth instantly
    faces = cubie_to_facelets(cc)
    return jsonify({
        'faces': faces,
        'scramble': ' '.join(moves)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
