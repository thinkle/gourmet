"""Internationalization for Gourmet.

This file defines a gettext-like interface with the gourmet domain, and is
later imported in the rest of the application.
"""
import gettext
from pathlib import Path

mo_path = Path(__file__).parent / 'data' / 'locale'

langs = gettext.translation('gourmet', mo_path, fallback=True)
_ = langs.gettext
