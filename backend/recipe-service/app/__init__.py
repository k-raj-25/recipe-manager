from flask import Flask
from app.config import Config
from app.extensions import db, migrate
from confluent_kafka import Consumer
from flask_jwt_extended import JWTManager


# Kafka consumer configuration
consumer_config = {
    'bootstrap.servers': 'localhost:9092',  # Kafka broker
    'group.id': 'test-consumer-group2',          # Consumer group ID
    'auto.offset.reset': 'earliest',        # Start consuming from the beginning
}
consumer = Consumer(consumer_config)
consumer.subscribe(['jwt_blacklist'])

# In-memory blacklist
BLACKLIST = set()

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
        BLACKLIST.add(jti)  # Add the `jti` to the blacklist
        print(f"Token added to blacklist: {jti}")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    jwt = JWTManager()

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        print("{0}TOKEN CHECKING{1} RECEIPE".format(BLACKLIST, jti))
        return jti in BLACKLIST  # Check if the token is blacklisted

    # Register blueprints
    from app.routes import recipe_bp
    app.register_blueprint(recipe_bp)

    return app