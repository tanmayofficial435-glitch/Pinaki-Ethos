import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

from database import (
    create_user,
    authenticate_user,
    create_session,
    get_user_from_session,
    delete_session,
)


HOST = "127.0.0.1"
PORT = 5002


# =================================
# PLANS
# =================================

PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "description": "Get started with My AI",
        "features": [
            "AI chat",
            "Local memory",
            "Basic tools"
        ]
    },

    "pro": {
        "name": "Pro",
        "price": 499,
        "description": "More AI power and tools",
        "features": [
            "Everything in Free",
            "Advanced AI tools",
            "More usage",
            "Priority features"
        ]
    },

    "creator": {
        "name": "Creator",
        "price": 999,
        "description": "For serious creators",
        "features": [
            "Everything in Pro",
            "Creative tools",
            "PPT generation",
            "Design tools",
            "Advanced creation features"
        ]
    }
}


# =================================
# HELPERS
# =================================

def send_json(handler, data, status=200):

    body = json.dumps(
        data,
        ensure_ascii=False
    ).encode("utf-8")

    handler.send_response(status)

    handler.send_header(
        "Content-Type",
        "application/json; charset=utf-8"
    )

    handler.send_header(
        "Content-Length",
        str(len(body))
    )

    handler.send_header(
        "Access-Control-Allow-Origin",
        "*"
    )

    handler.send_header(
        "Access-Control-Allow-Headers",
        "Content-Type, Authorization"
    )

    handler.send_header(
        "Access-Control-Allow-Methods",
        "GET, POST, OPTIONS"
    )

    handler.end_headers()

    handler.wfile.write(body)


def read_json(handler):

    content_length = int(
        handler.headers.get(
            "Content-Length",
            0
        )
    )

    raw_body = handler.rfile.read(
        content_length
    )

    if not raw_body:
        return {}

    return json.loads(
        raw_body.decode("utf-8")
    )


def get_token(handler):

    authorization = handler.headers.get(
        "Authorization",
        ""
    )

    if not authorization.startswith(
        "Bearer "
    ):
        return None

    return authorization[7:].strip()


def valid_email(email):

    return re.match(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        email
    ) is not None


def public_user(user):

    if user is None:
        return None

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "plan": user["plan"],
        "created_at": user["created_at"]
    }


# =================================
# SERVER
# =================================

class AuthHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):

        send_json(
            self,
            {"ok": True}
        )


    def do_GET(self):

        # -----------------------------
        # PLANS
        # -----------------------------

        if self.path == "/api/plans":

            send_json(
                self,
                {
                    "plans": PLANS
                }
            )

            return


        # -----------------------------
        # CURRENT USER
        # -----------------------------

        if self.path == "/api/me":

            token = get_token(self)

            user = get_user_from_session(
                token
            )

            if user is None:

                send_json(
                    self,
                    {
                        "authenticated": False
                    },
                    401
                )

                return

            send_json(
                self,
                {
                    "authenticated": True,
                    "user": public_user(user)
                }
            )

            return


        send_json(
            self,
            {
                "error": "Not found."
            },
            404
        )


    def do_POST(self):

        # -----------------------------
        # SIGNUP
        # -----------------------------

        if self.path == "/api/signup":

            try:

                data = read_json(self)

                name = str(
                    data.get(
                        "name",
                        ""
                    )
                ).strip()

                email = str(
                    data.get(
                        "email",
                        ""
                    )
                ).strip().lower()

                password = str(
                    data.get(
                        "password",
                        ""
                    )
                )

                if not valid_email(email):

                    send_json(
                        self,
                        {
                            "error":
                            "Please enter a valid email address."
                        },
                        400
                    )

                    return

                success, message = create_user(
                    name,
                    email,
                    password
                )

                if not success:

                    send_json(
                        self,
                        {
                            "error": message
                        },
                        400
                    )

                    return

                user = authenticate_user(
                    email,
                    password
                )

                token = create_session(
                    user["id"]
                )

                send_json(
                    self,
                    {
                        "success": True,
                        "message": "Account created.",
                        "token": token,
                        "user": public_user(user)
                    },
                    201
                )

            except Exception as error:

                print(
                    "Signup error:",
                    error
                )

                send_json(
                    self,
                    {
                        "error":
                        "Could not create the account."
                    },
                    500
                )

            return


        # -----------------------------
        # LOGIN
        # -----------------------------

        if self.path == "/api/login":

            try:

                data = read_json(self)

                email = str(
                    data.get(
                        "email",
                        ""
                    )
                ).strip().lower()

                password = str(
                    data.get(
                        "password",
                        ""
                    )
                )

                user = authenticate_user(
                    email,
                    password
                )

                if user is None:

                    send_json(
                        self,
                        {
                            "error":
                            "Incorrect email or password."
                        },
                        401
                    )

                    return

                token = create_session(
                    user["id"]
                )

                send_json(
                    self,
                    {
                        "success": True,
                        "token": token,
                        "user": public_user(user)
                    }
                )

            except Exception as error:

                print(
                    "Login error:",
                    error
                )

                send_json(
                    self,
                    {
                        "error":
                        "Could not log in."
                    },
                    500
                )

            return


        # -----------------------------
        # LOGOUT
        # -----------------------------

        if self.path == "/api/logout":

            token = get_token(self)

            delete_session(token)

            send_json(
                self,
                {
                    "success": True
                }
            )

            return


        send_json(
            self,
            {
                "error": "Not found."
            },
            404
        )


    def log_message(self, format, *args):

        print(
            "[My AI Accounts]",
            format % args
        )


# =================================
# START
# =================================

print("=================================")
print("🔐 MY AI ACCOUNT SERVER")
print("=================================")
print(
    f"http://{HOST}:{PORT}"
)
print("Signup: /api/signup")
print("Login:  /api/login")
print("Plans:  /api/plans")
print("=================================")


server = HTTPServer(
    (HOST, PORT),
    AuthHandler
)

server.serve_forever()
