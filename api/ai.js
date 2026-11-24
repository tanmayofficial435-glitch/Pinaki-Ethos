module.exports = async function handler(req, res) {
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.setHeader("Cache-Control", "no-store");

    if (req.method !== "POST") {
        res.setHeader("Allow", "POST");
        return res.status(405).json({ ok: false, error: "Method not allowed." });
    }

    const readBody = () => {
        let body = req.body;
        if (typeof body === "string") {
            try { body = JSON.parse(body); } catch { body = {}; }
        }
        return body && typeof body === "object" ? body : {};
    };

    const extractText = (value) => {
        if (typeof value === "string") return value.trim();
        if (Array.isArray(value)) {
            return value.map(part => typeof part === "string" ? part : (part?.text || ""))
                .filter(Boolean).join("\n").trim();
        }
        return "";
    };

    const body = readBody();
    const prompt = String(body.prompt || body.message || "").trim();
    const system = String(
        body.system ||
        "You are Pinaki Ethos, a helpful, intelligent and creative AI assistant. Answer the user's question directly, accurately and clearly."
    );

    if (!prompt) {
        return res.status(400).json({ ok: false, error: "Please enter a message." });
    }

    const failures = [];

    // Primary provider: Gemini. This uses the existing production GEMINI_API_KEY.
    if (process.env.GEMINI_API_KEY) {
        try {
            const response = await fetch(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "x-goog-api-key": process.env.GEMINI_API_KEY
                    },
                    body: JSON.stringify({
                        systemInstruction: { parts: [{ text: system }] },
                        contents: [{ role: "user", parts: [{ text: prompt }] }],
                        generationConfig: { temperature: 0.7, maxOutputTokens: 2048 }
                    })
                }
            );

            const raw = await response.text();
            let data;
            try { data = JSON.parse(raw); } catch { data = {}; }

            if (!response.ok) {
                const message = data?.error?.message || "Gemini request failed with status " + response.status;
                failures.push("Gemini: " + message);
                console.error("Pinaki Ethos Gemini error:", response.status, message);
            } else {
                const answer = extractText(
                    data?.candidates?.[0]?.content?.parts?.map(part => part.text || "")
                );
                if (answer) {
                    return res.status(200).json({ ok: true, answer, provider: "gemini" });
                }
                const reason = data?.promptFeedback?.blockReason ||
                    data?.candidates?.[0]?.finishReason ||
                    "No text content returned";
                failures.push("Gemini: " + reason);
                console.error("Pinaki Ethos Gemini empty response:", reason, JSON.stringify(data).slice(0, 1200));
            }
        } catch (error) {
            failures.push("Gemini: " + (error?.message || "Network error"));
            console.error("Pinaki Ethos Gemini connection error:", error);
        }
    } else {
        failures.push("Gemini: GEMINI_API_KEY is not configured");
    }

    // Fallback provider: OpenRouter.
    if (process.env.OPENROUTER_API_KEY) {
        try {
            const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
                method: "POST",
                headers: {
                    "Authorization": "Bearer " + process.env.OPENROUTER_API_KEY,
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://pinaki-ethos.vercel.app",
                    "X-Title": "Pinaki Ethos"
                },
                body: JSON.stringify({
                    model: "openrouter/free",
                    messages: [
                        { role: "system", content: system },
                        { role: "user", content: prompt }
                    ],
                    max_tokens: 2048
                })
            });

            const raw = await response.text();
            let data;
            try { data = JSON.parse(raw); } catch { data = {}; }

            if (!response.ok) {
                const message = data?.error?.message || "OpenRouter request failed with status " + response.status;
                failures.push("OpenRouter: " + message);
                console.error("Pinaki Ethos OpenRouter error:", response.status, message);
            } else {
                const message = data?.choices?.[0]?.message || {};
                const answer = extractText(message.content) || extractText(message.reasoning);
                if (answer) {
                    return res.status(200).json({ ok: true, answer, provider: "openrouter" });
                }
                const reason = data?.choices?.[0]?.finish_reason || "No text content returned";
                failures.push("OpenRouter: " + reason);
                console.error("Pinaki Ethos OpenRouter empty response:", reason, JSON.stringify(data).slice(0, 1200));
            }
        } catch (error) {
            failures.push("OpenRouter: " + (error?.message || "Network error"));
            console.error("Pinaki Ethos OpenRouter connection error:", error);
        }
    } else {
        failures.push("OpenRouter: OPENROUTER_API_KEY is not configured");
    }

    return res.status(502).json({
        ok: false,
        error: "Pinaki Ethos could not get a response from its AI providers. " + failures.join(" | ")
    });
};
