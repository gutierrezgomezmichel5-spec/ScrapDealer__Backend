# models.py
from extensions import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    saldo = db.Column(db.Float, default=0.0)  # ← SALDO ACUMULADO

    def __repr__(self):
        return f"<Usuario {self.nombre}>"

class Material(db.Model):
    __tablename__ = 'material'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    estado = db.Column(db.String(20), default='disponible')

    def __repr__(self):
        return f"<Material {self.tipo} - {self.cantidad}kg>"

class Solicitud(db.Model):
    __tablename__ = 'solicitudes'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), db.ForeignKey('usuario.email'), nullable=False)
    material = db.Column(db.String(50), nullable=False)
    precio_por_kg = db.Column(db.Float, nullable=False)
    cantidad_kg = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default='en_recoleccion')  # en_recoleccion o recolectada
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Solicitud {self.material} - {self.cantidad_kg}kg>"