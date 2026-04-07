import re
from typing import List, Dict
import mammoth
import pdfplumber


class Chapter:
    def __init__(self, title: str, text: str):
        self.title = title
        self.text = text.strip()
        self.word_count = len(self.text.split())


def parse_docx(file_path: str) -> List[Dict[str, any]]:
    """Extract text and chapters from a DOCX file."""
    try:
        with open(file_path, "rb") as docx_file:
            result = mammoth.extract_raw_text(docx_file)
            text = result.value

        chapters = detect_chapters(text)

        return [
            {
                "title": ch.title,
                "text": ch.text,
                "word_count": ch.word_count
            }
            for ch in chapters
        ]
    except Exception as e:
        raise Exception(f"Failed to parse DOCX: {str(e)}")


def parse_pdf(file_path: str) -> List[Dict[str, any]]:
    """Extract text and chapters from a PDF file."""
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        chapters = detect_chapters(text)

        return [
            {
                "title": ch.title,
                "text": ch.text,
                "word_count": ch.word_count
            }
            for ch in chapters
        ]
    except Exception as e:
        raise Exception(f"Failed to parse PDF: {str(e)}")


def detect_chapters(text: str) -> List[Chapter]:
    """
    Detect chapters in text using regex patterns.
    Looks for patterns like 'Chapter 1', 'CHAPTER ONE', 'Chapter I', etc.
    If no chapters found, treats entire text as one chapter.
    """
    # Common chapter patterns
    patterns = [
        r"(?:^|\n)\s*(?:Chapter|CHAPTER|Ch\.?)\s+([IVXLCDM]+|\d+|One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|[A-Z][a-z]+)\s*[:\-—]?\s*([^\n]*)\n",
        r"(?:^|\n)\s*([IVXLCDM]+|\d+)\.\s+([^\n]+)\n",
    ]

    chapters = []

    for pattern in patterns:
        matches = list(re.finditer(pattern, text, re.MULTILINE))
        if matches:
            for i, match in enumerate(matches):
                chapter_num = match.group(1)
                chapter_subtitle = match.group(2).strip() if len(match.groups()) > 1 else ""

                title = f"Chapter {chapter_num}"
                if chapter_subtitle:
                    title += f": {chapter_subtitle}"

                start_pos = match.end()
                end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                chapter_text = text[start_pos:end_pos].strip()

                if chapter_text:
                    chapters.append(Chapter(title, chapter_text))

            if chapters:
                break

    # If no chapters detected, treat entire document as one chapter
    if not chapters:
        chapters.append(Chapter("Full Book", text))

    return chapters
