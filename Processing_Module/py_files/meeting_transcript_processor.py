import json
from datetime import datetime

class MeetingTranscriptProcessor:
    def __init__(self, text_cleaner, speaker_analyzer, temporal_segmenter, context_preparer):
        """
        Initializes the processor with injected dependencies.
        
        Args:
            text_cleaner: An instance of TextCleaner.
            speaker_analyzer: An instance of SpeakerAnalyzer.
            temporal_segmenter: An instance of TemporalSegmenter.
            context_preparer: An instance of LLMContextPreparer.
        """
        self.text_cleaner = text_cleaner
        self.speaker_analyzer = speaker_analyzer
        self.temporal_segmenter = temporal_segmenter
        self.context_preparer = context_preparer
    
    def process_transcript(self, transcript_data, meeting_date=None):
        """
        Main processing pipeline for meeting transcripts
        
        Args:
            transcript_data: List of transcript segments
            meeting_date: Optional meeting date string
        
        Returns:
            dict: Processed context ready for LLM
        """
        
        print("...Running core processing pipeline...")
        
        # Step 1: Clean transcript text
        cleaned_segments = self.text_cleaner.clean_transcript_segments(transcript_data)
        
        # Step 2: Analyze and enhance speaker information
        speaker_mapping, speaker_stats = self.speaker_analyzer.analyze_speakers(cleaned_segments)
        mapped_segments = self.speaker_analyzer.apply_speaker_mapping(cleaned_segments, speaker_mapping)
        
        # Step 3: Create temporal segments
        time_windows = self.temporal_segmenter.create_time_windows(mapped_segments)
        meeting_duration = self.temporal_segmenter.get_meeting_duration(mapped_segments)
        
        # Step 4: Prepare comprehensive context
        context = self.context_preparer.prepare_comprehensive_context(mapped_segments, speaker_stats)
        
        # Add additional metadata
        context['meeting_info']['date'] = meeting_date or datetime.now().strftime("%Y-%m-%d")
        context['processing_metadata'] = {
            'original_segments': len(transcript_data),
            'processed_segments': len(mapped_segments),
            'time_windows': len(time_windows),
            'processing_timestamp': datetime.now().isoformat()
        }
        
        # Step 5: Generate LLM prompt
        llm_prompt = self.context_preparer.create_llm_prompt(context)
        
        print("...Core processing complete.")
        
        return {
            'context': context,
            'llm_prompt': llm_prompt,
            'processed_segments': mapped_segments,
            'time_windows': time_windows,
            'speaker_mapping': speaker_mapping,
            'metadata': {
                'total_duration_minutes': meeting_duration / 60,
                'processing_stats': context['processing_metadata']
            }
        }
    
    def save_processed_data(self, processed_data, output_file):
        """Save processed data to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # Create a serializable version
                serializable_data = {
                    'context': processed_data['context'],
                    'processed_segments': processed_data['processed_segments'],
                    'speaker_mapping': processed_data['speaker_mapping'],
                    'metadata': processed_data['metadata']
                }
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
            # This print is now more useful as it confirms the save in the loop
            # print(f" Processed data saved to {output_file}")
            return True
        except Exception as e:
            print(f" Error saving processed data to {output_file}: {e}")
            return False

    
    def get_summary_statistics(self, processed_data):
        """Get summary statistics of processed data"""
        context = processed_data['context']
        
        stats = {
            'meeting_duration_minutes': processed_data['metadata']['total_duration_minutes'],
            'total_participants': len(context['meeting_info']['participants']),
            'total_segments': context['meeting_info']['total_segments'],
            'action_items_detected': len(context['identified_actions']),
            'decisions_detected': len(context['identified_decisions']),
            'entities_extracted': {
                'people': len(context['key_entities']['people']),
                'organizations': len(context['key_entities']['organizations']),
                'dates': len(context['key_entities']['dates'])
            },
            'key_moments': len(context['key_moments'])
        }
        
        return stats
