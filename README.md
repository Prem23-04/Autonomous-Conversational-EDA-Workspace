# Project Descriptions — Autonomous Conversational EDA Workspace

---

## 1. GitHub README Intro (paste at the top of your README.md)

# 🤖 Autonomous Conversational EDA Workspace

> Upload any dataset. Ask questions in plain English. Get instant insights, charts, and statistical reports — no coding required.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?logo=flask)
![LangChain](https://img.shields.io/badge/LangChain-0.3-green)
![Groq](https://img.shields.io/badge/Groq-Free_API-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

An end-to-end, production-ready **AI-powered Exploratory Data Analysis platform** built
with Flask, LangChain, and ydata-profiling. Non-technical users can upload raw `.csv` or
`.xlsx` datasets and interact with an intelligent AI agent through a ChatGPT-style
interface to clean data, generate visualizations, and uncover statistical insights —
entirely through natural language, with zero code.

### ✨ Key Features
- 📂 **Drag-and-drop upload** for `.csv` and `.xlsx` files (up to 50MB)
- 📊 **Automated profiling report** — one-click ydata-profiling HTML report with
  distributions, correlations, missing value analysis, and more
- 💬 **Conversational AI agent** — ask data questions in plain English; the agent
  writes and executes pandas/matplotlib code and returns text answers or rendered charts
- 🧹 **Quick Clean panel** — drop duplicates, fill missing values with mean/median/drop
  in one click
- 🔌 **Multi-provider LLM support** — switch between Groq (free), OpenAI, or Google
  Gemini by changing one line in `.env`
- 🔒 **Session-isolated storage** — each user's data is sandboxed in its own directory
- 🌑 **Dark-mode UI** — clean, responsive interface built with vanilla HTML/CSS/JS

---

## 2. GitHub Repository Description (the one-liner under your repo name)

AI-powered Flask web app for Exploratory Data Analysis — upload CSV/Excel datasets and chat with an LLM agent to get visualizations, statistical insights, and data cleaning in plain English. Powered by LangChain, Groq, ydata-profiling, and pandas.

---

## 3. GitHub Topics / Tags (add these to your repo)

flask, python, langchain, exploratory-data-analysis, data-science, pandas, 
ydata-profiling, groq, llm, ai-agent, matplotlib, seaborn, natural-language-processing,
machine-learning, data-visualization, chatbot, openai, full-stack, web-app, eda

---

## 4. LinkedIn Post

🚀 Excited to share my latest project — the Autonomous Conversational EDA Workspace!

As data scientists, we spend 80% of our time just understanding and cleaning raw data
before any real analysis begins. I built a tool to change that.

🔍 What it does:
Upload any .csv or .xlsx dataset and ask questions about it in plain English — like
talking to a senior data scientist.

💡 Key highlights:
✅ AI-powered chat interface (LangChain + Groq/OpenAI/Gemini)
✅ Automated statistical profiling reports (ydata-profiling)
✅ Dynamic chart generation — histograms, heatmaps, scatter plots, bar charts
✅ One-click data cleaning — remove duplicates, handle missing values
✅ Secure, session-isolated file handling
✅ Clean dark-mode UI — no frameworks, pure HTML/CSS/JS
✅ Multi-LLM support — swap providers in one line

🛠 Tech Stack:
Backend: Python, Flask, LangChain, pandas, ydata-profiling
AI Layer: Groq (Llama 3.3), OpenAI (GPT-4o-mini), Google Gemini
Frontend: Vanilla HTML, CSS, JavaScript
Visualization: Matplotlib, Seaborn, Plotly

This project bridges the gap between raw data and actionable insights — making EDA
accessible to non-technical users while being powerful enough for data professionals.

🔗 GitHub: [your-github-link]

I'd love your feedback! Drop a comment or connect if you're working on similar
AI + data science tooling. 🙌

#DataScience #ArtificialIntelligence #MachineLearning #Python #Flask #LangChain
#EDA #DataAnalysis #OpenAI #Groq #FullStack #BuildInPublic #DataEngineering

---

## 5. Resume Bullet Points

### Option A — For a Data Science / ML role:
**Autonomous Conversational EDA Workspace** | Python, Flask, LangChain, Groq, pandas
- Built a production-ready AI-powered web platform enabling non-technical users to
  perform full exploratory data analysis on CSV/Excel datasets through a natural
  language chat interface, eliminating the need for manual coding
- Engineered a LangChain pandas dataframe agent backed by Groq's Llama 3.3 70B model
  that translates natural language queries into executable pandas/matplotlib code,
  dynamically generating statistical summaries and visualizations in real time
- Integrated ydata-profiling to auto-generate comprehensive HTML reports covering
  distributions, correlations, missing value analysis, and data type inference on upload
- Implemented secure, session-isolated file management with per-user sandboxed storage,
  input validation, and configurable upload size limits using Flask and Werkzeug
- Designed a responsive dark-mode frontend (HTML/CSS/JS) with drag-and-drop upload,
  embedded report iframe, and a ChatGPT-style chat interface serving rendered chart PNGs

### Option B — For a Full Stack / Software Engineering role:
**Autonomous Conversational EDA Workspace** | Flask, LangChain, Python, Vanilla JS
- Architected and delivered a full-stack AI web application with a Flask REST API
  backend and a responsive vanilla JS frontend, supporting multi-provider LLM
  integration (Groq, OpenAI, Gemini) configurable via environment variables
- Designed RESTful API endpoints for file upload, data profiling, AI chat, dataset
  cleaning, and session management with robust error handling and input sanitization
- Built a session-scoped data pipeline using pandas for secure CSV/Excel ingestion,
  canonical storage, and deterministic cleaning operations exposed via dedicated endpoints
- Implemented dynamic chart capture by intercepting matplotlib plt.savefig() calls
  from LLM-generated code, serving chart PNGs as static assets back to the chat UI

### Option C — One-liner for a skills/projects list:
AI-powered EDA web app (Flask + LangChain + Groq) — natural language interface for
dataset analysis, automated profiling reports, and dynamic chart generation.

---

## 6. Project Tagline (for portfolio websites)

"Talk to your data. Upload a dataset, ask questions in plain English,
and get instant charts, statistics, and insights — powered by AI."
