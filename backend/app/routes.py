import os
import jwt
import bcrypt
import re
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from functools import wraps
from pydantic import ValidationError
from app.models import LoginRequest, ContribuyenteUpdate
from app.database import supabase

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

def get_jwt_secret():
    return os.environ.get('JWT_SECRET', 'super-secret-default-key')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        try:
            data = jwt.decode(token, get_jwt_secret(), algorithms=["HS256"])
            current_user = data['sub']
        except Exception as e:
            return jsonify({'error': 'Token is invalid or expired'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

def validar_ruc_sintaxis(ruc: str) -> bool:
    return bool(re.match(r'^\d{13}$', ruc))

@api_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400
            
        validated_data = LoginRequest(**data)
        ruc = validated_data.ruc
        password = validated_data.password

        if not supabase:
            return jsonify({'error': 'Database connection error'}), 500

        # En Supabase, usamos la tabla contribuyentes para el login
        response = supabase.table('contribuyentes').select('*').eq('ruc', ruc).execute()
        
        if not response.data or len(response.data) == 0:
            return jsonify({'error': 'Invalid credentials'}), 401
            
        user = response.data[0]
        
        # Validar password con bcrypt (asegurándonos de que el campo exista)
        if 'password_hash' not in user or not user['password_hash']:
            return jsonify({'error': 'Invalid credentials'}), 401

        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 401
            
        # Generar JWT usando el RUC como subject
        token = jwt.encode({
            'sub': user['ruc'],
            'exp': datetime.utcnow() + timedelta(hours=2)
        }, get_jwt_secret(), algorithm="HS256")
        
        return jsonify({'token': token, 'ruc': user['ruc']}), 200

    except ValidationError as e:
        return jsonify({'error': 'Validation Error', 'details': e.errors()}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/contribuyente/<ruc>', methods=['GET'])
@token_required
def get_contribuyente(current_user, ruc):
    if not validar_ruc_sintaxis(ruc):
        return jsonify({'error': 'RUC inválido. Debe tener exactamente 13 dígitos numéricos.'}), 400
        
    if not supabase:
        return jsonify({'error': 'Database connection error'}), 500
        
    response = supabase.table('contribuyentes').select('*').eq('ruc', ruc).execute()
    
    if not response.data or len(response.data) == 0:
        return jsonify({'error': 'Contribuyente no encontrado'}), 404
        
    return jsonify(response.data[0]), 200

@api_bp.route('/contribuyente/<ruc>', methods=['PUT'])
@token_required
def update_contribuyente(current_user, ruc):
    if not validar_ruc_sintaxis(ruc):
        return jsonify({'error': 'RUC inválido. Debe tener exactamente 13 dígitos numéricos.'}), 400
        
    try:
        data = request.get_json()
        validated_data = ContribuyenteUpdate(**data).model_dump(exclude_unset=True)
        
        if not validated_data:
            return jsonify({'error': 'No fields to update'}), 400
            
        if not supabase:
            return jsonify({'error': 'Database connection error'}), 500
            
        # Actualizar automatically ultima_actualizacion
        validated_data['ultima_actualizacion'] = datetime.utcnow().isoformat()
        
        response = supabase.table('contribuyentes').update(validated_data).eq('ruc', ruc).execute()
        
        if not response.data or len(response.data) == 0:
            return jsonify({'error': 'Contribuyente no encontrado o error al actualizar'}), 404
            
        return jsonify(response.data[0]), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation Error', 'details': e.errors()}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
