const crypto = require("crypto");

const COOKIE_NAME = "__Host-pe_admin_session";
const SESSION_TTL_SECONDS = 8 * 60 * 60;

function sendSecurityHeaders(res) {
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.setHeader("Cache-Control", "no-store, no-cache, must-revalidate, private");
    res.setHeader("Pragma", "no-cache");
    res.setHeader("X-Content-Type-Options", "nosniff");
    res.setHeader("Referrer-Policy", "no-referrer");
}

function getCookie(req, name) {
    const cookieHeader = String(req.headers.cookie || "");
    for (const part of cookieHeader.split(";")) {
        const separator = part.indexOf("=");
        if (separator < 0) continue;
        const key = part.slice(0, separator).trim();
        if (key === name) return part.slice(separator + 1).trim();
    }
    return "";
}

function isConfigured() {
    return Boolean(
        process.env.ADMIN_PASSWORD &&
        process.env.ADMIN_PASSWORD.length >= 24 &&
        process.env.ADMIN_SESSION_SECRET &&
        process.env.ADMIN_SESSION_SECRET.length >= 64
    );
}

function signTimestamp(timestamp) {
    return crypto
        .createHmac("sha256", process.env.ADMIN_SESSION_SECRET)
        .update(timestamp)
        .digest("base64url");
}

function createSessionToken() {
    const timestamp = String(Date.now());
    return timestamp + "." + signTimestamp(timestamp);
}

function hasValidSession(req) {
    if (!isConfigured()) return false;

    const token = getCookie(req, COOKIE_NAME);
    const parts = token.split(".");
    if (parts.length !== 2) return false;

    const [timestamp, receivedSignature] = parts;
    if (!/^\d{13}$/.test(timestamp) || !receivedSignature) return false;

    const expectedSignature = signTimestamp(timestamp);
    const expected = Buffer.from(expectedSignature);
    const received = Buffer.from(receivedSignature);

    if (expected.length !== received.length) return false;
    if (!crypto.timingSafeEqual(expected, received)) return false;

    const issuedAt = Number(timestamp);
    const age = Date.now() - issuedAt;

    return Number.isSafeInteger(issuedAt) &&
        age >= -60_000 &&
        age <= SESSION_TTL_SECONDS * 1000;
}

function isSameOriginRequest(req) {
    const origin = req.headers.origin;
    const forwardedHost = req.headers["x-forwarded-host"];
    const requestHost = String(forwardedHost || req.headers.host || "")
        .split(",")[0]
        .trim()
        .toLowerCase();

    if (!origin || !requestHost) return false;

    try {
        const parsedOrigin = new URL(origin);
        const secureProtocol = parsedOrigin.protocol === "https:";
        const localDevelopment =
            parsedOrigin.protocol === "http:" &&
            (parsedOrigin.hostname === "localhost" || parsedOrigin.hostname === "127.0.0.1");

        return parsedOrigin.host.toLowerCase() === requestHost &&
            (secureProtocol || localDevelopment);
    } catch {
        return false;
    }
}

function setSessionCookie(res, token) {
    res.setHeader(
        "Set-Cookie",
        COOKIE_NAME + "=" + token +
        "; Path=/; Max-Age=" + SESSION_TTL_SECONDS +
        "; HttpOnly; Secure; SameSite=Strict"
    );
}

function clearSessionCookie(res) {
    res.setHeader(
        "Set-Cookie",
        COOKIE_NAME + "=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Strict"
    );
}

function readBody(req) {
    if (req.body && typeof req.body === "object") return req.body;
    if (typeof req.body === "string") {
        try {
            const parsed = JSON.parse(req.body);
            return parsed && typeof parsed === "object" ? parsed : {};
        } catch {
            return {};
        }
    }
    return {};
}

function safePasswordMatch(candidate) {
    const expectedPassword = process.env.ADMIN_PASSWORD || "";
    const suppliedDigest = crypto.createHash("sha256").update(candidate).digest();
    const expectedDigest = crypto.createHash("sha256").update(expectedPassword).digest();
    return crypto.timingSafeEqual(suppliedDigest, expectedDigest);
}

module.exports = async function handler(req, res) {
    sendSecurityHeaders(res);

    if (!["GET", "POST", "DELETE"].includes(req.method)) {
        res.setHeader("Allow", "GET, POST, DELETE");
        return res.status(405).json({ ok: false, error: "Method not allowed." });
    }

    if (req.method === "GET") {
        if (!isConfigured()) {
            // A missing setup secret is an expected first-run state, not a failed network request.
            return res.status(200).json({
                ok: true,
                configured: false,
                authenticated: false,
                error: "Management access is not configured yet. Add ADMIN_PASSWORD and ADMIN_SESSION_SECRET in Vercel Project Settings."
            });
        }

        const authenticated = hasValidSession(req);
        return res.status(200).json({
            ok: true,
            configured: true,
            authenticated,
            ...(authenticated ? {
                sessionExpiresIn: SESSION_TTL_SECONDS,
                environment: process.env.VERCEL_ENV || "production",
                services: {
                    aiBackend: Boolean(process.env.CLOUDFLARE_WORKER_URL),
                    supabaseAuth: Boolean(
                        process.env.SUPABASE_URL &&
                        process.env.SUPABASE_PUBLISHABLE_KEY
                    )
                }
            } : {})
        });
    }

    if (!isSameOriginRequest(req)) {
        return res.status(403).json({ ok: false, error: "Request origin was not accepted." });
    }

    if (req.method === "DELETE") {
        clearSessionCookie(res);
        return res.status(200).json({ ok: true, message: "Management session ended." });
    }

    if (!isConfigured()) {
        return res.status(503).json({
            ok: false,
            error: "The management portal is not configured."
        });
    }

    const body = readBody(req);
    const password = typeof body.password === "string" ? body.password : "";

    if (!password || password.length > 4096 || !safePasswordMatch(password)) {
        return res.status(401).json({
            ok: false,
            error: "The management password is incorrect."
        });
    }

    setSessionCookie(res, createSessionToken());
    return res.status(200).json({ ok: true, authenticated: true });
};
