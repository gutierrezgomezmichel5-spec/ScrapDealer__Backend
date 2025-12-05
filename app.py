# app.py
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from routes import init_routes
from models import define_models

app = Flask(__name__)
app.config.from_object(Config)

# CREAMOS db AQUÍ
db = SQLAlchemy(app)

# DEFINIMOS EL MODELO DESPUÉS DE db
Material = define_models(db)

# CREAMOS TABLAS
with app.app_context():
    db.create_all()

# INICIAMOS RUTAS
init_routes(app, db, Material)  # Pasamos db y Material

if __name__ == '__main__':
    app.run(debug=True)