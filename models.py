# models.py
from flask_sqlalchemy import SQLAlchemy

# NO definas db aquí
# db = SQLAlchemy()  ← ¡BORRA ESTO!

# Define el modelo como función
def define_models(db):
    class Material(db.Model):
        __tablename__ = 'material'
        id = db.Column(db.Integer, primary_key=True)
        tipo = db.Column(db.String(50), nullable=False)
        cantidad = db.Column(db.Float, nullable=False)
        lat = db.Column(db.Float)
        lon = db.Column(db.Float)
        estado = db.Column(db.String(20), default='disponible')
        fecha = db.Column(db.DateTime, default=db.func.now())

        def to_dict(self):
            return {
                "id": self.id,
                "tipo": self.tipo,
                "cantidad": self.cantidad,
                "lat": self.lat,
                "lon": self.lon,
                "estado": self.estado
            }

    return Material