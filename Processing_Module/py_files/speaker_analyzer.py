from collections import defaultdict

class SpeakerAnalyzer:
    def __init__(self):
        pass
    
    def analyze_speakers(self, segments):
        """Analyze speaker patterns and create meaningful mappings"""
        speaker_stats = defaultdict(lambda: {
            'duration': 0, 
            'word_count': 0, 
            'segments': 0,
            'avg_segment_length': 0
        })
        
        # Calculate speaker statistics
        for segment in segments:
            speaker = segment['speaker']
            duration = segment['end'] - segment['start']
            word_count = len(segment['text'].split())
            
            speaker_stats[speaker]['duration'] += duration
            speaker_stats[speaker]['word_count'] += word_count
            speaker_stats[speaker]['segments'] += 1
        
        # Calculate average segment length
        for speaker in speaker_stats:
            if speaker_stats[speaker]['segments'] > 0:
                speaker_stats[speaker]['avg_segment_length'] = (
                    speaker_stats[speaker]['word_count'] / 
                    speaker_stats[speaker]['segments']
                )
        
        # Sort speakers by total speaking time
        sorted_speakers = sorted(
            speaker_stats.items(), 
            key=lambda x: x[1]['duration'], 
            reverse=True
        )
        
        # Create meaningful speaker mappings
        speaker_mapping = {}
        for i, (speaker, stats) in enumerate(sorted_speakers):
            if speaker.upper() != 'UNKNOWN':
                # Determine role based on speaking patterns
                if i == 0 and stats['duration'] > sum(s[1]['duration'] for s in sorted_speakers) * 0.4:
                    speaker_mapping[speaker] = "Primary_Speaker"
                elif stats['avg_segment_length'] > 15:  # Longer segments suggest presenter
                    speaker_mapping[speaker] = f"Presenter_{i+1}"
                else:
                    speaker_mapping[speaker] = f"Participant_{i+1}"
            else:
                speaker_mapping[speaker] = "Unidentified"
        
        return speaker_mapping, dict(speaker_stats)
    
    def apply_speaker_mapping(self, segments, speaker_mapping):
        """Apply speaker mapping to segments"""
        mapped_segments = []
        for segment in segments:
            mapped_segment = segment.copy()
            mapped_segment['speaker'] = speaker_mapping.get(
                segment['speaker'], 
                segment['speaker']
            )
            mapped_segments.append(mapped_segment)
        
        return mapped_segments
