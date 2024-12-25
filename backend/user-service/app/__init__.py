from flask import Flask, send_from_directory
from .extensions import db, migrate
from .config import Config
from .routes import user_bp
from .models import User
from confluent_kafka import Consumer
from flask_jwt_extended import JWTManager


# Kafka consumer configuration
consumer_config = {
    'bootstrap.servers': 'localhost:9092',  # Kafka broker
    'group.id': 'test-consumer-group',          # Consumer group ID
    'auto.offset.reset': 'earliest',        # Start consuming from the beginning
}
consumer = Consumer(consumer_config)
consumer.subscribe(['jwt_blacklist'])

# In-memory blacklist
BLACKLIST2 = set()

def consume_blacklist_messages():
    """Background thread for consuming blacklist tokens."""
    while True:
        msg = consumer.poll(1.0)  # Poll for new messages
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        jti = msg.value().decode('utf-8')
        BLACKLIST2.add(jti)  # Add the `jti` to the blacklist
        print(f"Token added to blacklist (user): {jti}")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = '../uploads/'
    jwt = JWTManager()

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        print("{0}TOKEN CHECKING{1} RECEIPE".format(BLACKLIST2, jti))
        return jti in BLACKLIST2  # Check if the token is blacklisted

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    app.register_blueprint(user_bp)

    return app
