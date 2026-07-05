from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Enable CORS si es necesario, o mantenerlo simple si el frontend lo manejará.
    # Dado que estarán en la misma red o el frontend hará peticiones desde el cliente,
    # podríamos necesitar CORS. Por ahora asumimos que la configuración básica es suficiente.
    from flask_cors import CORS
    CORS(app)

    from app.routes import api_bp
    app.register_blueprint(api_bp)

    # Inicializar DB automáticamente
    try:
        from init_db import init_db
        init_db()
    except Exception as e:
        print(f"No se pudo inicializar la base de datos automáticamente: {e}")

    @app.route('/health')
    def health():
        return {"status": "healthy"}, 200

    return app
