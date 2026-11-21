# AI Chatbot

A simple, fast AI chatbot built with **FastAPI** and the **Groq API**, featuring real-time word-by-word replies and a clean web interface.

🔗 **Live Demo:** *(https://ai-chatbot-by-sm.onrender.com/)*

---

## What It Does

- **Real-Time Replies:** Streams answers smoothly as the AI generates them.
- **Remembers Context:** Keeps track of your conversation so you can ask follow-up questions.
- **Simple Web UI:** Clean, distraction-free chat window with a **New Chat** button to reset the conversation.
- **Built-in API Docs:** Test the backend endpoints directly at `/docs`.

---

## Project Folder Guide


ai_chatbot/
├── app/
│   ├── main.py          # Backend server & chat logic
│   └── schemas.py       # Input/output data rules
├── frontend/
│   └── index.html       # Web chat interface
├── experiments/         # Early practice scripts (sm1 - sm4)
├── .env.example         # Template for your API key
├── requirements.txt     # Python libraries needed
└── README.md