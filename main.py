# main.py
from flask import Flask
from app.api.routes import api
from app.ui.interfaz import ui  # Importar la interfaz web

def create_app():
    app = Flask(__name__)
    app.register_blueprint(api)
    app.register_blueprint(ui)  # Registrar la interfaz web
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
