# from flask import Blueprint, request, jsonify, redirect, url_for, session
# from google.oauth2 import id_token
# from google_auth_oauthlib.flow import Flow
# import os
# import pathlib
# from user_auth import register_user, authenticate  # Make sure this file is in the same folder
# from google.auth.transport.requests import Request  # Import the correct Request class

# auth_bp = Blueprint('auth', __name__)

# # Google OAuth Configuration
# os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # For local development only
# GOOGLE_CLIENT_ID = ""
# GOOGLE_CLIENT_SECRET = os.environ.get("client_secret") 
# GOOGLE_DISCOVERY_URL = ""

# # Path to client secrets JSON file
# CLIENT_SECRETS_FILE = str(pathlib.Path(__file__).parent / "client_secret.json")

# flow = Flow.from_client_secrets_file(
#     CLIENT_SECRETS_FILE,
#     scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
#     redirect_uri="http://127.0.0.1:5000/google/callback"
# )

# @auth_bp.route('/register', methods=['POST'])
# def register():
#     data = request.json
#     name = data.get('name')
#     email = data.get('email')
#     password = data.get('password')
#     success, message = register_user(name, email, password)
#     return jsonify({"success": success, "message": message}), (200 if success else 400)

# @auth_bp.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     identifier = data.get('identifier')
#     password = data.get('password')
#     success = authenticate(identifier, password)
#     return jsonify({"success": success, "message": "Login successful" if success else "Invalid credentials"}), (200 if success else 401)

# @auth_bp.route('/google/login', methods=['GET'])
# def google_login():
#     print("Google login route hit")  # Debugging
#     authorization_url, state = flow.authorization_url()
#     session["state"] = state
#     return redirect(authorization_url)

# @auth_bp.route('/google/callback', methods=['GET'])
# def google_callback():
#     try:
#         # Fetch the token from the authorization response
#         flow.fetch_token(authorization_response=request.url)

#         # Verify the state parameter to prevent CSRF attacks
#         if not session.get("state") or session["state"] != request.args.get("state"):
#             return jsonify({"error": "Invalid state parameter"}), 400

#         # Get the credentials and verify the ID token
#         credentials = flow.credentials
#         id_info = id_token.verify_oauth2_token(
#             credentials.id_token,
#             Request(),  # Use the correct Request object
#             GOOGLE_CLIENT_ID
#         )

#         # Extract user info from the verified token
#         email = id_info.get("email")
#         name = id_info.get("name")

#         if not email or not name:
#             return jsonify({"error": "Failed to retrieve user information"}), 400

#         # Check if the user exists in the database or register them
#         from user_auth import register_user
#         success, message = register_user(name, email, "google_oauth_dummy_password")
#         if not success:
#             return jsonify({"error": message}), 400

#         # Redirect to the frontend with success parameters
#         return redirect(f"http://localhost:3000?google_login=success&name={name}&email={email}")

#     except ValueError as e:
#         # Handle invalid token or other errors
#         return jsonify({"error": f"Authentication failed: {str(e)}"}), 400

# @auth_bp.route('/logout', methods=['POST'])
# def logout():
#     session.clear()  # Clear all session data
#     return jsonify({"success": True, "message": "Logged out successfully"})


from flask import Blueprint, request, jsonify, redirect, url_for, session
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import os
import pathlib
import json
from user_auth import register_user, authenticate
from google.auth.transport.requests import Request

auth_bp = Blueprint('auth', __name__)

# Google OAuth Configuration
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # For local development only

# Load Google client configuration from JSON file
CLIENT_SECRETS_FILE = str(pathlib.Path(__file__).parent / "client_secret.json")

with open(CLIENT_SECRETS_FILE, "r") as f:
    client_config = json.load(f)

GOOGLE_CLIENT_ID = client_config["web"]["client_id"]
GOOGLE_CLIENT_SECRET = client_config["web"]["client_secret"]
GOOGLE_DISCOVERY_URL = client_config["web"].get("auth_uri", "")

# Create OAuth flow instance
flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ],
    redirect_uri="http://127.0.0.1:5000/google/callback"
)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    success, message = register_user(name, email, password)
    return jsonify({"success": success, "message": message}), (200 if success else 400)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    identifier = data.get('identifier')
    password = data.get('password')
    success = authenticate(identifier, password)
    return jsonify({"success": success, "message": "Login successful" if success else "Invalid credentials"}), (200 if success else 401)

@auth_bp.route('/google/login', methods=['GET'])
def google_login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@auth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    try:
        flow.fetch_token(authorization_response=request.url)

        if not session.get("state") or session["state"] != request.args.get("state"):
            return jsonify({"error": "Invalid state parameter"}), 400

        credentials = flow.credentials
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            Request(),
            GOOGLE_CLIENT_ID
        )

        email = id_info.get("email")
        name = id_info.get("name")

        if not email or not name:
            return jsonify({"error": "Failed to retrieve user information"}), 400
        
        from user_auth import register_user
        success, message = register_user(name, email, "google_oauth_dummy_password")
        if not success:
            return jsonify({"error": message}), 400

        return redirect(f"http://localhost:3000?google_login=success&name={name}&email={email}")

    except ValueError as e:
        return jsonify({"error": f"Authentication failed: {str(e)}"}), 400

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"})
