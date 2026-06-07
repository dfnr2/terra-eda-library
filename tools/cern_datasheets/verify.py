"""Exact datasheet verification: confirm MPN + CERN params appear in PDF text."""
from __future__ import annotations

from pathlib import Path
from typing import List


def check_text(text: str, mpn: str, params: List[str]) -> str:
    """Return one of: ok | unparseable | mpn_mismatch | param_missing."""
    if not text or not text.strip():
        return "unparseable"
    norm = text.upper()
    if mpn.upper() not in norm:
        return "mpn_mismatch"
    for p in params:
        if p and p.upper() not in norm:
            return "param_missing"
    return "ok"


def extract_text(pdf_path: Path) -> str:
    """Extract text from a PDF. Returns '' if it cannot be parsed."""
    try:
        from pypdf import PdfReader  # lazy import; add as dep when fetching
    except ImportError:  # pragma: no cover
        raise RuntimeError("pypdf not installed; run: uv add --dev pypdf")
    try:
        reader = PdfReader(str(pdf_path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:
        return ""


def verify_pdf(pdf_path: Path, mpn: str, params: List[str]) -> str:
    return check_text(extract_text(pdf_path), mpn, params)
