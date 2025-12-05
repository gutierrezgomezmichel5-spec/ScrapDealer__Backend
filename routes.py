# routes.py
from flask import jsonify, request
from geopy.distance import geodesic

def init_routes(app, db, Material):

    @app.route('/')
    def home():
        return jsonify({"mensaje": "¡EcoRuta backend activado! 🌱"})

    @app.route('/api/material', methods=['POST'])
    def add_material():
        data = request.get_json()
        if not data or 'tipo' not in data or 'cantidad' not in data:
            return jsonify({"error": "Faltan datos"}), 400

        nuevo = Material(
            tipo=data['tipo'],
            cantidad=data['cantidad'],
            lat=data.get('lat'),
            lon=data.get('lon')
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"mensaje": "Registrado", "id": nuevo.id}), 201

    @app.route('/api/materiales_cercanos', methods=['GET'])
    def cercanos():
        try:
            lat = float(request.args.get('lat'))
            lon = float(request.args.get('lon'))
            radio = float(request.args.get('radio', 5))
        except:
            return jsonify({"error": "Parámetros inválidos"}), 400

        materiales = Material.query.filter(Material.estado == 'disponible').all()
        resultado = []

        for m in materiales:
            if m.lat and m.lon:
                dist = geodesic((lat, lon), (m.lat, m.lon)).km
                if dist <= radio:
                    resultado.append({
                        "id": m.id,
                        "tipo": m.tipo,
                        "cantidad": m.cantidad,
                        "distancia_km": round(dist, 2)
                    })

        resultado.sort(key=lambda x: x['distancia_km'])
        return jsonify(resultado)