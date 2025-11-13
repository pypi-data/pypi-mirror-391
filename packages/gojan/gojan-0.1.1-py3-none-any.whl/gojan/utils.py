"""
Utility helpers for gojan package.

- intern_link(): imports tensorflow and runs a tiny check/demo.
- available_components(): reports which optional libraries (flask, numpy, pandas, sklearn, torch) are importable.
- create_app(): a tiny Flask app factory (only if Flask is installed); returns a Flask app that shows component status.
"""

from typing import Dict

def intern_link() -> Dict:
    """
    Try importing tensorflow and return a small dict confirming the TF import and version.
    If TensorFlow is not available, raise an ImportError.
    """
    try:
        import tensorflow as tf
    except Exception as e:
        raise ImportError(
            "TensorFlow could not be imported. Make sure tensorflow==2.12.1 is installed. Original error: "
            + str(e)
        )

    try:
        c = tf.constant([[1.0, 2.0], [3.0, 4.0]])
        # tf.Tensor has .shape; convert to python list if possible
        shape = tuple(c.shape.as_list()) if hasattr(c.shape, "as_list") else tuple(c.shape)
        return {
            "tensorflow_version": tf.__version__,
            "tensor_shape": shape,
            "note": "TensorFlow imported successfully and a small constant was created."
        }
    except Exception as e:
        return {
            "tensorflow_version": tf.__version__,
            "error": f"TensorFlow imported but small demo op failed: {e}"
        }


def available_components() -> Dict[str, bool]:
    """
    Probe for optional libraries and return a status dict.
    Example keys: 'flask', 'numpy', 'pandas', 'sklearn', 'torch'
    """
    components = {}
    for name, import_name in [
        ("flask", "flask"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("scikit-learn", "sklearn"),
        ("scipy", "scipy"),
        ("matplotlib", "matplotlib"),
        ("Pillow", "PIL"),
        ("seaborn", "seaborn"),
        ("torch", "torch"),
    ]:
        try:
            __import__(import_name)
            components[name] = True
        except Exception:
            components[name] = False
    return components


def create_app(test_config: dict = None):
    """
    Minimal Flask app factory that shows which optional components are available.
    If Flask is not installed, raises ImportError.
    Usage:
        app = create_app()
        app.run(port=5000)
    """
    try:
        from flask import Flask, jsonify, render_template_string
    except Exception as e:
        raise ImportError("Flask is not installed. Install 'gojan[web]' or 'Flask' separately.") from e

    app = Flask(__name__)

    @app.route("/")
    def index():
        comps = available_components()
        html = """
        <html>
        <head><title>gojan status</title></head>
        <body style="font-family: Arial; padding: 2rem;">
          <h1>gojan — components status</h1>
          <p>TensorFlow version (if available) and small demo can be fetched via <code>intern_link()</code>.</p>
          <h2>Optional libraries</h2>
          <ul>
          {% for k, v in comps.items() %}
            <li><strong>{{ k }}</strong>: {{ "available" if v else "not installed" }}</li>
          {% endfor %}
          </ul>
        </body>
        </html>
        """
        return render_template_string(html, comps=comps)

    @app.route("/intern")
    def intern_info():
        try:
            info = intern_link()
            return jsonify({"ok": True, "info": info})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

    return app
