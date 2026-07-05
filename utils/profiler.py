"""
profiler.py
-----------
Generates a ydata-profiling HTML report for a session's active dataframe.
"""
import os
from ydata_profiling import ProfileReport


def generate_profile_report(df, output_dir: str, session_id: str, minimal: bool = False) -> str:
    """Generates an HTML profiling report and returns its filename
    (relative to the reports static directory)."""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"profile_{session_id}.html"
    output_path = os.path.join(output_dir, filename)

    # `minimal=True` skips expensive correlation/interaction computations -
    # useful as an automatic fallback for very large datasets.
    profile = ProfileReport(
        df,
        title="Automated EDA Profiling Report",
        explorative=not minimal,
        minimal=minimal,
        progress_bar=False,
    )
    profile.to_file(output_path)
    return filename
