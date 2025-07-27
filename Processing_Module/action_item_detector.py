import re

class ActionItemDetector:
    def __init__(self):
        self.action_patterns = [
            r'(?:will|going to|need to|should|must|have to|responsible for)\s+(.{10,100})(?:\.|$|,)',
            r'(?:action item|todo|task|assignment):\s*(.{5,100})(?:\.|$)',
            r'(?:by|before|due)\s+(?:next\s+)?\w+(?:day)?\s*(.{5,100})(?:\.|$)',
            r'(?:let\'s|we should|we need to)\s+(.{10,100})(?:\.|$)',
            r'(?:I\'ll|you\'ll|he\'ll|she\'ll|they\'ll)\s+(.{10,100})(?:\.|$)',
            r'(?:assigned to|responsible for)\s+(.{5,100})(?:\.|$)'
        ]
        
        self.decision_patterns = [
            r'(?:decided|agreed|concluded|determined)\s+(?:that\s+)?(.{10,100})(?:\.|$)',
            r'(?:decision|conclusion):\s*(.{5,100})(?:\.|$)',
            r'(?:we\'ll|let\'s|going with)\s+(.{10,100})(?:\.|$)',
            r'(?:final decision|final call)\s+(?:is|was)\s+(.{10,100})(?:\.|$)'
        ]
        
        self.deadline_patterns = [
            r'(?:by|before|due|deadline)\s+((?:next\s+)?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|week|month|year|\d+))',
            r'(?:by|before|due)\s+(\d{1,2}[/-]\d{1,2})',
            r'(?:by|before|due)\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}'
        ]
    
    def detect_action_items(self, segments):
        """Detect action items from meeting segments"""
        actions = []
        
        for segment in segments:
            text = segment['text']
            speaker = segment['speaker']
            timestamp = segment['start']
            
            for pattern in self.action_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    action_text = match.group(1).strip()
                    
                    # Extract potential assignee and deadline
                    assignee = self.extract_assignee(action_text, text)
                    deadline = self.extract_deadline(action_text, text)
                    
                    actions.append({
                        'action': action_text,
                        'speaker': speaker,
                        'assignee': assignee,
                        'deadline': deadline,
                        'timestamp': timestamp,
                        'confidence': 0.8
                    })
        
        return self.deduplicate_actions(actions)
    
    def detect_decisions(self, segments):
        """Detect decisions made during the meeting"""
        decisions = []
        
        for segment in segments:
            text = segment['text']
            speaker = segment['speaker']
            timestamp = segment['start']
            
            for pattern in self.decision_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    decision_text = match.group(1).strip()
                    
                    decisions.append({
                        'decision': decision_text,
                        'speaker': speaker,
                        'timestamp': timestamp
                    })
        
        return self.deduplicate_decisions(decisions)
    
    def extract_assignee(self, action_text, full_text):
        """Extract potential assignee from action text"""
        assignee_patterns = [
            r'(?:assigned to|responsibility of|handled by)\s+([A-Za-z\s]+)',
            r'([A-Za-z]+)\s+(?:will|should|needs to)',
            r'(?:for|by)\s+([A-Za-z]+)(?:\s|$|\.)'
        ]
        
        combined_text = action_text + " " + full_text
        
        for pattern in assignee_patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                assignee = match.group(1).strip()
                if 2 < len(assignee) < 30:
                    return assignee
        
        return "TBD"
    
    def extract_deadline(self, action_text, full_text):
        """Extract potential deadline from action text"""
        combined_text = action_text + " " + full_text
        
        for pattern in self.deadline_patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                deadline = match.group(1).strip()
                return deadline
        
        return None
    
    def deduplicate_actions(self, actions):
        """Remove duplicate action items"""
        seen = set()
        unique_actions = []
        
        for action in actions:
            action_key = action['action'].lower()[:50]  # First 50 chars
            if action_key not in seen:
                seen.add(action_key)
                unique_actions.append(action)
        
        return unique_actions
    
    def deduplicate_decisions(self, decisions):
        """Remove duplicate decisions"""
        seen = set()
        unique_decisions = []
        
        for decision in decisions:
            decision_key = decision['decision'].lower()[:50]
            if decision_key not in seen:
                seen.add(decision_key)
                unique_decisions.append(decision)
        
        return unique_decisions

