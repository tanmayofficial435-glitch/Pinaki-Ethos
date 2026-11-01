// ============================================================
// PRISM AI BACKEND
// ============================================================

const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
const OpenAI = require("openai");
const bcrypt = require("bcryptjs");
const crypto = require("crypto");
const path = require("path");
const fs = require("fs");
const sqlite3 = require("sqlite3").verbose();

dotenv.config();

const app = express();
const PORT = 3000;

// ============================================================
// CONFIG
// ============================================================

const MODEL = "openrouter/free";

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;

if (!OPENROUTER_API_KEY) {
    console.error("❌ OPENROUTER_API_KEY is missing");
}

// ============================================================
// OPENROUTER
// ============================================================

const client = new OpenAI({
    baseURL: "https://openrouter.ai/api/v1",
    apiKey: OPENROUTER_API_KEY
});

// ============================================================
// MIDDLEWARE
// ============================================================

app.use(cors());

app.use(express.json({
    limit: "20mb"
}));

app.use(express.urlencoded({
    extended: true,
    limit: "20mb"
}));

// ============================================================
// DATABASE
// ============================================================

const DATA_DIR = path.join(__dirname, "data");
const DB_FILE = path.join(DATA_DIR, "users.db");

if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, {
        recursive: true
    });
}

const db = new sqlite3.Database(DB_FILE, (err) => {
    if (err) {
        console.error("❌ SQLite connection failed:", err.message);
    } else {
        console.log("🗄️ SQLite database connected");
        console.log("📁 Database file:", DB_FILE);
    }
});

// ============================================================
// CREATE USERS TABLE
// ============================================================

db.run(`
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        passwordHash TEXT NOT NULL,
        createdAt TEXT NOT NULL
    )
`, (err) => {
    if (err) {
        console.error("❌ Could not create users table:", err.message);
    } else {
        console.log("✅ Users table ready");
    }
});

// ============================================================
// SESSIONS
// ============================================================

const sessions = new Map();

// ============================================================
// HELPERS
// ============================================================

function createSession(user) {
    const token = crypto.randomBytes(32).toString("hex");

    sessions.set(token, {
        userId: user.id,
        createdAt: Date.now()
    });

    return token;
}

function getUserFromRequest(req) {
    const authHeader = req.headers.authorization || "";

    if (!authHeader.startsWith("Bearer ")) {
        return null;
    }

    const token = authHeader.substring(7);

    const session = sessions.get(token);

    if (!session) {
        return null;
    }

    return new Promise((resolve) => {
        db.get(
            `
            SELECT id, name, email, createdAt
            FROM users
            WHERE id = ?
            `,
            [session.userId],
            (err, user) => {
                if (err || !user) {
                    resolve(null);
                    return;
                }

                resolve({
                    ...user,
                    token
                });
            }
        );
    });
}

// ============================================================
// API STATUS
// ============================================================

app.get("/api/status", (req, res) => {
    res.json({
        ok: true,
        provider: "OpenRouter",
        model: MODEL,
        database: "SQLite",
        authentication: true,
        webSearch: true,
        logoGeneration: true
    });
});

// ============================================================
// SIGN UP
// ============================================================

app.post("/api/auth/signup", async (req, res) => {
    try {
        const name = String(req.body.name || "").trim();
        const email = String(req.body.email || "").trim().toLowerCase();
        const password = String(req.body.password || "");

        if (!name || !email || !password) {
            return res.status(400).json({
                ok: false,
                error: "Name, email and password are required."
            });
        }

        if (password.length < 6) {
            return res.status(400).json({
                ok: false,
                error: "Password must be at least 6 characters."
            });
        }

        db.get(
            `
            SELECT id
            FROM users
            WHERE email = ?
            `,
            [email],
            async (err, existingUser) => {
                if (err) {
                    console.error(err);

                    return res.status(500).json({
                        ok: false,
                        error: "Database error."
                    });
                }

                if (existingUser) {
                    return res.status(409).json({
                        ok: false,
                        error: "An account with this email already exists."
                    });
                }

                const passwordHash = await bcrypt.hash(password, 12);

                const userId = crypto.randomUUID();

                const createdAt = new Date().toISOString();

                db.run(
                    `
                    INSERT INTO users
                    (
                        id,
                        name,
                        email,
                        passwordHash,
                        createdAt
                    )
                    VALUES (?, ?, ?, ?, ?)
                    `,
                    [
                        userId,
                        name,
                        email,
                        passwordHash,
                        createdAt
                    ],
                    function (insertErr) {
                        if (insertErr) {
                            console.error(insertErr);

                            return res.status(500).json({
                                ok: false,
                                error: "Could not create account."
                            });
                        }

                        const user = {
                            id: userId,
                            name,
                            email,
                            createdAt
                        };

                        const token = createSession(user);

                        res.json({
                            ok: true,
                            message: "Account created successfully.",
                            token,
                            user
                        });
                    }
                );
            }
        );
    } catch (error) {
        console.error("Signup error:", error);

        res.status(500).json({
            ok: false,
            error: "Signup failed."
        });
    }
});

