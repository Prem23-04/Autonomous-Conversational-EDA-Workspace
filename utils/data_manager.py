"""
data_manager.py
----------------
Handles secure, session-isolated storage and loading of uploaded datasets.
Each session gets its own subdirectory under UPLOAD_ROOT so users can never
see or overwrite each other's files.
"""
import os
import uuid
import pandas as pd
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}
MAX_ROWS_PREVIEW = 50


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class DataManager:
    """Manages a single session's dataset lifecycle on disk."""

    def __init__(self, upload_root: str, session_id: str):
        self.session_dir = os.path.join(upload_root, session_id)
        os.makedirs(self.session_dir, exist_ok=True)

    def save_upload(self, file_storage) -> dict:
        """Validates and persists an uploaded file. Returns metadata dict."""
        filename = secure_filename(file_storage.filename or "")
        if not filename:
            raise ValueError("Invalid filename.")
        if not allowed_file(filename):
            raise ValueError("Unsupported file type. Please upload .csv or .xlsx.")

        # Give every upload a unique on-disk name to avoid collisions,
        # but keep the original name for display purposes.
        ext = filename.rsplit(".", 1)[1].lower()
        stored_name = f"{uuid.uuid4().hex}.{ext}"
        stored_path = os.path.join(self.session_dir, stored_name)
        file_storage.save(stored_path)

        try:
            df = self._read_dataframe(stored_path, ext)
        except Exception as e:
            os.remove(stored_path)
            raise ValueError(f"Could not parse file: {e}")

        # Persist a canonicalized copy as parquet-free CSV for fast reload,
        # and cache the path so the agent can reload fresh each turn.
        clean_csv_path = os.path.join(self.session_dir, "active_dataset.csv")
        df.to_csv(clean_csv_path, index=False)

        return {
            "original_filename": filename,
            "stored_path": stored_path,
            "active_csv_path": clean_csv_path,
            "n_rows": int(df.shape[0]),
            "n_cols": int(df.shape[1]),
            "columns": list(df.columns.astype(str)),
        }

    @staticmethod
    def _read_dataframe(path: str, ext: str) -> pd.DataFrame:
        if ext == "csv":
            df = pd.read_csv(path, low_memory=False)
        else:
            df = pd.read_excel(path)
        if df.empty:
            raise ValueError("Uploaded file contains no data.")
        return df

    def load_active_dataframe(self) -> pd.DataFrame:
        path = os.path.join(self.session_dir, "active_dataset.csv")
        if not os.path.exists(path):
            raise FileNotFoundError("No active dataset found for this session.")
        return pd.read_csv(path, low_memory=False)

    def preview(self, n=MAX_ROWS_PREVIEW) -> dict:
        df = self.load_active_dataframe()
        head = df.head(n)
        return {
            "columns": list(head.columns.astype(str)),
            "rows": head.astype(object).where(pd.notnull(head), None).values.tolist(),
            "dtypes": {c: str(t) for c, t in df.dtypes.items()},
            "shape": list(df.shape),
        }

    def basic_clean(self, drop_duplicates=True, fillna_strategy="none") -> dict:
        """A safe, deterministic cleaning pass exposed via a dedicated endpoint
        (kept separate from the freeform agent for predictability)."""
        df = self.load_active_dataframe()
        before = df.shape[0]
        if drop_duplicates:
            df = df.drop_duplicates()
        if fillna_strategy == "mean":
            numeric_cols = df.select_dtypes(include="number").columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        elif fillna_strategy == "median":
            numeric_cols = df.select_dtypes(include="number").columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        elif fillna_strategy == "drop":
            df = df.dropna()

        active_csv_path = os.path.join(self.session_dir, "active_dataset.csv")
        df.to_csv(active_csv_path, index=False)
        return {
            "rows_before": before,
            "rows_after": df.shape[0],
            "shape": list(df.shape),
        }
