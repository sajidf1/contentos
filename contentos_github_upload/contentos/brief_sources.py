"""Extract plain-text creative direction from user-provided files or public Google Docs."""
from io import BytesIO
import re
from urllib.parse import urlparse

from docx import Document
from pypdf import PdfReader

MAX_BYTES = 8 * 1024 * 1024
MAX_CHARS = 12000


class BriefSourceError(ValueError):
    pass


def extract_upload(upload) -> str:
    name = upload.name.lower()
    data = upload.getvalue()
    if not data or len(data) > MAX_BYTES:
        raise BriefSourceError("Upload must be nonempty and no larger than 8 MB.")
    try:
        if name.endswith(".pdf"):
            reader = PdfReader(BytesIO(data))
            if len(reader.pages) > 50:
                raise BriefSourceError("PDFs must be 50 pages or fewer.")
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif name.endswith(".docx"):
            doc = Document(BytesIO(data))
            text = "\n".join([p.text for p in doc.paragraphs] +
                             [cell.text for table in doc.tables for row in table.rows for cell in row.cells])
        elif name.endswith(".doc"):
            raise BriefSourceError("Legacy .doc files are unsupported. Save as .docx or PDF.")
        else:
            raise BriefSourceError("Upload a PDF or .docx file.")
    except BriefSourceError:
        raise
    except Exception as exc:
        raise BriefSourceError("Could not read this file. Check that it is a valid, unencrypted PDF or DOCX.") from exc
    text = text.strip()
    if not text:
        raise BriefSourceError("No selectable text was found. Scanned/image-only PDFs need text recognition first.")
    return text[:MAX_CHARS]


def extract_public_google_doc(url: str) -> str:
    """Fetch text from a public, published Google Doc; no visitor account authorization."""
    from urllib.request import Request, urlopen
    match = re.fullmatch(r"https://docs\.google\.com/document/d/([a-zA-Z0-9_-]{20,})/(?:edit|view)?(?:\?.*)?(?:#.*)?", url.strip())
    if not match:
        raise BriefSourceError("Paste a Google Docs document link (docs.google.com/document/d/…).")
    document_id = match.group(1)
    export_url = f"https://docs.google.com/document/d/{document_id}/export?format=txt"
    try:
        request = Request(export_url, headers={"User-Agent": "ContentStudioDemo/1.0"})
        # urllib follows redirects; reject non-Google redirect targets before reading.
        with urlopen(request, timeout=12) as response:
            final = urlparse(response.geturl())
            if final.scheme != "https" or final.hostname not in ("docs.google.com", "doc-0c-00-docs.googleusercontent.com") and not (final.hostname or "").endswith(".googleusercontent.com"):
                raise BriefSourceError("Google Docs redirected to an unexpected destination.")
            if response.status != 200:
                raise BriefSourceError("Google Docs did not return a document.")
            data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise BriefSourceError("Google Doc exceeds the 8 MB limit.")
        text = data.decode("utf-8-sig").strip()
        if not text or text.lstrip().startswith("<!DOCTYPE html") or text.lstrip().startswith("<html"):
            raise BriefSourceError("The Google Doc could not be exported. Enable link access or upload a DOCX/PDF.")
        return text[:MAX_CHARS]
    except BriefSourceError:
        raise
    except Exception as exc:
        raise BriefSourceError("Could not access this Google Doc. It must allow link-based viewing and text export; otherwise upload a DOCX or PDF.") from exc
