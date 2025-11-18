# data/utils_pdf.py
import os
import tempfile
from typing import Dict, Any, List
import re
from docling.document_converter import DocumentConverter
from PIL import Image
import pandas as pd
import json
# -------------------------------------------------------------
# Helper: regex caption extraction
# -------------------------------------------------------------
def extract_captions_from_text(full_text: str) -> List[str]:
    """
    Extract figure captions from the full paper text.
    Matches variations like:
    Fig. 1, Figure 2A, FIGURE S1, figure 3: ...
    """
    pattern = re.compile(r"(?i)^(fig(?:ure)?\.?\s*[S\d]+[A-Za-z]?[.:–-]?\s+.+)")
    lines = full_text.splitlines()
    captions = []
    for line in lines:
        line = line.strip()
        match = pattern.match(line)
        if match:
            captions.append(match.group(1))
    return captions

def extract_tables_from_docling(result, full_text: str):
    """
    Try to extract structured tables from Docling.
    If none found, fallback to text-based detection.
    """
    tables = []

    # --- 1. Docling structured tables ---
    for page in getattr(result, "pages", []):
        ts = getattr(page.predictions, "tablestructure", None)
        if ts and hasattr(ts, "tables") and ts.tables:
            for t in ts.tables:
                try:
                    if hasattr(t, "cells") and t.cells:
                        df = pd.DataFrame(t.cells)
                        if not df.empty:
                            tables.append(df)
                except Exception as e:
                    print(f"[warn] Failed to parse table: {e}")

    if tables:
        return tables  # found structured tables

    # --- 2. Fallback: reconstruct tables from text blocks ---
    print("[info] No structured tables found. Trying regex-based extraction...")

    # Simple heuristic: find blocks of text with multiple columns separated by 2+ spaces or tabs
    potential_tables = re.findall(
        r"(?:\S+(?:\s{2,}|\t)\S+[^\n]*\n){2,}",  # at least 2 rows with multi-column layout
        full_text,
        flags=re.MULTILINE
    )

    for block in potential_tables:
        try:
            rows = [re.split(r"\s{2,}|\t", line.strip()) for line in block.strip().split("\n")]
            df = pd.DataFrame(rows)
            if len(df.columns) > 1:
                tables.append(df)
        except Exception as e:
            print(f"[warn] Failed to parse text table: {e}")

    return tables



def extract_text_images_tables(pdf_path: str,) -> Dict[str, Any]:
    """
    Parse a scientific PDF using Docling.

    Args:
        pdf_path: path to the PDF file.
        save_figures: whether to extract and save embedded figure images.

    Returns:
        dict with keys:
            - text: full paper text
            - tables: list of tables as pandas DataFrames
            - figures: list of dicts with caption text and file path (if saved)
    """
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    doc = getattr(result, "document", None)
    if doc is None:
        raise RuntimeError("Docling conversion failed: no document found.")
    
    # ---- 1. Text extraction ----
    text_blocks = []
    for t in getattr(doc, "texts", []):
        txt = getattr(t, "text", "").strip()
        if txt:
            text_blocks.append(txt)
    full_text = "\n".join(text_blocks)

    # ---- 2. Table extraction ----
    tables = extract_tables_from_docling(result, full_text)
    
    # ---- 3. Figure captions (regex search) ----
    captions = extract_captions_from_text(full_text)
    figures = [{"index": i, "caption": cap} for i, cap in enumerate(captions)]

    return {"text": full_text, "tables": tables, "figures": figures}



    
    
# -------------------------------------------------------------------------
# Example usage
# -------------------------------------------------------------------------
if __name__ == "__main__":
    pdf_path = "data/pdf_samples/10.48550_arXiv.2306.02901.pdf"
    parsed = extract_text_images_tables(pdf_path)

    print("\n=== TEXT PREVIEW ===")
    print(parsed["text"][:500], "...\n")

    print("=== TABLES ===")
    for i, table in enumerate(parsed["tables"]):
        print(f"\nTable {i+1}:\n", table.head())

    print("=== FIGURES ===")
    for f in parsed["figures"]:
        print(f)
    
