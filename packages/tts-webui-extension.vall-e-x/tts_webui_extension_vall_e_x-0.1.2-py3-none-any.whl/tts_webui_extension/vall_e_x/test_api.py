#!/usr/bin/env python3
"""
Unit tests for Vall-E-X API functions.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the extension directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from api import preprocess_text, get_lang


class TestVallEXAPI(unittest.TestCase):
    """Test cases for Vall-E-X API functions."""

    @patch('valle_x.utils.generation.langdropdown2token')
    @patch('valle_x.utils.generation.token2lang')
    def test_get_lang_english(self, mock_token2lang, mock_lang2token):
        """Test get_lang function with English."""
        mock_lang2token.__getitem__.return_value = "en"
        mock_token2lang.__getitem__.return_value = "en"

        result = get_lang("English")
        self.assertEqual(result, "en")

    @patch('valle_x.utils.generation.langdropdown2token')
    @patch('valle_x.utils.generation.token2lang')
    def test_get_lang_mix(self, mock_token2lang, mock_lang2token):
        """Test get_lang function with Mix (should return auto)."""
        mock_lang2token.__getitem__.return_value = "mix"
        mock_token2lang.__getitem__.return_value = "mix"

        result = get_lang("Mix")
        self.assertEqual(result, "auto")

    @patch('valle_x.utils.generation.text_tokenizer')
    @patch('valle_x.utils.generation.lang2token')
    @patch('api.get_lang')
    def test_preprocess_text(self, mock_get_lang, mock_lang2token, mock_tokenizer):
        """Test preprocess_text function."""
        # Setup mocks
        mock_get_lang.return_value = "en"
        mock_lang2token.__getitem__.return_value = "[EN]"
        mock_tokenizer.tokenize.return_value = "processed_text"

        result = preprocess_text("Hello world", "English")

        # Assertions
        mock_get_lang.assert_called_once_with("English")
        mock_tokenizer.tokenize.assert_called_once_with(text="_[EN]Hello world[EN]")
        self.assertEqual(result, "processed_text")

    @patch('valle_x.utils.generation.text_tokenizer')
    @patch('valle_x.utils.generation.lang2token')
    @patch('api.get_lang')
    def test_preprocess_text_auto_language(self, mock_get_lang, mock_lang2token, mock_tokenizer):
        """Test preprocess_text function with auto language detection."""
        # Setup mocks
        mock_get_lang.return_value = "auto"
        mock_lang2token.__getitem__.return_value = "[AUTO]"
        mock_tokenizer.tokenize.return_value = "processed_text"

        result = preprocess_text("Hello world", "auto")

        # Assertions
        mock_get_lang.assert_called_once_with("auto")
        mock_tokenizer.tokenize.assert_called_once_with(text="_[AUTO]Hello world[AUTO]")
        self.assertEqual(result, "processed_text")


if __name__ == "__main__":
    unittest.main()
