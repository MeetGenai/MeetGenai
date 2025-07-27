import spacy
import re

class EntityExtractor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("spaCy English model not found. Please install it with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract_entities(self, text):
        """Extract named entities from text"""
        if not self.nlp:
            return {
                'people': [], 'organizations': [], 'dates': [], 'locations': [],
                'money': [], 'products': [], 'events': [], 'times': []
            }
            
        doc = self.nlp(text)
        
        entities = {
            'people': [],
            'organizations': [],
            'dates': [],
            'locations': [],
            'money': [],
            'products': [],
            'events': [],
            'times': []
        }
        
        for ent in doc.ents:
            entity_text = ent.text.strip()
            if len(entity_text) > 1:
                if ent.label_ in ['PERSON']:
                    entities['people'].append(entity_text)
                elif ent.label_ in ['ORG']:
                    entities['organizations'].append(entity_text)
                elif ent.label_ in ['DATE']:
                    entities['dates'].append(entity_text)
                elif ent.label_ in ['GPE', 'LOC']:
                    entities['locations'].append(entity_text)
                elif ent.label_ in ['MONEY']:
                    entities['money'].append(entity_text)
                elif ent.label_ in ['PRODUCT']:
                    entities['products'].append(entity_text)
                elif ent.label_ in ['EVENT']:
                    entities['events'].append(entity_text)
                elif ent.label_ in ['TIME']:
                    entities['times'].append(entity_text)
        
        # Remove duplicates and clean
        for key in entities:
            entities[key] = list(set(entities[key]))
            # Remove very short or common words
            entities[key] = [
                item for item in entities[key] 
                if len(item) > 2 and item.lower() not in ['the', 'and', 'or', 'but']
            ]
        
        return entities
    
    def extract_meeting_metadata(self, segments, entities):
        """Extract meeting-specific metadata"""
        all_text = ' '.join([seg['text'] for seg in segments])
        
        # Extract potential meeting topics
        topics = []
        topic_patterns = [
            r'(?:discuss|talking about|focus on|regarding)\s+(.+?)(?:\.|,|$)',
            r'(?:topic|subject|issue)\s+(?:is|was|of)\s+(.+?)(?:\.|,|$)',
            r'(?:meeting about|call about)\s+(.+?)(?:\.|,|$)'
        ]
        
        for pattern in topic_patterns:
            matches = re.finditer(pattern, all_text, re.IGNORECASE)
            for match in matches:
                topic = match.group(1).strip()
                if 5 < len(topic) < 50:
                    topics.append(topic)
        
        # Extract meeting duration
        duration = 0
        if segments:
            import pandas as pd
            df = pd.DataFrame(segments)
            duration = (df['end'].max() - df['start'].min()) / 60  # Convert to minutes
        
        return {
            'topics': list(set(topics)),
            'duration_minutes': round(duration, 1),
            'entities': entities
        }
