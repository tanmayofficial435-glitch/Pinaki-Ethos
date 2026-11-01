import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path


# =================================
# DATABASE
# =================================

DATABASE_FILE = Path("ai/my_ai.db")


def get_connection():
    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.row_factory = sqlite3.Row

    return connection


# =================================
# INITIALIZE
# =================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            plan TEXT NOT NULL DEFAULT 'free',
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    connection.commit()

    connection.close()


# =================================
# PASSWORD HASHING
# =================================

def hash_password(password, salt=None):

    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200_000
    ).hex()

    return password_hash, salt


def verify_password(
    password,
    stored_hash,
    salt
):

    password_hash, _ = hash_password(
        password,
        salt
    )

    return secrets.compare_digest(
        password_hash,
        stored_hash
    )


# =================================
# CREATE USER
# =================================

def create_user(
    name,
    email,
    password
):

    name = name.strip()
    email = email.strip().lower()

    if not name:
        return False, "Name is required."

    if not email:
        return False, "Email is required."

    if len(password) < 8:
        return False, (
            "Password must be at least 8 characters."
        )

    password_hash, salt = hash_password(
        password
    )

    connection = get_connection()

    try:

        connection.execute(
            """
            INSERT INTO users (
                name,
                email,
                password_hash,
                salt,
                plan,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                email,
                password_hash,
                salt,
                "free",
                datetime.now(
                    timezone.utc
                ).isoformat()
            )
        )

        connection.commit()

        return True, "Account created."

    except sqlite3.IntegrityError:

        return False, (
            "An account with this email already exists."
        )

    finally:

        connection.close()


# =================================
# GET USER
# =================================

def get_user_by_email(email):

    email = email.strip().lower()

    connection = get_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (email,)
    ).fetchone()

    connection.close()

    return user


def get_user_by_id(user_id):

    connection = get_connection()

    user = connection.execute(
        """
        SELECT id, name, email, plan, created_at
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    connection.close()

    return user


# =================================
# LOGIN
# =================================

def authenticate_user(
    email,
    password
):

    user = get_user_by_email(
        email
    )

    if user is None:
        return None

    if not verify_password(
        password,
        user["password_hash"],
        user["salt"]
    ):
        return None

    return user


# =================================
# SESSIONS
# =================================

def create_session(user_id):

    token = secrets.token_urlsafe(48)

    expires_at = (
        datetime.now(
            timezone.utc
        ) + timedelta(days=30)
    ).isoformat()

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO sessions (
            token,
            user_id,
            expires_at
        )
        VALUES (?, ?, ?)
        """,
        (
            token,
            user_id,
            expires_at
        )
    )

    connection.commit()
    connection.close()

    return token


def get_user_from_session(token):

    if not token:
        return None

    connection = get_connection()

    session = connection.execute(
        """
        SELECT user_id, expires_at
        FROM sessions
        WHERE token = ?
        """,
        (token,)
    ).fetchone()

    if session is None:

        connection.close()

        return None

    expires_at = datetime.fromisoformat(
        session["expires_at"]
    )

    if expires_at <= datetime.now(
        timezone.utc
    ):

        connection.execute(
            """
            DELETE FROM sessions
            WHERE token = ?
            """,
            (token,)
        )

        connection.commit()
        connection.close()

        return None

    user = connection.execute(
        """
        SELECT
            id,
            name,
            email,
            plan,
            created_at
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    connection.close()

    return user


def delete_session(token):

    if not token:
        return

    connection = get_connection()

    connection.execute(
        """
        DELETE FROM sessions
        WHERE token = ?
        """,
        (token,)
    )

    connection.commit()
    connection.close()


# =================================
# STARTUP
# =================================

initialize_database()


if __name__ == "__main__":

    print("=================================")
    print("🧠 MY AI DATABASE")
    print("=================================")
    print(
        "Database:",
        DATABASE_FILE
    )
    print(
        "Database initialized successfully."
    )
    print("=================================")