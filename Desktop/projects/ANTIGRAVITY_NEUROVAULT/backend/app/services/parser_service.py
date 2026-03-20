import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)

CHUNK_SIZE = 512
CHUNK_OVERLAP = 64


class ParserService:
    """Extracts text from PDF, DOCX, TXT and image files."""

    def extract_text(self, file_bytes: bytes, file_type: str) -> str:
        """Dispatch to the correct extractor based on MIME / extension."""
        ft = file_type.lower()
        try:
            if ft in ("application/pdf", "pdf"):
                return self._extract_pdf(file_bytes)
            elif ft in (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "docx",
            ):
                return self._extract_docx(file_bytes)
            elif ft in ("text/plain", "txt", "md", "csv"):
                return file_bytes.decode("utf-8", errors="replace")
            elif ft.startswith("image/") or ft in ("png", "jpg", "jpeg", "tiff", "bmp"):
                return self._extract_image(file_bytes)
            else:
                # Attempt UTF-8 decode as fallback
                return file_bytes.decode("utf-8", errors="replace")
        except Exception as e:
            logger.warning(f"Text extraction failed ({ft}): {e}")
            return ""

    def _extract_pdf(self, data: bytes) -> str:
        import PyPDF2

        reader = PyPDF2.PdfReader(io.BytesIO(data))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
        return "\n\n".join(pages)

    def _extract_docx(self, data: bytes) -> str:
        import docx

        doc = docx.Document(io.BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)

    def _extract_image(self, data: bytes) -> str:
        try:
            import pytesseract
            from PIL import Image

            img = Image.open(io.BytesIO(data))
            return pytesseract.image_to_string(img)
        except Exception as e:
            logger.warning(f"OCR failed: {e}")
            return ""

    def chunk_text(
        self,
        text: str,
        chunk_size: int = CHUNK_SIZE,
        overlap: int = CHUNK_OVERLAP,
    ) -> list[str]:
        """Split text into overlapping chunks by word count."""
        if not text or not text.strip():
            return []
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk = " ".join(words[start:end])
            if chunk.strip():
                chunks.append(chunk)
            if end >= len(words):
                break
            start += chunk_size - overlap
        return chunks

    def get_preview(self, text: str, max_chars: int = 300) -> str:
        """Return a short preview of the document text."""
        cleaned = " ".join(text.split())
        return cleaned[:max_chars] + ("…" if len(cleaned) > max_chars else "")


parser_service = ParserService()
