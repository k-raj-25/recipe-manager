# User Service

This microservice handles user authentication, profile creation, and updates.

## Installation

1. Create a virtual environment:
    ```bash
    python -m venv venv
    ```

2. Activate the virtual environment:
    - On Windows:
        ```bash
        venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up the database:
    ```bash
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    ```

5. Run the application:
    ```bash
    python run.py
    ```

## Endpoints

- `POST /users/signup` - Create a new user.
- `POST /users/login` - Authenticate user.
- `POST /users/logout` - Logout user.
- `GET /users/profile` - View user profile (requires authentication).
- `PUT /users/profile` - Update user profile (requires authentication).
