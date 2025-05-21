import mysql.connector
import hashlib
import re
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Topperguddan@26",
            database="chatbot"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection failed: {err}")
        return None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email):
    email = email.strip().lower()
    if not re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email):
        return False, "Invalid email address."
    return True, ""

def is_valid_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(char.isupper() for char in password):
        return False, "Password must include at least one uppercase letter."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must include at least one special character (!@#$%^&* etc.)."
    return True, ""
def register_user(name, email, password):
    conn = get_db_connection()
    if conn is None:
        return False, "Database connection failed"

    cursor = conn.cursor(buffered=True, dictionary=True)

    # Check if the email is already registered
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            # If the user exists and is an OAuth user, allow login
            if password == "google_oauth_dummy_password" and user["password"] == "google_oauth_dummy_password":
                return True, "User logged in successfully"
            else:
                return False, "Email already registered with a manual account"
    except Exception as e:
        return False, f"Error checking user: {str(e)}"

    # Skip password validation for Google OAuth users
    if password != "google_oauth_dummy_password":
        password_valid, password_error = is_valid_password(password)
        if not password_valid:
            return False, password_error

    hashed_password = hash_password(password) if password != "google_oauth_dummy_password" else password
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_password)
        )
        conn.commit()
        return True, "Registration successful"
    except mysql.connector.IntegrityError:
        return False, "Email already registered"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"
    finally:
        cursor.close()
        conn.close()

def authenticate(identifier, password):
    conn = get_db_connection()
    if conn is None:
        return False

    cursor = conn.cursor(buffered=True, dictionary=True)
    hashed_password = hash_password(password)
    try:
        cursor.execute("SELECT * FROM users WHERE (name = %s OR email = %s) AND password = %s",
                       (identifier, identifier, hashed_password))
        user = cursor.fetchone()
        cursor.fetchall()
        return user is not None
    except Exception as e:
        print(f"Authentication error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


