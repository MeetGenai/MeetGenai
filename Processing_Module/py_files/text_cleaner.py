
import re
import pandas as pd
from ftfy import fix_text
import json
import sys

class TextCleaner:
    def __init__(self):
        self.fillers = [
            'um', 'uh', 'er', 'ah', 'like', 'you know', 'sort of', 'kind of',
            'I mean', 'actually', 'basically', 'literally', 'obviously',
            'well', 'so', 'right', 'okay', 'ok', 'yeah', 'yes', 'no'
        ]
    
    def clean_text(self, text):
        """Clean and normalize transcript text"""
        if not text or pd.isna(text):
            return ""
        
        # Fix encoding issues
        text = fix_text(text)
        
        # Convert to lowercase for filler removal (but preserve original case)
        text_lower = text.lower()
        
        # Remove filler words more carefully
        for filler in self.fillers:
            # Remove fillers at word boundaries
            pattern = r'\b' + re.escape(filler) + r'\b[,\s]*'
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
        
        # Clean repeated words (e.g., "I I think" -> "I think")
        text = re.sub(r'\b(\w+)(\s+\1\b)+', r'\1', text)
        
        # Standardize punctuation
        text = re.sub(r'[.]{2,}', '...', text)
        text = re.sub(r'[,]{2,}', ',', text)
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        
        # Remove extra whitespace
        text = text.strip()
        
        return text
    
    def clean_transcript_segments(self, segments):
        """Clean all transcript segments"""
        cleaned_segments = []
        for segment in segments:
            cleaned_segment = segment.copy()
            cleaned_segment['text'] = self.clean_text(segment['text'])
            
            # Only keep segments with meaningful content
            if len(cleaned_segment['text'].strip()) > 3:
                cleaned_segments.append(cleaned_segment)
        
        return cleaned_segments


