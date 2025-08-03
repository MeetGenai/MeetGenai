"""
sentiment_analyzer.py

Purpose:
    This module introduces a multi-modal analysis capability by assessing the
    emotional sentiment of transcript segments. While designed to be replaced
    by a sophisticated audio-based sentiment model, this implementation
    provides a powerful text-based proxy. It scans dialogue for positive and
    negative keywords to classify the sentiment of each utterance, adding a
    rich layer of emotional context to the analysis.

Key Features:
    - Provides a framework for sentiment analysis.
    - Uses a rule-based keyword approach for text sentiment as a stand-in
      for a true multi-modal (audio) model.
    - Classifies segments as 'Positive', 'Negative', or 'Neutral'.
    - Enriches each segment with sentiment data for downstream use.
"""

from typing import List, Dict, Any, Set

class SentimentAnalyzer:
    """
    Analyzes and attaches sentiment labels to transcript segments.
    """

    # Keyword sets for rule-based sentiment classification.
    # These can be expanded for more nuanced detection.
    _POSITIVE_KEYWORDS: Set[str] = {
        'agree', 'excellent', 'perfect', 'great', 'love', 'success', 'support',
        'resolved', 'achieved', 'fantastic', 'wonderful', 'impressed'
    }
    _NEGATIVE_KEYWORDS: Set[str] = {
        'problem', 'issue', 'concern', 'disagree', 'blocker', 'risk', 'fail',
        'difficult', 'trouble', 'challenge', 'unfortunately', 'error'
    }

    def analyze_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Iterates through segments and attaches a sentiment classification.

        For each segment, it checks for the presence of positive or negative
        keywords. If found, it labels the segment accordingly; otherwise, it
        defaults to 'Neutral'.

        Args:
            segments: A list of transcript segment dictionaries.

        Returns:
            The same list of segments, with each segment dictionary now
            containing a 'sentiment' key.
        """
        if not segments:
            return []

        analyzed_segments = []
        for segment in segments:
            new_segment = segment.copy()
            text_lower = new_segment.get('text', '').lower()
            
            # Simple keyword-based sentiment detection
            has_positive = any(key in text_lower for key in self._POSITIVE_KEYWORDS)
            has_negative = any(key in text_lower for key in self._NEGATIVE_KEYWORDS)

            if has_positive and not has_negative:
                sentiment = 'Positive'
            elif has_negative and not has_positive:
                sentiment = 'Negative'
            else:
                sentiment = 'Neutral'
            
            new_segment['sentiment'] = {
                'label': sentiment,
                'method': 'text_keyword_analysis' # Indicates this is not from an audio model
            }
            analyzed_segments.append(new_segment)
            
        return analyzed_segments
