import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# =================================
# SETTINGS
# =================================

HOST = "127.0.0.1"
PORT = 5001

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "qwen3:1.7b"

MEMORY_FILE = Path("ai/memory.json")
MAX_HISTORY = 10


# =================================
# MY AI API KEY
# =================================

# Replace this with YOUR real MYAI-... key.
# Do not send the key to me.
API_KEY = "2F391E961E7FD092A5F0F6318DDC6411C4B7CC40C840BB43"


# =================================
# MEMORY
# =================================

def load_memory():
    if not MEMORY_FILE.exists():
        return []

    try:
        data = json.loads(
            MEMORY_FILE.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(data, list):
            return data[-MAX_HISTORY:]

    except Exception as error:
        print("Memory load error:", error)

    return []


conversation_history = load_memory()


def save_memory():
    MEMORY_FILE.write_text(
        json.dumps(
            conversation_history[-MAX_HISTORY:],
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def clear_memory():
    conversation_history.clear()
    save_memory()


# =================================
# API KEY CHECK
# =================================

def valid_api_key(handler):
    authorization = handler.headers.get(
        "Authorization",
        ""
    )

    expected = "Bearer " + API_KEY

    return authorization == expected


# =================================
# OLLAMA
# =================================

def generate_response(message, system_prompt=None):

    system_message = (
        system_prompt.strip()
        if system_prompt and system_prompt.strip()
        else (
            "You are My AI, a helpful local AI assistant. "
            "Answer the user's actual question directly. "
            "Be clear, useful, and natural. "
            "Do not pretend to know things you do not know."
        )
    )

    messages = [
        {
            "role": "system",
            "content": system_message
        }
    ]

    for item in conversation_history[-MAX_HISTORY:]:

        messages.append(
            {
                "role": "user",
                "content": item["user"]
            }
        )

        messages.append(
            {
                "role": "assistant",
                "content": item["ai"]
            }
        )

    messages.append(
        {
            "role": "user",
            "content": message
        }
    )

    payload = json.dumps(
        {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": False
        }
    ).encode("utf-8")

    request = Request(
        OLLAMA_URL,
        data=payload,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:

        with urlopen(
            request,
            timeout=300
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        reply = (
            data
            .get("message", {})
            .get("content", "")
            .strip()
        )

        if not reply:
            return "I couldn't generate a response."

        conversation_history.append(
            {
                "user": message,
                "ai": reply
            }
        )

        while len(conversation_history) > MAX_HISTORY:
            conversation_history.pop(0)

        save_memory()

        return reply

    except HTTPError as error:

        print("Ollama HTTP error:", error)

        return (
            "The local AI engine returned an error."
        )

    except URLError:

        return (
            "Ollama is not running. "
            "Please start Ollama first."
        )

    except Exception as error:

        print("AI error:", error)

        return (
            "Something went wrong while generating "
            "the response."
        )

    for item in conversation_history[-MAX_HISTORY:]:

        messages.append(
            {
                "role": "user",
                "content": item["user"]
            }
        )

        messages.append(
            {
                "role": "assistant",
                "content": item["ai"]
            }
        )

    messages.append(
        {
            "role": "user",
            "content": message
        }
    )

    payload = json.dumps(
        {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": False
        }
    ).encode("utf-8")

    request = Request(
        OLLAMA_URL,
        data=payload,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:

        with urlopen(
            request,
            timeout=300
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        reply = (
            data
            .get("message", {})
            .get("content", "")
            .strip()
        )

        if not reply:
            return "I couldn't generate a response."

        conversation_history.append(
            {
                "user": message,
                "ai": reply
            }
        )

        while len(conversation_history) > MAX_HISTORY:
            conversation_history.pop(0)

        save_memory()

        return reply

    except HTTPError as error:

        print("Ollama HTTP error:", error)

        return (
            "The local AI engine returned an error."
        )

    except URLError:

        return (
            "Ollama is not running. "
            "Please start Ollama first."
        )

    except Exception as error:

        print("AI error:", error)

        return (
            "Something went wrong while generating "
            "the response."
        )


# =================================
# HTTP HANDLER
# =================================

class AIHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):

        body = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(body))
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Authorization"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, OPTIONS"
        )

        self.end_headers()

        self.wfile.write(body)

    def do_OPTIONS(self):

        self.send_response(200)

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Authorization"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, OPTIONS"
        )

        self.end_headers()

    def do_POST(self):

        # -----------------------------
        # API KEY
        # -----------------------------

        if not valid_api_key(self):

            self.send_json(
                {
                    "error": "Invalid or missing My AI API key."
                },
                401
            )

            return

        # -----------------------------
        # CLEAR MEMORY
        # -----------------------------

        if self.path == "/api/clear":

            clear_memory()

            self.send_json(
                {
                    "success": True,
                    "message": "Memory cleared."
                }
            )

            return

        # -----------------------------
        # CHAT
        # -----------------------------

        if self.path != "/api/chat":

            self.send_json(
                {
                    "error": "Not found."
                },
                404
            )

            return

        try:

            content_length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            raw_body = self.rfile.read(
                content_length
            )

            data = json.loads(
                raw_body.decode("utf-8")
            )

            message = str(
                data.get(
                    "message",
                    ""
                )
            ).strip()
            system_prompt = str(
                data.get(
                    "system",
                    ""
                )
            ).strip()
            if not message:

                self.send_json(
                    {
                        "error": "No message received."
                    },
                    400
                )

                return

            print("User:", message)

            reply = generate_response(
                message,
                system_prompt
            )

            print("My AI:", reply)

            self.send_json(
                {
                    "reply": reply
                }
            )

        except Exception as error:

            print(
                "Request error:",
                error
            )

            self.send_json(
                {
                    "error":
                        "Could not process the request."
                },
                500
            )

    def log_message(self, format, *args):

        print(
            "[My AI]",
            format % args
        )


# =================================
# START SERVER
# =================================

print("=================================")
print("🧠 MY AI LOCAL ENGINE")
print("=================================")
print(
    "Website API:",
    f"http://{HOST}:{PORT}"
)
print(
    "Brain:",
    MODEL_NAME
)
print(
    "Saved memory:",
    len(conversation_history)
)
print("=================================")


server = HTTPServer(
    (HOST, PORT),
    AIHandler
)

server.serve_forever()