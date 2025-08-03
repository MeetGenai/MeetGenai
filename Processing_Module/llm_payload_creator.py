"""
llm_payload_creator.py

Purpose:
    This module acts as the final assembly stage before interacting with a
    Large Language Model (LLM). It now gathers an even richer set of structured
    data—including sentiment analysis—and masterfully formats it into a highly
    detailed context object. It then uses this multi-modal context to engineer
    an advanced, precise prompt designed to guide an LLM to generate a superior,
    nuanced, and structured JSON summary of the meeting.

Key Features:
    - Aggregates data from multiple analytical sources, including sentiment.
    - Constructs a rich, multi-layered context dictionary.
    - Implements advanced prompt engineering to leverage multi-modal insights.
    - Generates a final, clean prompt string ready for an LLM API call.
"""

from typing import List, Dict, Any

# Import analytical components for type hinting
from ner_extractor import NamedEntityExtractor
from outcome_detector import OutcomeDetector
from thematic_analyzer import ThematicAnalyzer

class LLMPayloadCreator:
    """
    Builds a comprehensive, multi-modal context object and a structured prompt for an LLM.
    """

    def __init__(self,
                 entity_extractor: NamedEntityExtractor,
                 outcome_detector: OutcomeDetector,
                 thematic_analyzer: ThematicAnalyzer):
        """
        Initializes the payload creator with its analytical dependencies.

        Args:
            entity_extractor: An instance of the NamedEntityExtractor.
            outcome_detector: An instance of the OutcomeDetector.
            thematic_analyzer: An instance of the ThematicAnalyzer.
        """
        self.entity_extractor = entity_extractor
        self.outcome_detector = outcome_detector
        self.thematic_analyzer = thematic_analyzer

    def build_context_and_prompt(self,
                                 segments: List[Dict[str, Any]],
                                 participant_stats: Dict[str, Any],
                                 participant_roles: Dict[str, str]
                                 ) -> Dict[str, Any]:
        """
        Creates the full analytical context and generates the final, advanced LLM prompt.

        Args:
            segments: The list of processed, sentiment-enriched transcript segments.
            participant_stats: A dictionary with statistics for each speaker.
            participant_roles: A dictionary mapping speaker IDs to roles.

        Returns:
            A dictionary containing the final 'context' object and the 'llm_prompt'.
        """
        full_text = " ".join(seg.get('text', '') for seg in segments)

        # 1. Run all analyses on the full text of the window
        entities = self.entity_extractor.extract_from_corpus(full_text)
        outcomes = self.outcome_detector.detect_outcomes(segments)
        themes = self.thematic_analyzer.discover_themes(segments, num_themes=4)

        # 2. Assemble the comprehensive context object (without the redundant transcript string)
        context = {
            'meeting_metadata': {
                'duration_seconds': segments[-1]['end'] - segments[0]['start'] if segments else 0,
                'participants': list(participant_roles.values()),
                'participant_contributions': participant_stats
            },
            'extracted_intelligence': {
                'entities': entities,
                'outcomes': outcomes,
                'discussion_themes': themes,
                'sentiment_flow': self._summarize_sentiment(segments)
            }
        }

        # 3. Generate the final LLM prompt, creating the formatted transcript string on the fly
        llm_prompt = self._generate_llm_prompt(context, segments)

        return {
            'final_context': context,
            'llm_prompt': llm_prompt
        }

    def _summarize_sentiment(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Creates a high-level summary of the conversation's emotional tone."""
        sentiment_summary = []
        for segment in segments:
            sentiment_label = segment.get('sentiment', {}).get('label')
            if sentiment_label in ['Positive', 'Negative']:
                sentiment_summary.append({
                    'speaker': segment.get('speaker'),
                    'sentiment': sentiment_label,
                    'text_snippet': segment.get('text', '')[:100] + '...'
                })
        return sentiment_summary

    def _generate_llm_prompt(self, context: Dict[str, Any], segments: List[Dict[str, Any]]) -> str:
        """
        Constructs a detailed, structured prompt for the LLM, now including a key topics summary.
        """
        def format_list(items: List[Any]) -> str:
            return ", ".join(map(str, items)) if items else "None"

        def format_outcomes(items: List[Dict], limit: int = 7) -> str:
            if not items: return "  - None automatically detected."
            lines = [f"  - {item['description']}" for item in items[:limit]]
            return "\n".join(lines)

        def format_themes_for_prompt(themes: Dict) -> str:
            if not themes: return "No distinct themes identified."
            # Create a concise, readable list of theme keywords
            all_keywords = [kw for keywords_list in themes.values() for kw in keywords_list]
            return ", ".join(sorted(list(set(all_keywords))[:10])) # Limit for brevity

        # Create the formatted transcript string specifically for the prompt
        formatted_transcript_chunk = "\n".join(
            f"[{s['speaker']} at {s['start']:.1f}s | Sentiment: {s.get('sentiment', {}).get('label', 'N/A')}]: {s['text']}" for s in segments
        )

        prompt = f"""
# MISSION
Your task is to act as an expert meeting analyst with high emotional intelligence. Analyze the provided meeting transcript chunk and its multi-modal metadata to produce a concise, structured, and deeply insightful summary in JSON format.

# INPUT DATA
## Meeting Metadata
- Participants: {format_list(context['meeting_metadata']['participants'])}
- Key Topics Discussed: {format_themes_for_prompt(context['extracted_intelligence']['discussion_themes'])}
- Overall Sentiment: The transcript includes sentiment labels ('Positive', 'Negative', 'Neutral') for each utterance. Pay close attention to shifts in tone.

## Extracted Intelligence
- Detected Action Items (Tasks):
{format_outcomes(context['extracted_intelligence']['outcomes']['tasks'])}
- Detected Key Decisions:
{format_outcomes(context['extracted_intelligence']['outcomes']['decisions'])}

## Full Transcript Chunk with Sentiment
```
{formatted_transcript_chunk}
```

# INSTRUCTIONS
Based *only* on the information provided above, generate a JSON object with the following exact structure. Do not add comments or any text outside the JSON block. Your summary should reflect the emotional context and key topics of the conversation.

```json
{{
  "executive_summary": "A 2-3 sentence high-level overview of this part of the meeting, covering its main purpose, key topics, and the overall emotional tone.",
  "detailed_summary": "A 3-4 paragraph narrative summarizing the discussion. Detail the main points, arguments, and conclusions, weaving in observations about the sentiment and topics. For instance, 'The discussion around [Topic X] became Negative, but a Positive resolution was reached when...'",
  "action_items": [
    {{
      "task": "A clear, concise description of the action to be performed.",
      "assignee": "The person or team responsible, or 'Unassigned'.",
      "deadline": "The specified deadline, or 'Not Specified'."
    }}
  ],
  "key_decisions": [
    {{
      "decision": "A concise statement of the final decision made.",
      "context": "A brief explanation of the discussion leading to the decision, including the sentiment and topic being discussed at that time."
    }}
  ]
}}
```
"""
        return prompt.strip()