// ============================================================
// LOGIN
// ============================================================

app.post("/api/auth/login", async (req, res) => {
    try {
        const email = String(req.body.email || "").trim().toLowerCase();
        const password = String(req.body.password || "");

        if (!email || !password) {
            return res.status(400).json({
                ok: false,
                error: "Email and password are required."
            });
        }

        db.get(
            `
            SELECT *
            FROM users
            WHERE email = ?
            `,
            [email],
            async (err, user) => {
                if (err) {
                    console.error(err);

                    return res.status(500).json({
                        ok: false,
                        error: "Database error."
                    });
                }

                if (!user) {
                    return res.status(401).json({
                        ok: false,
                        error: "Invalid email or password."
                    });
                }

                const passwordMatches = await bcrypt.compare(
                    password,
                    user.passwordHash
                );

                if (!passwordMatches) {
                    return res.status(401).json({
                        ok: false,
                        error: "Invalid email or password."
                    });
                }

                const safeUser = {
                    id: user.id,
                    name: user.name,
                    email: user.email,
                    createdAt: user.createdAt
                };

                const token = createSession(safeUser);

                res.json({
                    ok: true,
                    message: "Login successful.",
                    token,
                    user: safeUser
                });
            }
        );
    } catch (error) {
        console.error("Login error:", error);

        res.status(500).json({
            ok: false,
            error: "Login failed."
        });
    }
});

// ============================================================
// GET CURRENT USER
// ============================================================

app.get("/api/auth/me", async (req, res) => {
    try {
        const user = await getUserFromRequest(req);

        if (!user) {
            return res.status(401).json({
                ok: false,
                error: "Not logged in."
            });
        }

        res.json({
            ok: true,
            user: {
                id: user.id,
                name: user.name,
                email: user.email,
                createdAt: user.createdAt
            }
        });
    } catch (error) {
        console.error("ME error:", error);

        res.status(500).json({
            ok: false,
            error: "Could not load account."
        });
    }
});

// ============================================================
// LOGOUT
// ============================================================

app.post("/api/auth/logout", (req, res) => {
    const authHeader = req.headers.authorization || "";

    if (authHeader.startsWith("Bearer ")) {
        const token = authHeader.substring(7);

        sessions.delete(token);
    }

    res.json({
        ok: true,
        message: "Logged out."
    });
});

// ============================================================
// UPDATE PROFILE
// ============================================================

