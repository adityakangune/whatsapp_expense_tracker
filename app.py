from flask import Flask
from routes.whatsapp import bp as whatsapp_bp
from routes.summary import bp as summary_bp
from routes.debug import bp as debug_bp
from config import GROQ_API_KEY, OCR_BACKEND, TESSERACT_CMD

def create_app():
    app = Flask(__name__)
    app.register_blueprint(whatsapp_bp)
    app.register_blueprint(summary_bp)
    app.register_blueprint(debug_bp)
    print(f"Grok key loaded: {'yes' if GROQ_API_KEY else 'NO'}")
    print(f"OCR backend: {OCR_BACKEND}  (tesseract at {TESSERACT_CMD})")
    return app

app = create_app()

if __name__ == "__main__":
    # Local run; Cloud Run uses gunicorn via Dockerfile
    app.run(host="0.0.0.0", port=5000, debug=True)
