from entity_extractor import EntityExtractor
from action_item_detector import ActionItemDetector
from topic_analyzer import TopicAnalyzer

class LLMContextPreparer:
    def __init__(self, entity_extractor, action_detector, topic_analyzer):
        """
        Initializes the context preparer with injected dependencies.
        
        Args:
            entity_extractor: An instance of EntityExtractor.
            action_detector: An instance of ActionItemDetector.
            topic_analyzer: An instance of TopicAnalyzer.
        """
        self.entity_extractor = entity_extractor
        self.action_detector = action_detector
        self.topic_analyzer = topic_analyzer
    
    def prepare_comprehensive_context(self, processed_segments, speaker_stats):
        """Prepare comprehensive context for LLM processing"""
        
        # Extract entities from all text
        all_text = ' '.join([seg['text'] for seg in processed_segments])
        entities = self.entity_extractor.extract_entities(all_text)
        
        # Extract meeting metadata
        meeting_metadata = self.entity_extractor.extract_meeting_metadata(
            processed_segments, entities
        )
        
        # Detect action items and decisions
        actions = self.action_detector.detect_action_items(processed_segments)
        decisions = self.action_detector.detect_decisions(processed_segments)
        
        # Extract topics
        clusters, topic_keywords = self.topic_analyzer.extract_topics_and_themes(
            processed_segments, n_topics=3
        )
        
        # Prepare context structure
        context = {
            'meeting_info': {
                'duration_minutes': meeting_metadata['duration_minutes'],
                'total_segments': len(processed_segments),
                'participants': list(speaker_stats.keys()),
                'participant_stats': speaker_stats
            },
            'key_entities': entities,
            'conversation_summary': self.create_conversation_summary(processed_segments),
            'identified_actions': actions,
            'identified_decisions': decisions,
            'topics_discussed': topic_keywords,
            'key_moments': self.extract_key_moments(processed_segments)
        }
        
        return context
    
    def create_conversation_summary(self, segments):
        """Create structured conversation summary"""
        summary_segments = []
        
        # Group segments by speaker for better flow
        current_speaker = None
        current_text = ""
        current_start = 0
        
        for segment in segments:
            if segment['speaker'] != current_speaker:
                if current_text and current_speaker:
                    summary_segments.append({
                        'speaker': current_speaker,
                        'start_time': current_start,
                        'content': current_text.strip(),
                        'key_points': self.extract_key_sentences(current_text)
                    })
                
                current_speaker = segment['speaker']
                current_text = segment['text']
                current_start = segment['start']
            else:
                current_text += " " + segment['text']
        
        # Add the last segment
        if current_text and current_speaker:
            summary_segments.append({
                'speaker': current_speaker,
                'start_time': current_start,
                'content': current_text.strip(),
                'key_points': self.extract_key_sentences(current_text)
            })
        
        return summary_segments
    
    def extract_key_sentences(self, text, max_sentences=2):
        """Extract key sentences from text"""
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
        
        if len(sentences) <= max_sentences:
            return sentences
        
        # Score sentences
        keywords = [
            'important', 'key', 'main', 'primary', 'crucial', 'significant',
            'decision', 'action', 'next', 'follow', 'complete', 'finish',
            'deadline', 'due', 'responsible', 'assign'
        ]
        
        scored_sentences = []
        for sentence in sentences:
            score = len(sentence.split())  # Base score on length
            
            # Boost score for important keywords
            for keyword in keywords:
                if keyword in sentence.lower():
                    score *= 1.3
            
            # Boost score for questions and directives
            if '?' in sentence or any(word in sentence.lower() for word in ['should', 'will', 'need']):
                score *= 1.2
            
            scored_sentences.append((sentence, score))
        
        # Return top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        return [sent[0] for sent in scored_sentences[:max_sentences]]
    
    def extract_key_moments(self, segments):
        """Extract key moments from the meeting"""
        key_moments = []
        
        # Look for moments with high engagement (speaker changes, questions, decisions)
        for i, segment in enumerate(segments):
            text = segment['text'].lower()
            
            # Decision moments
            if any(word in text for word in ['decide', 'agree', 'conclude', 'final']):
                key_moments.append({
                    'type': 'decision',
                    'timestamp': segment['start'],
                    'speaker': segment['speaker'],
                    'content': segment['text']
                })
            
            # Question moments
            elif '?' in segment['text']:
                key_moments.append({
                    'type': 'question',
                    'timestamp': segment['start'],
                    'speaker': segment['speaker'],
                    'content': segment['text']
                })
            
            # Action moments
            elif any(word in text for word in ['action', 'task', 'assign', 'responsible']):
                key_moments.append({
                    'type': 'action',
                    'timestamp': segment['start'],
                    'speaker': segment['speaker'],
                    'content': segment['text']
                })
        
        return key_moments[:10]  # Limit to top 10 key moments
    
    def create_llm_prompt(self, context_data):
        """Create optimized prompt for LLM summarization"""
        
        # Format conversation highlights
        conversation_highlights = []
        for segment in context_data['conversation_summary'][:8]:  # Limit for prompt length
            conversation_highlights.append(
                f"[{segment['start_time']:.1f}s] {segment['speaker']}: {segment['content'][:150]}..."
            )
        
        # Format identified actions
        action_list = []
        for action in context_data['identified_actions'][:10]:
            deadline_info = f" (Due: {action['deadline']})" if action['deadline'] else ""
            assignee_info = f" - Assignee: {action['assignee']}" if action['assignee'] != "TBD" else ""
            action_list.append(f"• {action['action']}{deadline_info}{assignee_info}")
        
        # Format decisions
        decision_list = []
        for decision in context_data['identified_decisions'][:5]:
            decision_list.append(f"• {decision['decision']} (by {decision['speaker']})")
        
        prompt = f"""
Please analyze this meeting transcript and provide a comprehensive summary in the following JSON format:

MEETING OVERVIEW:
- Duration: {context_data['meeting_info']['duration_minutes']} minutes
- Participants: {', '.join(context_data['meeting_info']['participants'])}
- Total Segments: {context_data['meeting_info']['total_segments']}

KEY ENTITIES MENTIONED:
- People: {', '.join(context_data['key_entities']['people'][:5]) if context_data['key_entities']['people'] else 'None'}
- Organizations: {', '.join(context_data['key_entities']['organizations'][:3]) if context_data['key_entities']['organizations'] else 'None'}
- Important Dates: {', '.join(context_data['key_entities']['dates'][:3]) if context_data['key_entities']['dates'] else 'None'}

CONVERSATION HIGHLIGHTS:
{chr(10).join(conversation_highlights)}

PRE-IDENTIFIED ACTION ITEMS:
{chr(10).join(action_list) if action_list else 'None detected automatically'}

PRE-IDENTIFIED DECISIONS:
{chr(10).join(decision_list) if decision_list else 'None detected automatically'}

TOPICS DISCUSSED:
{self.format_topics(context_data['topics_discussed'])}

Please provide output in this exact JSON structure:
{{
 "action_items": [
  {{
   "action": "specific action description",
   "assignee": "person responsible",
   "deadline": "deadline if mentioned or null",
   "priority": "high/medium/low",
   "status": "pending"
  }}
 ],
 "keynotes": [
  "key point 1 - most important topic discussed",
  "key point 2 - major decision or outcome", 
  "key point 3 - significant issue or concern"
 ],
 "full_summary": "A comprehensive 3-4 paragraph summary covering the main topics, discussions, decisions made, and outcomes of the meeting. Include context about who said what and why it matters.",
 "tldr": "A concise 2-3 sentence executive summary highlighting the most critical outcomes and next steps from this meeting for quick reference.",
 "decisions_made": [
  "specific decision 1 with context",
  "specific decision 2 with rationale"
 ],
 "next_steps": [
  "immediate next step 1",
  "follow-up action 2",
  "long-term objective 3"
 ],
 "meeting_metadata": {{
  "duration_minutes": {context_data['meeting_info']['duration_minutes']},
  "participant_count": {len(context_data['meeting_info']['participants'])},
  "key_topics": ["topic1", "topic2", "topic3"],
  "meeting_type": "planning/review/update/decision/other"
 }}
}}

Focus on accuracy and completeness. If information is not available or unclear, indicate this rather than making assumptions.
"""
        
        return prompt
    
    def format_topics(self, topics_dict):
        """Format topics for prompt"""
        if not topics_dict:
            return "No specific topics automatically identified"
        
        topic_strings = []
        for topic_id, keywords in topics_dict.items():
            if keywords:
                topic_strings.append(f"Topic {topic_id + 1}: {', '.join(keywords[:5])}")
        
        return '\n'.join(topic_strings) if topic_strings else "No specific topics identified"