app.put("/api/auth/profile", async (req, res) => {
    try {
        const currentUser = await getUserFromRequest(req);

        if (!currentUser) {
            return res.status(401).json({
                ok: false,
                error: "You must be logged in."
            });
        }

        const newName = String(req.body.name || "").trim();
        const newEmail = String(req.body.email || "")
            .trim()
            .toLowerCase();

        if (!newName) {
            return res.status(400).json({
                ok: false,
                error: "Name cannot be empty."
            });
        }

        if (!newEmail) {
            return res.status(400).json({
                ok: false,
                error: "Email cannot be empty."
            });
        }

        // --------------------------------------------------------
        // CHECK WHETHER EMAIL IS ALREADY USED
        // --------------------------------------------------------

        db.get(
            `
            SELECT id
            FROM users
            WHERE email = ?
            AND id != ?
            `,
            [
                newEmail,
                currentUser.id
            ],
            (emailErr, existingUser) => {
                if (emailErr) {
                    console.error(emailErr);

                    return res.status(500).json({
                        ok: false,
                        error: "Database error."
                    });
                }

                if (existingUser) {
                    return res.status(409).json({
                        ok: false,
                        error: "That email is already being used by another account."
                    });
                }

                // ------------------------------------------------
                // UPDATE DATABASE
                // ------------------------------------------------

                db.run(
                    `
                    UPDATE users
                    SET
                        name = ?,
                        email = ?
                    WHERE id = ?
                    `,
                    [
                        newName,
                        newEmail,
                        currentUser.id
                    ],
                    function (updateErr) {
                        if (updateErr) {
                            console.error(updateErr);

                            return res.status(500).json({
                                ok: false,
                                error: "Could not update profile."
                            });
                        }

                        // ------------------------------------------------
                        // UPDATE ALL ACTIVE SESSIONS FOR THIS USER
                        // ------------------------------------------------

                        for (const [token, session] of sessions.entries()) {
                            if (session.userId === currentUser.id) {
                                sessions.set(token, {
                                    ...session,
                                    userId: currentUser.id
                                });
                            }
                        }

                        // ------------------------------------------------
                        // RETURN UPDATED USER
                        // ------------------------------------------------

                        res.json({
                            ok: true,
                            message: "Profile updated successfully.",
                            user: {
                                id: currentUser.id,
                                name: newName,
                                email: newEmail,
                                createdAt: currentUser.createdAt
                            }
                        });
                    }
                );
            }
        );
    } catch (error) {
        console.error("Profile update error:", error);

        res.status(500).json({
            ok: false,
            error: "Profile update failed."
        });
    }
});

// ============================================================
// CHANGE PASSWORD
// ============================================================

app.put("/api/auth/password", async (req, res) => {
    try {
        const currentUser = await getUserFromRequest(req);

        if (!currentUser) {
            return res.status(401).json({
                ok: false,
                error: "You must be logged in."
            });
        }

        const currentPassword = String(
            req.body.currentPassword || ""
        );

        const newPassword = String(
            req.body.newPassword || ""
        );

        if (!currentPassword || !newPassword) {
            return res.status(400).json({
                ok: false,
                error: "Current and new passwords are required."
            });
        }

        if (newPassword.length < 6) {
            return res.status(400).json({
                ok: false,
                error: "New password must be at least 6 characters."
            });
        }

        db.get(
            `
            SELECT passwordHash
            FROM users
            WHERE id = ?
            `,
            [currentUser.id],
            async (err, user) => {
                if (err || !user) {
                    return res.status(500).json({
                        ok: false,
                        error: "Could not find account."
                    });
                }

                const matches = await bcrypt.compare(
                    currentPassword,
                    user.passwordHash
                );

                if (!matches) {
                    return res.status(401).json({
                        ok: false,
                        error: "Current password is incorrect."
                    });
                }

                const newPasswordHash = await bcrypt.hash(
                    newPassword,
                    12
                );

                db.run(
                    `
                    UPDATE users
                    SET passwordHash = ?
                    WHERE id = ?
                    `,
                    [
                        newPasswordHash,
                        currentUser.id
                    ],
                    (updateErr) => {
                        if (updateErr) {
                            console.error(updateErr);

                            return res.status(500).json({
                                ok: false,
                                error: "Could not change password."
                            });
                        }

                        res.json({
                            ok: true,
                            message: "Password changed successfully."
                        });
                    }
                );
            }
        );
    } catch (error) {
        console.error("Password change error:", error);

        res.status(500).json({
            ok: false,
            error: "Password change failed."
        });
    }
});

// ============================================================
// AI API
// ============================================================

app.post("/api/ai", async (req, res) => {
    try {
        if (!OPENROUTER_API_KEY) {
            return res.status(500).json({
                ok: false,
                error: "OPENROUTER_API_KEY is missing."
            });
        }

        const prompt = String(req.body.prompt || "").trim();

        const system = String(
            req.body.system ||
            "You are Prism AI, a helpful, intelligent and creative AI assistant."
        );

        if (!prompt) {
            return res.status(400).json({
                ok: false,
                error: "Prompt is required."
            });
        }

        const response = await client.chat.completions.create({
            model: MODEL,

            messages: [
                {
                    role: "system",
                    content: system
                },
                {
                    role: "user",
                    content: prompt
                }
            ]
        });

        const answer =
            response.choices?.[0]?.message?.content ||
            "No response generated.";

        res.json({
            ok: true,
            answer
        });
    } catch (error) {
        console.error("AI error:", error);

        res.status(500).json({
            ok: false,
            error: error.message || "AI request failed."
        });
    }
});

