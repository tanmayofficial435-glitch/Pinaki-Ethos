const OpenAI = require("openai");

const client = new OpenAI({
    baseURL: "https://openrouter.ai/api/v1",
    apiKey: process.env.OPENROUTER_API_KEY
});

module.exports = async function handler(req, res) {
    res.setHeader("Content-Type", "application/json; charset=utf-8");

    if (req.method !== "POST") {
        res.setHeader("Allow", "POST");
        return res.status(405).json({ ok: false, error: "Method not allowed." });
    }

    try {
        if (!process.env.OPENROUTER_API_KEY) {
            return res.status(500).json({
                ok: false,
                error: "AI service is not configured. Add OPENROUTER_API_KEY to the deployment environment."
            });
        }

        let body = req.body;
        if (typeof body === "string") {
            try { body = JSON.parse(body); } catch { body = {}; }
        }
        body = body || {};

        const prompt = String(body.prompt || body.message || "").trim();
        const system = String(
            body.system ||
            "You are Pinaki Ethos, a helpful, intelligent and creative AI assistant. Give clear, accurate, friendly answers."
        );

        if (!prompt) {
            return res.status(400).json({ ok: false, error: "Prompt is required." });
        }

        const completion = await client.chat.completions.create({
            model: "openrouter/free",
            messages: [
                { role: "system", content: system },
                { role: "user", content: prompt }
            ]
        });

        const answer = completion.choices?.[0]?.message?.content;
        if (!answer) {
            return res.status(502).json({ ok: false, error: "The AI provider returned an empty response. Please try again." });
        }

        return res.status(200).json({ ok: true, answer });
    } catch (error) {
        console.error("Pinaki Ethos AI function error:", error);
        return res.status(502).json({
            ok: false,
            error: error?.message || "The AI service could not complete this request."
        });
    }
};
