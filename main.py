from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect
from typing import Optional
from pydantic import BaseModel, ValidationError, EmailStr
from pymongo import MongoClient
import validators
import uuid
import jwt
import bcrypt
from bson import json_util, ObjectId
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

client = MongoClient(os.getenv('MONGO_URI'))
db = client['why-media-db']
users_collection = db['users']
urls_collection = db['urls']


class Users(BaseModel):
    username: str
    email: str
    password: str
    avatar: Optional[str] = None

class Urls(BaseModel):
    long_url: str
    short_url: str
    user_id: Optional[str] = None

def generate_unique_id():
    while True:
        unique_id = uuid.uuid4().hex[:8]
        url_doc = urls_collection.find_one({'short_url': unique_id})
        if not url_doc:
            break
    return unique_id

def validate_url(url):
    return validators.url(url)

class UrlCreateRequest(BaseModel):
    url: str
    user_id: Optional[str] = None

class UserRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    avatar: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

def generate_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password_hash(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def generate_token(user_id):
    payload = {
        'user_id': str(user_id),
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256')

def convert_objectid_to_str(data):
    if isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
            elif isinstance(value, (dict, list)):
                data[key] = convert_objectid_to_str(value)
    return data

def verify_token(token):
    try:
        decoded_token = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
@app.get('/')
def home():
    return jsonify({'message': 'Welcome to URL Shortener API'}), 200

@app.post('/register')
def register():
    data = request.get_json()
    try:
        user_data = UserRegisterRequest(**data)
    except ValidationError as error:
        return jsonify({'message': 'Invalid data', 'errors': error.errors()}), 400

    user = users_collection.find_one({'email': user_data.email})

    if user:
        return jsonify({'message': 'User already exists'}), 400
    
    hashed_password = generate_password_hash(user_data.password)
    new_user = {
        'username': user_data.username,
        'email': user_data.email,
        'password': hashed_password,
        'avatar': f"https://api.multiavatar.com/{user_data.username}.svg?apikey=${os.getenv('MULTIAVATAR_API_KEY')}"
    }

    try:
        users_collection.insert_one(new_user)
        user_registered = users_collection.find_one({'email': user_data.email}, {'password': 0})
        user_created = convert_objectid_to_str(user_registered)
    except Exception as error:
        return jsonify({'message': 'An error occurred while registering user', 'error': str(error)}), 500
    
    token = generate_token(user_created['_id'])

    return app.response_class(
        response=json_util.dumps({'message': 'User registered successfully', 'user': user_created, 'token': token}),
        status=201,
        mimetype='application/json'
    )


@app.post('/login')
def login():
    data = request.get_json()
    try:
        user_data = UserLoginRequest(**data)
    except ValidationError as e:
        return jsonify({'message': 'Invalid data', 'errors': e.errors()}), 400

    user = users_collection.find_one({'email': user_data.email})

    if not user or not check_password_hash(user_data.password, user['password']):
        return jsonify({'message': 'Invalid email or password'}), 401

    token = generate_token(user['_id'])

    user.pop('password', None)
    user = convert_objectid_to_str(user)

    return app.response_class(
        response=json_util.dumps({'message': 'Login successfully', 'user': user, 'token': token}),
        status=200,
        mimetype='application/json'
    )                        

@app.post('/create-short-url')
def create_short_url():
    token = request.headers.get('Authorization')
    try:
        data = request.get_json()
        url_data = UrlCreateRequest(**data)
    except ValidationError as error:
        return jsonify({'message': 'Invalid data', 'errors': error.errors()}), 400

    if not validate_url(url_data.url):
        return jsonify({'message': 'Invalid Url'}), 400

    url_doc = urls_collection.find_one({'long_url': url_data.url})
     
    if url_doc:
        if token:
            token = token.split(" ")[1]
            decoded_token = verify_token(token)
           
            if decoded_token:
                if not url_doc['user_id']:
                    urls_collection.update_one({'_id': url_doc['_id']}, {'$set': {'user_id': decoded_token['user_id']}})

        short_url = url_doc['short_url']
        return jsonify({'short_url': f"dzshort.vercel.app/{short_url}"}), 200

    short_url_id = generate_unique_id()

    new_url_doc = {
        'long_url': url_data.url,
        'short_url': short_url_id
    }
   
    if token:
        token = token.split(" ")[1]
        decoded_token = verify_token(token)
        if decoded_token:
            new_url_doc['user_id'] = decoded_token['user_id']
    
    urls_collection.insert_one(new_url_doc)

    return jsonify({'short_url': f"dzshort.vercel.app/{short_url_id}"}), 201
    
@app.get('/<short_url>')
def redirect_to_original_url(short_url):
    url_doc = urls_collection.find_one({'short_url': short_url})
    
    if url_doc:
        if 'user_id' in url_doc and url_doc['user_id']:
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'message': 'Unauthorized'}), 401
            token = token.split(" ")[1] 
            decoded_token = verify_token(token)
            if not decoded_token:
                return jsonify({'message': 'Invalid or expired token'}), 403
            if decoded_token['user_id'] != url_doc['user_id']:
                return jsonify({'message': 'Forbidden'}), 403
        
        return redirect(url_doc['long_url'])
    else:
        return jsonify({'message': 'No Url found'}), 404
    
if __name__ == '__main__':
    app.run(debug=True)
