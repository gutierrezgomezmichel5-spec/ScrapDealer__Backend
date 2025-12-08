# app.py ← VERSIÓN CORREGIDA
import os
from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db  # ← Ahora usamos la instancia global
from routes import init_routes
# Ya no necesitas: import models

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/*": {"origins": "*"}})

# Inicializamos la extensión con la app
db.init_app(app)

# CREAR TABLAS
with app.app_context():
    db.create_all()
    print("¡Tablas usuario y material creadas o ya existen en Neon!")

# RUTAS
init_routes(app, db)

port = int(os.environ.get("PORT", 5000))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)