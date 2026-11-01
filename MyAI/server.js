const express = require("express");
const cors = require("cors");

const app = express();
const PORT = 4000;

app.use(cors());
app.use(express.json());

// Serve your My AI website
app.use(express.static(__dirname));

// Chat endpoint
app.post("/api/chat", (req, res) => {
    const { message } = req.body;

    if (!message) {
        return res.status(400).json({
            error: "No message received."
        });
    }

    // Temporary response.
    // We will replace this with your own AI model.
    const reply = `You said: ${message}`;

    res.json({
        reply: reply
    });
});

app.listen(PORT, () => {
    console.log("=================================");
    console.log("🧠 MY AI");
    console.log("=================================");
    console.log(`🚀 http://localhost:${PORT}`);
    console.log("=================================");
});