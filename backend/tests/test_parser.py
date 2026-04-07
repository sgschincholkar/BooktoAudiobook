import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from parser import detect_chapters


def test_detects_numeric_chapters():
    text = """
Chapter 1: The Beginning
Once upon a time there was a book.

Chapter 2: The Middle
Things got interesting here.

Chapter 3: The End
And they all lived happily ever after.
"""
    chapters = detect_chapters(text)
    assert len(chapters) == 3
    assert "1" in chapters[0].title
    assert "2" in chapters[1].title
    assert "3" in chapters[2].title


def test_detects_uppercase_chapters():
    text = """
CHAPTER 1
First chapter content here.

CHAPTER 2
Second chapter content here.
"""
    chapters = detect_chapters(text)
    assert len(chapters) == 2


def test_fallback_to_full_book_when_no_chapters():
    text = "This is just a block of text with no chapter markers at all."
    chapters = detect_chapters(text)
    assert len(chapters) == 1
    assert chapters[0].title == "Full Book"
    assert "block of text" in chapters[0].text


def test_chapter_text_is_not_empty():
    text = """
Chapter 1: Setup
This chapter has content.

Chapter 2: Payoff
This chapter also has content.
"""
    chapters = detect_chapters(text)
    for chapter in chapters:
        assert chapter.word_count > 0
        assert chapter.text.strip() != ""


def test_word_count_is_accurate():
    text = """
Chapter 1
one two three four five
"""
    chapters = detect_chapters(text)
    assert chapters[0].word_count == 5


def test_roman_numeral_chapters():
    text = """
Chapter I: Introduction
Content of the first chapter.

Chapter II: Development
Content of the second chapter.
"""
    chapters = detect_chapters(text)
    assert len(chapters) == 2


def test_empty_text_fallback():
    chapters = detect_chapters("")
    assert len(chapters) == 1
    assert chapters[0].title == "Full Book"
