# Autonomous Conversational EDA Workspace

An interactive Flask web application where non-technical users can upload `.csv` or `.xlsx`
datasets, get an automated `ydata-profiling` statistical report, and converse with a
LangChain-powered AI agent to clean data, run analyses, and generate charts — all from
a browser, no coding required.

---

## 📁 Project Structure

```
project/
├── app.py                        # Flask app & all API route handlers
├── requirements.txt              # All Python dependencies (fully pinned)
├── .env.example                  # Template for your environment variables
├── .env                          # Your actual secrets — never commit this!
│
├── utils/                        # Backend Python modules
│   ├── __init__.py
│   ├── agent.py                  # LangChain AI agent (Groq / OpenAI / Gemini)
│   ├── data_manager.py           # Secure upload, storage & cleaning per session
│   └── profiler.py               # ydata-profiling HTML report generator
│
├── templates/
│   └── index.html                # Main UI (tabbed: Upload / Profile / Chat)
│
├── static/
│   ├── css/
│   │   └── style.css             # Dark-theme stylesheet
│   ├── js/
│   │   └── main.js               # Drag-drop upload, table preview, chat logic
│   ├── charts/                   # Auto-generated chart PNGs (created at runtime)
│   └── reports/                  # Auto-generated profiling HTML (created at runtime)
│
└── uploads/                      # Per-session uploaded datasets (created at runtime)
    └── <session_id>/
        ├── <uuid>.csv / .xlsx    # Original uploaded file
        └── active_dataset.csv    # Cleaned/canonical working copy
```

---

## ⚙️ Setup Instructions

### 1. Prerequisites
- Python **3.12** (recommended — 3.13/3.14 may lack prebuilt wheels for scipy/numba)
- Download from https://www.python.org/downloads/ if needed

### 2. Clone / download the project
```
project/
├── app.py
├── requirements.txt
├── .env.example
├── utils/
├── templates/
└── static/
```

### 3. Create a virtual environment with Python 3.12
```bash
cd "C:\path\to\project"
py -3.12 -m venv venv
venv\Scripts\activate
```

### 4. Install dependencies (order matters!)
```bash
pip install --upgrade pip
pip install setuptools
pip install -r requirements.txt
```
> ⚠️ Always install `setuptools` first — `ydata-profiling` imports `pkg_resources`
> (part of setuptools) at startup before pip's dependency resolver can catch it.

### 5. Get a free Groq API key
1. Go to https://console.groq.com
2. Sign up (free, no credit card needed)
3. Navigate to **API Keys → Create Key**
4. Copy the key

### 6. Configure your environment
Copy `.env.example` to `.env` and fill in your values:
```bash
copy .env.example .env
```

Edit `.env`:
```
FLASK_SECRET_KEY=any-long-random-string-here
MAX_UPLOAD_MB=50

LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-key-here
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## 🚀 Running the App

```bash
venv\Scripts\activate
python app.py
```

Open your browser at: **http://localhost:5000**

For production use gunicorn (Linux/Mac):
```bash
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

---

## 🔌 Supported LLM Providers

Change `LLM_PROVIDER` in `.env` to switch — no code changes needed.

| Provider  | Cost        | Key Source                              | .env setting         |
|-----------|-------------|-----------------------------------------|----------------------|
| **Groq**  | ✅ Free      | https://console.groq.com               | `LLM_PROVIDER=groq`  |
| OpenAI    | 💳 Paid      | https://platform.openai.com/api-keys   | `LLM_PROVIDER=openai`|
| Gemini    | ✅ Free tier | https://aistudio.google.com/app/apikey | `LLM_PROVIDER=gemini`|

### Groq `.env`
```
LLM_PROVIDER=groq
GROQ_API_KEY=your-key
GROQ_MODEL=llama-3.3-70b-versatile
```

### OpenAI `.env`
```
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4o-mini
```

### Gemini `.env`
```
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your-key
GEMINI_MODEL=gemini-1.5-flash
```
Install extra package for Gemini:
```bash
pip install langchain-google-genai
```

---

## 🌐 API Endpoints

| Method | Endpoint           | Description                                      |
|--------|--------------------|--------------------------------------------------|
| GET    | `/`                | Serves the main UI                               |
| POST   | `/api/upload`      | Upload a `.csv` or `.xlsx` file                  |
| GET    | `/api/preview`     | Get first 50 rows of the active dataset          |
| POST   | `/api/clean`       | Apply deterministic cleaning (dedup, fill NA)    |
| POST   | `/api/profile`     | Generate ydata-profiling HTML report             |
| GET    | `/reports/<file>`  | Serve a generated profiling report               |
| POST   | `/api/chat`        | Send a natural language question to the AI agent |
| POST   | `/api/reset`       | Clear session data and start fresh               |

---

## 💬 Example Chat Questions

**Basic info**
```
What is the shape of the dataset?
Show me summary statistics of all columns
How many missing values are in each column?
```

**Visualizations**
```
Plot the distribution of salary
Show me a heatmap of the correlation matrix
Create a bar chart of sales by region
Plot a boxplot of price grouped by category
```

**Analysis**
```
Which columns are most correlated with each other?
Show me the top 5 highest revenue rows
Group by country and show average sales
What is the trend of orders over time?
```

---

## 🔧 Troubleshooting

| Error | Fix |
|-------|-----|
| `No module named 'pkg_resources'` | `pip install setuptools` |
| `No module named 'langchain_core.pydantic_v1'` | Wipe venv, reinstall — mixed LangChain versions |
| `pandas` fails to install (build error) | Use Python 3.12 not 3.13/3.14 |
| `429 quota exceeded` | Switch to Groq (free) via `LLM_PROVIDER=groq` |
| `401 invalid api key` | Check `.env` — key must match your provider |
| Agent gives wrong answers | Be more specific; include exact column names |

---

## 🔒 Security Notes

- Filenames sanitized with `secure_filename`; only `.csv`/`.xlsx`/`.xls` accepted
- Each session's files are isolated in `uploads/<session_id>/` — users cannot access each other's data
- Upload size capped via `MAX_UPLOAD_MB` in `.env` (default 50MB)
- **Never hardcode API keys in `app.py`** — use `.env` only
- **Never commit `.env` to git** — add it to `.gitignore`
- Set a strong random `FLASK_SECRET_KEY` in production