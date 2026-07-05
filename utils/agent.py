"""
agent.py
--------
Wraps a LangChain pandas dataframe agent supporting multiple LLM providers:
  - Groq  (FREE tier - recommended: llama-3.3-70b-versatile)
  - OpenAI (paid: gpt-4o-mini, gpt-4o)
  - Google Gemini (FREE tier: gemini-1.5-flash)

Set LLM_PROVIDER in .env to switch providers.
"""
import os
import re
import uuid
import contextlib
import io

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

CHARTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

SAFE_GLOBALS = {
    "pd": pd,
    "plt": plt,
    "sns": sns,
    "__builtins__": {
        "len": len, "range": range, "min": min, "max": max, "sum": sum,
        "sorted": sorted, "list": list, "dict": dict, "set": set,
        "float": float, "int": int, "str": str, "round": round,
        "enumerate": enumerate, "zip": zip, "abs": abs,
    },
}


class AgentError(Exception):
    pass


def _build_llm():
    """
    Reads LLM_PROVIDER from environment and returns the appropriate LangChain
    chat model. Defaults to Groq if no provider is specified.

    Supported values for LLM_PROVIDER:
      groq    -> uses GROQ_API_KEY   (free tier available)
      openai  -> uses OPENAI_API_KEY (paid)
      gemini  -> uses GOOGLE_API_KEY (free tier available)
    """
    provider = os.environ.get("LLM_PROVIDER", "groq").lower().strip()

    if provider == "groq":
        try:
            from langchain_groq import ChatGroq
        except ImportError:
            raise AgentError(
                "langchain-groq is not installed. Run: pip install langchain-groq"
            )
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise AgentError(
                "GROQ_API_KEY is not set. Get a free key at https://console.groq.com "
                "and add it to your .env file."
            )
        model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        return ChatGroq(model=model, temperature=0, api_key=api_key)

    elif provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise AgentError(
                "langchain-openai is not installed. Run: pip install langchain-openai"
            )
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise AgentError(
                "OPENAI_API_KEY is not set. Add it to your .env file."
            )
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        return ChatOpenAI(model=model, temperature=0, api_key=api_key)

    elif provider == "gemini":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            raise AgentError(
                "langchain-google-genai is not installed. "
                "Run: pip install langchain-google-genai"
            )
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        if not api_key:
            raise AgentError(
                "GOOGLE_API_KEY is not set. Get a free key at "
                "https://aistudio.google.com/app/apikey and add it to your .env file."
            )
        model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        return ChatGoogleGenerativeAI(model=model, temperature=0, google_api_key=api_key)

    else:
        raise AgentError(
            f"Unknown LLM_PROVIDER '{provider}'. "
            "Choose one of: groq, openai, gemini"
        )


class EDAAgent:
    """Session-scoped pandas dataframe agent with chart capture."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.llm = _build_llm()

        # Groq/Gemini don't support OPENAI_FUNCTIONS agent type — use
        # ZERO_SHOT_REACT_DESCRIPTION instead (works for all providers).
        provider = os.environ.get("LLM_PROVIDER", "groq").lower()
        agent_type = (
            AgentType.OPENAI_FUNCTIONS
            if provider == "openai"
            else AgentType.ZERO_SHOT_REACT_DESCRIPTION
        )

        self.agent = create_pandas_dataframe_agent(
            self.llm,
            self.df,
            verbose=False,
            agent_type=agent_type,
            allow_dangerous_code=True,
            max_iterations=8,
            handle_parsing_errors=True,
        )

    def ask(self, question: str) -> dict:
        """Run a natural language question, return text or chart result."""
        chart_id = uuid.uuid4().hex
        chart_path = os.path.join(CHARTS_DIR, f"{chart_id}.png")

        augmented_question = (
            f"{question}\n\n"
            "Instructions: If the user is asking for a chart/plot/visualization, "
            f"create it with matplotlib or seaborn and save it with "
            f"plt.savefig(r'{chart_path}', bbox_inches='tight', dpi=120) "
            "instead of plt.show(). Always finish with a short, plain-English "
            "summary of the result as your final answer."
        )

        plt.close("all")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                result = self.agent.invoke({"input": augmented_question})
            answer_text = (
                result.get("output", "").strip()
                if isinstance(result, dict)
                else str(result)
            )
        except Exception as e:
            raise AgentError(self._friendly_error(e))

        if os.path.exists(chart_path) and os.path.getsize(chart_path) > 0:
            return {
                "type": "chart",
                "content": answer_text or "Here is the chart you requested.",
                "chart_url": f"/static/charts/{chart_id}.png",
            }

        return {
            "type": "text",
            "content": answer_text or "I couldn't generate a response. Try rephrasing.",
        }

    @staticmethod
    def _friendly_error(e: Exception) -> str:
        msg = re.sub(r"\s+", " ", str(e)).strip()
        # Surface quota/auth errors clearly instead of hiding them
        if "429" in msg or "quota" in msg.lower():
            return (
                "API quota exceeded. Please check your plan/billing at your LLM "
                "provider, or switch to a free provider (Groq) by setting "
                "LLM_PROVIDER=groq in your .env file."
            )
        if "401" in msg or "invalid api key" in msg.lower() or "authentication" in msg.lower():
            return (
                "Invalid API key. Please check the key in your .env file matches "
                "what your provider issued."
            )
        if len(msg) > 300:
            msg = msg[:300] + "..."
        return f"The agent could not complete that request: {msg}"


def run_sandboxed_snippet(code: str, df: pd.DataFrame) -> str:
    """Sandboxed exec for vetted code snippets (debug/advanced use)."""
    forbidden = [r"\bimport\b", r"\bopen\(", r"\bexec\(", r"\beval\(",
                 r"__\w+__", r"\bos\.", r"\bsys\.", r"subprocess"]
    for pat in forbidden:
        if re.search(pat, code):
            raise AgentError("Code contains a disallowed operation.")
    local_ns = {"df": df.copy()}
    try:
        exec(code, dict(SAFE_GLOBALS), local_ns)   # noqa: S102
    except Exception as e:
        raise AgentError(f"Execution failed: {e}")
    return str(local_ns.get("result", "Code executed successfully."))