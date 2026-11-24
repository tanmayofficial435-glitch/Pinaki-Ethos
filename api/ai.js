const PINAKI_ETHOS_KNOWLEDGE = require("./pinaki-ethos-knowledge");

module.exports = async function handler(req, res) {
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.setHeader("Cache-Control", "no-store");

    if (req.method !== "POST") {
        res.setHeader("Allow", "POST");
        return res.status(405).json({ ok: false, error: "Method not allowed." });
    }

    const workerUrl = process.env.CLOUDFLARE_WORKER_URL;
    if (!workerUrl) {
        return res.status(503).json({
            ok: false,
            error: "Pinaki Intelligence is temporarily unavailable. Please try again later."
        });
    }

    let body = req.body;
    if (typeof body === "string") {
        try { body = JSON.parse(body); } catch { body = {}; }
    }
    body = body && typeof body === "object" ? body : {};

    const prompt = String(body.prompt || body.message || "").trim();
    const baseSystem = String(
        body.system ||
        "You are Pinaki Intelligence, the intelligent assistant inside Pinaki Ethos. Give helpful, accurate, clear answers."
    );
    const system = baseSystem + "\n\n" + PINAKI_ETHOS_KNOWLEDGE;

    // Keep the creator fact exact and reliable, even if the model is uncertain.
    const normalizedQuestion = prompt.toLowerCase().replace(/[^a-z0-9\s]/g, " ");
    const asksAboutCreator =
        /\b(who|which person|name of)\b/.test(normalizedQuestion) &&
        /\b(made|make|created|creator|founded|founder|built|developed|owner|owns)\b/.test(normalizedQuestion) &&
        /\b(pinaki\s*ethos|pinaki|this platform|this website)\b/.test(normalizedQuestion);

    if (asksAboutCreator) {
        const answer = "Pinaki Ethos was founded by Mr. Tanmay Satpute, with Mr. Prajwal Gosh as co-founder. The company name is Pinaki.";
        return res.status(200).json({
            ok: true,
            response: answer,
            reply: answer,
            answer,
                    });
    }

    if (!prompt) {
        return res.status(400).json({ ok: false, error: "Please enter a message." });
    }

    try {
        // CLOUDFLARE_WORKER_URL may be either the Worker base URL or its full /api/chat URL.
        const endpoint = new URL(workerUrl);
        if (!endpoint.pathname.replace(/\/$/, "").endsWith("/api/chat")) {
            endpoint.pathname = endpoint.pathname.replace(/\/$/, "") + "/api/chat";
        }

        const upstream = await fetch(endpoint.toString(), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
                ...(process.env.PE_API_SECRET
                    ? { "Authorization": "Bearer " + process.env.PE_API_SECRET }
                    : {})
            },
            body: JSON.stringify({
                message: prompt,
                prompt,
                system,
                conversation_id: body.conversation_id || undefined,
                tool: body.tool || "chat"
            }),
            signal: AbortSignal.timeout(55000)
        });

        const raw = await upstream.text();
        let data;
        try {
            data = JSON.parse(raw);
        } catch {
            console.error("assistant service Pinaki Intelligence returned non-JSON:", upstream.status, raw.slice(0, 500));
            return res.status(502).json({
                ok: false,
                error: "Pinaki Intelligence assistant service returned an invalid response. Please try again later."
            });
        }

        if (!upstream.ok) {
            const message = data?.error || data?.message || "assistant service Pinaki Intelligence request failed.";
            console.error("assistant service Pinaki Intelligence error:", upstream.status, message);
            return res.status(upstream.status >= 400 && upstream.status < 600 ? upstream.status : 502).json({
                ok: false,
                error: String(message)
            });
        }

        const answer = data?.reply || data?.response || data?.answer ||
            data?.result?.reply || data?.result?.response || data?.choices?.[0]?.message?.content;

        if (typeof answer !== "string" || !answer.trim()) {
            console.error("assistant service Pinaki Intelligence returned no answer:", JSON.stringify(data).slice(0, 1000));
            return res.status(502).json({
                ok: false,
                error: "Pinaki Intelligence assistant service connected but returned no reply. Please try again later."
            });
        }

        return res.status(200).json({
            ok: true,
            response: answer.trim(),
            reply: answer.trim(),
            answer: answer.trim(),
            conversation_id: data?.conversation_id || data?.result?.conversation_id || null,
                    });
    } catch (error) {
        console.error("Pinaki Ethos assistant service AI connection error:", error);
        return res.status(502).json({
            ok: false,
            error: error?.name === "TimeoutError"
                ? "Pinaki Intelligence assistant service took too long to respond. Please try again."
                : error?.message || "Unable to connect to Pinaki Intelligence assistant service."
        });
    }
};