// ============================================================
// WEB SEARCH
// ============================================================

app.post("/api/google-search", async (req, res) => {
    try {
        if (!OPENROUTER_API_KEY) {
            return res.status(500).json({
                ok: false,
                error: "OPENROUTER_API_KEY is missing."
            });
        }

        const query = String(req.body.query || "").trim();

        if (!query) {
            return res.status(400).json({
                ok: false,
                error: "Search query is required."
            });
        }

        const response = await client.chat.completions.create({
            model: MODEL,

            plugins: [
                {
                    id: "web"
                }
            ],

            messages: [
                {
                    role: "system",
                    content:
                        "You are Prism AI Research Lab. Search the web and provide accurate, useful information. Clearly distinguish facts from uncertainty."
                },
                {
                    role: "user",
                    content: query
                }
            ]
        });

        const message = response.choices?.[0]?.message || {};

        const answer =
            message.content ||
            "No search answer generated.";

        res.json({
            ok: true,
            answer,
            sources: message.annotations || [],
            results: message.web || []
        });
    } catch (error) {
        console.error("Web search error:", error);

        res.status(500).json({
            ok: false,
            error: error.message || "Web search failed."
        });
    }
});

// ============================================================
// LOGO GENERATION
// ============================================================

app.post("/api/generate-logo", async (req, res) => {
    try {
        if (!OPENROUTER_API_KEY) {
            return res.status(500).json({
                ok: false,
                error: "OPENROUTER_API_KEY is missing."
            });
        }

        const prompt = String(req.body.prompt || "").trim();

        if (!prompt) {
            return res.status(400).json({
                ok: false,
                error: "Logo prompt is required."
            });
        }

        const logoPrompt = `
Create a finished professional logo.

Logo requirements:

${prompt}

The result must be an actual finished logo, not a mockup,
not a screenshot and not a concept sheet.

Use a clean professional composition.

Transparent background.

No watermark.

No unnecessary objects.

The logo should work as a website/app brand identity.
`;

        const response = await fetch(
            "https://openrouter.ai/api/v1/images",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Authorization":
                        `Bearer ${OPENROUTER_API_KEY}`
                },

                body: JSON.stringify({
                    model: "openai/gpt-image-1",

                    prompt: logoPrompt,

                    size: "1024x1024",

                    response_format: "b64_json"
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            console.error("Logo API error:", data);

            return res.status(response.status).json({
                ok: false,
                error:
                    data?.error?.message ||
                    "Logo generation failed."
            });
        }

        const image =
            data?.data?.[0]?.b64_json ||
            data?.data?.[0]?.url;

        if (!image) {
            return res.status(500).json({
                ok: false,
                error: "No image was returned."
            });
        }

        res.json({
            ok: true,
            image
        });
    } catch (error) {
        console.error("Logo generation error:", error);

        res.status(500).json({
            ok: false,
            error:
                error.message ||
                "Logo generation failed."
        });
    }
});

// ============================================================
// STATIC WEBSITE
// ============================================================

app.use(express.static(__dirname));

// ============================================================
// 404 API HANDLER
// ============================================================

app.use("/api", (req, res) => {
    res.status(404).json({
        ok: false,
        error: "API route not found."
    });
});

// ============================================================
// SERVER
// ============================================================

app.listen(PORT, () => {
    console.log("");
    console.log("======================================");
    console.log("        PRISM AI BACKEND");
    console.log("======================================");
    console.log("");
    console.log(`🌐 http://localhost:${PORT}`);
    console.log("");
    console.log("🤖 Provider: OpenRouter");
    console.log(`🆓 Model: ${MODEL}`);
    console.log("");
    console.log("🔎 Web Search: OpenRouter Web");
    console.log("");
    console.log("🗄️ Database: SQLite");
    console.log(`📁 Database file: ${DB_FILE}`);
    console.log("");
    console.log("🔐 Authentication API: READY");
    console.log("🤖 AI API: READY");
    console.log("🔎 Web Search API: READY");
    console.log("🎨 Logo Generation API: READY");
    console.log("");
});