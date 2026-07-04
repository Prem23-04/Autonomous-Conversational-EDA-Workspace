# Project Descriptions — Autonomous Conversational EDA Workspace

---
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
