import json
import os
import threading
from pathlib import Path

import joblib
import numpy as np
from flask import Flask, jsonify, request
from PIL import Image
from skimage.feature import hog

APP_PORT = 8098
OPTIONS_PATH = "/data/options.json"

app = Flask(__name__)
_model_lock = threading.Lock()
_model = None
_model_path_loaded = None

# HOG settings must stay identical to the training notebook.
HOG_SIZE = (160, 120)  # width, height
HOG_ORIENTATIONS = 9
HOG_PIXELS_PER_CELL = (8, 8)
HOG_CELLS_PER_BLOCK = (2, 2)


def load_options():
    defaults = {
        "model_path": "/media/frigate/data/mailbox_rf.joblib",
        "default_image": "media/frigate/reference_image/ref_image.jpg",
    }
    try:
        with open(OPTIONS_PATH, "r", encoding="utf-8") as f:
            opts = json.load(f) or {}
        defaults.update(opts)
    except Exception:
        pass
    return defaults


def extract_features(image_path: str) -> np.ndarray:
    """
    HOG + color feature vector.

    Color features:
      - RGB histograms: 32 bins x 3
      - HSV histograms: 32 bins x 3
      - grayscale histogram: 32 bins
      - RGB mean/std: 6
      - grayscale mean/std: 2
      - edge-density proxy: 1

    Structural features:
      - HOG on 160x120 grayscale image

    IMPORTANT: Must stay identical to the training notebook.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    with Image.open(path) as im:
        rgb = im.convert("RGB").resize((320, 240))
        arr = np.asarray(rgb, dtype=np.uint8)
        feats = []

        # RGB histograms
        for c in range(3):
            hist, _ = np.histogram(arr[:, :, c], bins=32, range=(0, 256), density=True)
            feats.extend(hist.tolist())

        # HSV histograms
        hsv = np.asarray(rgb.convert("HSV"), dtype=np.uint8)
        for c in range(3):
            hist, _ = np.histogram(hsv[:, :, c], bins=32, range=(0, 256), density=True)
            feats.extend(hist.tolist())

        # Grayscale histogram + statistics
        gray = np.asarray(rgb.convert("L"), dtype=np.uint8)
        hist, _ = np.histogram(gray, bins=32, range=(0, 256), density=True)
        feats.extend(hist.tolist())

        feats.extend(arr.mean(axis=(0, 1)).tolist())
        feats.extend(arr.std(axis=(0, 1)).tolist())
        feats.append(float(gray.mean()))
        feats.append(float(gray.std()))

        # Simple edge-density proxy
        dx = np.abs(np.diff(gray.astype(np.int16), axis=1))
        dy = np.abs(np.diff(gray.astype(np.int16), axis=0))
        edge_density = float((dx > 20).mean() + (dy > 20).mean()) / 2.0
        feats.append(edge_density)

        # HOG structural features
        hog_gray = np.asarray(
            rgb.convert("L").resize(HOG_SIZE),
            dtype=np.float32
        ) / 255.0

        hog_features = hog(
            hog_gray,
            orientations=HOG_ORIENTATIONS,
            pixels_per_cell=HOG_PIXELS_PER_CELL,
            cells_per_block=HOG_CELLS_PER_BLOCK,
            block_norm="L2-Hys",
            feature_vector=True,
        )

        feats.extend(hog_features.tolist())

    return np.asarray(feats, dtype=np.float32)


def ensure_model():
    global _model, _model_path_loaded
    options = load_options()
    model_path = options["model_path"]

    with _model_lock:
        if _model is None or _model_path_loaded != model_path:
            if not os.path.exists(model_path):
                _model = None
                _model_path_loaded = None
                return None, model_path
            _model = joblib.load(model_path)
            _model_path_loaded = model_path

    return _model, model_path


@app.get("/")
def index():
    model, model_path = ensure_model()
    options = load_options()
    return f"""
    <html><body style="font-family:sans-serif;max-width:760px;margin:2rem auto;line-height:1.5">
      <h2>Mailbox Classifier</h2>
      <p><b>Classifier:</b> HOG + Color Random Forest</p>
      <p><b>Status:</b> {"model loaded" if model is not None else "model not found"}</p>
      <p><b>Model:</b> {model_path}</p>
      <p><b>Default image:</b> {options["default_image"]}</p>
      <p>POST JSON to <code>/classify</code> with
      <code>{{"image":"/media/current_mailbox.jpg"}}</code>.</p>
      <p>Health: <code>/health</code> &nbsp; Reload model: <code>POST /reload</code></p>
    </body></html>
    """


@app.get("/health")
def health():
    model, model_path = ensure_model()
    return jsonify({
        "ok": True,
        "classifier": "hog_color_random_forest",
        "model_loaded": model is not None,
        "model_path": model_path
    })


@app.post("/reload")
def reload_model():
    global _model, _model_path_loaded
    with _model_lock:
        _model = None
        _model_path_loaded = None
    model, model_path = ensure_model()
    if model is None:
        return jsonify({
            "ok": False,
            "error": "model_not_found",
            "model_path": model_path
        }), 404
    return jsonify({"ok": True, "model_path": model_path})


@app.post("/classify")
def classify():
    options = load_options()
    payload = request.get_json(silent=True) or {}
    image_path = payload.get("image") or options["default_image"]

    model, model_path = ensure_model()
    if model is None:
        return jsonify({
            "ok": False,
            "error": "model_not_found",
            "model_path": model_path,
            "hint": "Train with the included notebook and copy mailbox_rf.joblib to /data/mailbox_rf.joblib."
        }), 503

    try:
        features = extract_features(image_path).reshape(1, -1)
        prediction = str(model.predict(features)[0])

        result = {
            "ok": True,
            "classifier": "hog_color_random_forest",
            "image": image_path,
            "prediction": prediction,
            "model_path": model_path,
            "feature_count": int(features.shape[1]),
        }

        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(features)[0]
            classes = [str(c) for c in model.classes_]
            result["probabilities"] = {c: float(p) for c, p in zip(classes, probs)}
            if "occupied" in classes:
                result["occupied_probability"] = float(probs[classes.index("occupied")])
            if "empty" in classes:
                result["empty_probability"] = float(probs[classes.index("empty")])

        return jsonify(result)

    except FileNotFoundError as e:
        return jsonify({"ok": False, "error": "image_not_found", "message": str(e)}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": "classification_failed", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=APP_PORT)
