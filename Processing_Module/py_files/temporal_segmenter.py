import pandas as pd

class TemporalSegmenter:
    def __init__(self, window_size=300):  # 5-minute windows
        self.window_size = window_size
    
    def create_time_windows(self, segments):
        """Create time-based context windows"""
        if not segments:
            return []
        
        df = pd.DataFrame(segments)
        max_time = df['end'].max()
        time_windows = []
        
        for start_time in range(0, int(max_time), self.window_size):
            end_time = start_time + self.window_size
            window_segments = df[
                (df['start'] >= start_time) & (df['end'] <= end_time)
            ]
            
            if not window_segments.empty:
                combined_text = ' '.join(window_segments['text'].tolist())
                speakers_in_window = window_segments['speaker'].unique().tolist()
                
                time_windows.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'text': combined_text,
                    'speakers': speakers_in_window,
                    'segment_count': len(window_segments),
                    'duration': end_time - start_time,
                    'segments': window_segments.to_dict('records')
                })
        
        return time_windows
    
    def get_meeting_duration(self, segments):
        """Calculate total meeting duration"""
        if not segments:
            return 0
        
        df = pd.DataFrame(segments)
        return df['end'].max() - df['start'].min()
