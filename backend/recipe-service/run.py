from app import create_app, consume_blacklist_messages
from flask import jsonify
import os
import threading


# Create the Flask application
app = create_app()



# Define a simple route for health check
@app.route('/')
def health_check():
    return jsonify({"message": "Recipe Service is running"}), 200

if __name__ == '__main__':
    threading.Thread(target=consume_blacklist_messages, daemon=True).start()
    # Define the port where the service will run
    port = int(os.environ.get("PORT", 5002))
    app.run(host='0.0.0.0', port=port, debug=True)
