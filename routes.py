# routes.py
from extensions import db
from flask import jsonify, request
from geopy.distance import geodesic
import bcrypt
from models import Usuario, Material, Solicitud
from datetime import datetime

def init_routes(app, db):

    # PRECIOS DE MATERIALES (puedes cambiar los precios cuando quieras)
    PRECIOS_MATERIALES = {
        "pet": 5.50,
        "hdpe": 4.80,
        "aluminio": 25.00,
        "acero": 8.00,
        "carton": 2.50,
        "papel": 3.00,
        "vidrio": 1.80,
        "organico": 1.20
    }

    @app.route('/api/precios_materiales', methods=['GET'])
    def precios_materiales():
        precios = [
            {"nombre": k, "precio": v} for k, v in PRECIOS_MATERIALES.items()
        ]
        return jsonify(precios), 200

    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json()
        nombre = data.get('nombre')
        email = data.get('email')
        password = data.get('password')

        if not all([nombre, email, password]):
            return jsonify({"error": "Faltan datos"}), 400

        if db.session.query(Usuario).filter_by(email=email).first():
            return jsonify({"error": "Email ya existe"}), 400

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        nuevo = Usuario(nombre=nombre, email=email, password=hashed.decode('utf-8'), saldo=0.0)
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"mensaje": "Usuario creado con éxito"}), 201

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Faltan datos"}), 400

        usuario = db.session.query(Usuario).filter_by(email=email).first()
        if not usuario or not bcrypt.checkpw(password.encode('utf-8'), usuario.password.encode('utf-8')):
            return jsonify({"error": "Credenciales incorrectas"}), 401

        return jsonify({
            "mensaje": "Login exitoso",
            "nombre": usuario.nombre,
            "email": usuario.email
        }), 200

    @app.route('/api/material', methods=['POST'])
    def add_material():
        data = request.get_json()
        if not data or 'tipo' not in data or 'cantidad' not in data:
            return jsonify({"error": "Faltan datos"}), 400

        nuevo = Material(
            tipo=data['tipo'].lower(),
            cantidad=data['cantidad'],
            lat=data.get('lat'),
            lon=data.get('lon')
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"mensaje": "Material registrado"}), 201

    @app.route('/api/materiales_cercanos', methods=['GET'])
    def cercanos():
        try:
            lat = float(request.args.get('lat'))
            lon = float(request.args.get('lon'))
            radio = float(request.args.get('radio', 50))
        except:
            return jsonify({"error": "Parámetros inválidos"}), 400

        materiales = Material.query.all()
        resultado = []
        for m in materiales:
            if m.lat and m.lon:
                dist = geodesic((lat, lon), (m.lat, m.lon)).km
                if dist <= radio:
                    resultado.append({
                        "id": m.id,
                        "tipo": m.tipo,
                        "cantidad": m.cantidad,
                        "lat": m.lat,
                        "lon": m.lon,
                        "distancia_km": round(dist, 2)
                    })
        resultado.sort(key=lambda x: x['distancia_km'])
        return jsonify(resultado)

    # NUEVO: Crear solicitud (iniciar recolección)
    @app.route('/api/solicitudes', methods=['POST'])
    def crear_solicitud():
        data = request.get_json()
        email = data.get('email')
        material = data.get('material')
        precio_por_kg = data.get('precio_por_kg')
        cantidad_kg = data.get('cantidad_kg')
        total = data.get('total')

        if not all([email, material, precio_por_kg, cantidad_kg, total]):
            return jsonify({"error": "Faltan datos"}), 400

        # Verificar que el usuario exista
        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        nueva = Solicitud(
            email=email,
            material=material,
            precio_por_kg=precio_por_kg,
            cantidad_kg=cantidad_kg,
            total=total
        )
        db.session.add(nueva)
        db.session.commit()
        return jsonify({"mensaje": "Solicitud creada"}), 201

    # NUEVO: Listar solicitudes del usuario
    @app.route('/api/solicitudes', methods=['GET'])
    def listar_solicitudes():
        email = request.args.get('email')
        if not email:
            return jsonify({"error": "Falta email"}), 400

        solicitudes = Solicitud.query.filter_by(email=email).order_by(Solicitud.fecha.desc()).all()
        resultado = [{
            "id": s.id,
            "material": s.material,
            "precio_por_kg": s.precio_por_kg,
            "cantidad_kg": s.cantidad_kg,
            "total": s.total,
            "estado": s.estado,
            "fecha": s.fecha.isoformat()
        } for s in solicitudes]

        return jsonify(resultado), 200

    # NUEVO: Ver saldo
    @app.route('/api/saldo', methods=['GET'])
    def ver_saldo():
        email = request.args.get('email')
        if not email:
            return jsonify({"error": "Falta email"}), 400

        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        return jsonify({"saldo": usuario.saldo}), 200

    # NUEVO: Retirar fondos (simulamos que se procesa y se resta)
    @app.route('/api/retirar', methods=['POST'])
    def retirar_fondos():
        data = request.get_json()
        email = data.get('email')
        monto = data.get('monto')

        if not email or not monto or monto <= 0:
            return jsonify({"error": "Datos inválidos"}), 400

        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        if usuario.saldo < monto:
            return jsonify({"error": "Saldo insuficiente"}), 400

        usuario.saldo -= monto
        db.session.commit()
        return jsonify({"mensaje": "Retiro exitoso", "nuevo_saldo": usuario.saldo}), 200

    # NUEVO: Borrar cuenta
    @app.route('/api/usuario', methods=['DELETE'])
    def borrar_cuenta():
        data = request.get_json()
        email = data.get('email')
        if not email:
            return jsonify({"error": "Falta email"}), 400

        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        db.session.delete(usuario)
        db.session.commit()
        return jsonify({"mensaje": "Cuenta borrada"}), 200

    @app.route("/")
    def root():
        return jsonify({"mensaje": "¡ScrapDealer Backend FULL ACTIVADO! 🌱"}), 200