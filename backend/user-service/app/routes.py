import jwt, logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from .models import db, User
from .services import save_profile_pic
from .config import Config
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from confluent_kafka import Producer


user_bp = Blueprint('users', __name__, url_prefix='/users')

# Kafka producer configuration
producer_config = {
    'bootstrap.servers': 'localhost:9092',  # Kafka broker
}
producer = Producer(producer_config)


@user_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully!'}), 201

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    # token = jwt.encode({
    #     'sub': str(user.id),
    #     'iat': datetime.utcnow(),
    #     'exp': datetime.utcnow() + timedelta(hours=1)
    # }, Config.JWT_SECRET_KEY, algorithm='HS256')
    token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=1))

    # session = ActiveSession(token=token, user_id=user.id)
    # db.session.add(session)
    # db.session.commit()

    return jsonify({'token': token}), 200

@user_bp.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    if not refresh_token:
        return jsonify({'message': 'Refresh token is missing!'}), 403
    try:
        data = jwt.decode(refresh_token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        access_token = jwt.encode({
            'user_id': data['user_id'],
            'exp': datetime.utcnow() + timedelta(minutes=15)
        }, Config.JWT_SECRET_KEY, algorithm='HS256')
        return jsonify({'access_token': access_token}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Refresh token expired!'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid refresh token!'}), 403


@user_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    token = request.headers.get('Authorization').split()[1]
    try:
        decoded_token = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        jti = decoded_token.get('jti')
        if jti:
            # Publish the `jti` to Kafka topic
            producer.produce('jwt_blacklist', value=jti.encode('utf-8'))
            producer.flush()  # Ensure the message is sent to Kafka
        return jsonify({'message': 'User logged out successfully'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token already expired'}), 400
    except Exception as e:
        logging.error("Error: " + str(e))
        return jsonify({'message': 'Error processing logout'}), 500


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id).to_dict()
    return jsonify({
        'username': current_user.get("username"),
        'email': current_user.get("email"),
        'first_name': current_user.get("first_name"),
        'last_name': current_user.get("last_name"),
        'profile_pic': current_user.get("profile_pic")
    })

@user_bp.route('/profile', methods=['POST'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if not current_user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    
    # Update attributes of the User model instance
    current_user.first_name = data.get('first_name', current_user.first_name)
    current_user.last_name = data.get('last_name', current_user.last_name)
    current_user.email = data.get('email', current_user.email)
    
    # Handle profile picture upload if present
    if 'profile_pic' in request.files:
        profile_pic_url = save_profile_pic(request.files['profile_pic'], current_user.username)
        current_user.profile_pic = profile_pic_url  # Assuming this is a valid field in the model
    
    # Commit changes to the database
    db.session.commit()
    
    return jsonify({'message': 'Profile updated successfully'})
