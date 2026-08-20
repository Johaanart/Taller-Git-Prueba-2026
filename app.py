from flask import Flask, render_template, request, make_response
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO

app = Flask(__name__)

# Simplified polygon for Colombia (lon, lat) — rough outline for demo purposes
COLOMBIA_POLY = [
    (-79.0, 12.5), (-75.0, 11.5), (-72.0, 9.0), (-70.0, 4.0),
    (-73.0, -3.5), (-76.0, -4.2), (-78.0, -1.0), (-80.0, 2.0),
    (-82.0, 7.0), (-82.0, 11.0), (-79.0, 12.5)
]


def parse_coord(text):
    """Parse 'lat,lon' or 'lon,lat' (comma-separated). Returns (lon, lat) or None."""
    if not text:
        return None
    try:
        parts = [p.strip() for p in text.split(',')]
        if len(parts) != 2:
            return None
        a, b = float(parts[0]), float(parts[1])
        # Heuristic: if first number looks like latitude
        if -90 <= a <= 90 and -180 <= b <= 180:
            # assume a=lat, b=lon -> convert to (lon, lat)
            return (b, a)
        else:
            return (a, b)
    except Exception:
        return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/map.png')
def map_png():
    dep = request.args.get('dep')  # expected 'lat,lon' or similar
    arr = request.args.get('arr')
    intensity = request.args.get('intensity')

    dep_coord = parse_coord(dep)
    arr_coord = parse_coord(arr)
    try:
        intensity_val = float(intensity) if intensity is not None else None
    except Exception:
        intensity_val = None

    fig, ax = plt.subplots(figsize=(6, 6))
    # Draw simplified polygon
    xs = [p[0] for p in COLOMBIA_POLY]
    ys = [p[1] for p in COLOMBIA_POLY]
    ax.fill(xs, ys, facecolor='#cce5ff', edgecolor='#2b7bba')

    # Plot airports if provided
    if dep_coord:
        ax.plot(dep_coord[0], dep_coord[1], 'o', color='red', markersize=8 if not intensity_val else 4 + intensity_val)
        ax.text(dep_coord[0]+0.3, dep_coord[1]+0.3, 'Salida', color='red')
    if arr_coord:
        ax.plot(arr_coord[0], arr_coord[1], 'o', color='green', markersize=8 if not intensity_val else 4 + intensity_val)
        ax.text(arr_coord[0]+0.3, arr_coord[1]+0.3, 'Llegada', color='green')

    ax.set_xlim(-82, -66)
    ax.set_ylim(-5, 13)
    ax.set_xlabel('Longitud')
    ax.set_ylabel('Latitud')
    ax.set_title('Mapa aproximado de Colombia')
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.3)

    buf = BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)

    response = make_response(buf.read())
    response.headers.set('Content-Type', 'image/png')
    response.headers.set('Cache-Control', 'no-store')
    return response


if __name__ == '__main__':
    app.run(debug=True)
