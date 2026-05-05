from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover - optional dependency guard
    PdfReader = None


@dataclass(frozen=True)
class DocumentChunk:
    source: str
    chunk_id: int
    text: str


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_pdf(path: Path) -> str:
    if PdfReader is None:
        return ""
    reader = PdfReader(str(path))
    pages: list[str] = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def _read_hwpx(path: Path) -> str:
    """Best-effort HWPX text extraction.

    HWPX is a zip package containing XML files. This function extracts text nodes
    from XML files. Some documents may need additional namespace-specific parsing.
    """
    texts: list[str] = []
    try:
        with zipfile.ZipFile(path) as zf:
            xml_names = [name for name in zf.namelist() if name.lower().endswith(".xml")]
            for name in xml_names:
                try:
                    root = ET.fromstring(zf.read(name))
                except Exception:
                    continue
                for node in root.iter():
                    if node.text and node.text.strip():
                        texts.append(node.text.strip())
    except zipfile.BadZipFile:
        return ""
    return "\n".join(texts)


def read_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".csv", ".json"}:
        return _read_text_file(path)
    if suffix == ".pdf":
        return _read_pdf(path)
    if suffix == ".hwpx":
        return _read_hwpx(path)
    return ""


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100) -> list[str]:
    cleaned = _clean_text(text)
    if not cleaned:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(cleaned):
            break
        start = max(0, end - overlap)
    return chunks


def load_documents(paths: Iterable[Path], chunk_size: int = 700, overlap: int = 100) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for path in paths:
        if not path.is_file():
            continue
        text = read_document(path)
        for idx, chunk in enumerate(chunk_text(text, chunk_size=chunk_size, overlap=overlap)):
            chunks.append(DocumentChunk(source=path.name, chunk_id=idx, text=chunk))
    return chunks


def load_documents_from_dir(directory: str | Path) -> list[DocumentChunk]:
    directory = Path(directory)
    supported = {".txt", ".md", ".csv", ".json", ".pdf", ".hwpx"}
    paths = [path for path in directory.rglob("*") if path.suffix.lower() in supported]
    return load_documents(paths)
