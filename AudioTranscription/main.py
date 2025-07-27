import sys
from pydub import AudioSegment
import numpy as np
import webrtcvad
import whisper
import json
import os

import torchaudio
from df.enhance import enhance, init_df

import torch

from dotenv import load_dotenv

# Load variables from .env into environment
load_dotenv()

AUDIO_OUTPUTS = os.getenv("AUDIO_OUTPUTS")
WHISPER_MODEL = os.getenv("WHISPER_MODEL")
TRANSCRIPT_JSON = os.getenv("TRANSCRIPT_JSON")
TRANSCRIPT_OUTPUT_PATH = os.getenv("TRANSCRIPT_OUTPUT_PATH")

def boost_audio(audio_in_path):
    print("boost audio called")
    audio = AudioSegment.from_file(audio_in_path)
    audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    samples = np.array(audio.get_array_of_samples())
    samples = samples.astype(np.float32)
    boost = 3.16
    samples *= boost

    vad = webrtcvad.Vad(0)  # 0-3: aggressiveness
    frame_ms = 10
    frame_len = int(16000 * frame_ms / 1000)
    speech_mask = np.zeros(len(samples), dtype=bool)

    for i in range(0, len(samples)-frame_len, frame_len):
        frame = samples[i:i+frame_len].tobytes()
        if vad.is_speech(frame, 16000):
            speech_mask[i:i+frame_len] = True

    # Boost speech, suppress non-speech
    # boost = 3.16  # ~10dB gain
    # boost = 5
    processed = samples.astype(np.float32)
    # processed[speech_mask] *= boost
    # processed[~speech_mask] *= 0.2  # Lower background
    processed[~speech_mask] *= 0.8



    # vad = webrtcvad.Vad(0)  # 0-3: aggressiveness
    # frame_ms = 10
    # frame_len = int(16000 * frame_ms / 1000)
    # speech_mask = np.zeros(len(samples), dtype=bool)

    # for i in range(0, len(samples)-frame_len, frame_len):
    #     frame = samples[i:i+frame_len].tobytes()
    #     if vad.is_speech(frame, 16000):
    #         speech_mask[i:i+frame_len] = True

    # Save
    output = AudioSegment(
        processed.astype(np.int16).tobytes(),
        frame_rate=16000, sample_width=2, channels=1)
    output.export(AUDIO_OUTPUTS, format="wav")
    # return output

def denoise_audio(audio_in_path):
    print("Denoise called")
    # Initialize DeepFilterNet
    model, df_state, _ = init_df()

    # Load audio using torchaudio
    waveform, sample_rate = torchaudio.load(audio_in_path)

    # Ensure mono audio (DeepFilterNet expects single channel)
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)

    # Resample to DeepFilterNet's expected sample rate if needed
    if sample_rate != df_state.sr():
        resampler = torchaudio.transforms.Resample(sample_rate, df_state.sr())
        waveform = resampler(waveform)

    waveform = waveform.contiguous()
    # If using CUDA, move waveform and model to GPU
    if torch.cuda.is_available():
        model = model.cuda()
        waveform = waveform.cuda()

    # Enhance the audio
    enhanced_audio = enhance(model, df_state, waveform)

    # Save the result
    torchaudio.save(AUDIO_OUTPUTS, enhanced_audio, df_state.sr())




def deep_filter_denoise_chunked(audio_in_path, chunk_duration=30):

    # Initialize DeepFilterNet once
    model, df_state, _ = init_df()
    
    # Load audio
    waveform, sample_rate = torchaudio.load(audio_in_path)
    
    # Ensure mono audio
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    
    # Resample if needed
    if sample_rate != df_state.sr():
        resampler = torchaudio.transforms.Resample(sample_rate, df_state.sr())
        waveform = resampler(waveform)
    
    # Calculate chunk size in samples
    chunk_samples = int(chunk_duration * df_state.sr())
    total_samples = waveform.shape[1]
    
    enhanced_chunks = []
    
    print(f"Processing audio in chunks of {chunk_duration} seconds...")
    print(f"Total duration: {total_samples / df_state.sr():.2f} seconds")
    
    # Process each chunk
    for i in range(0, total_samples, chunk_samples):
        end_idx = min(i + chunk_samples, total_samples)
        chunk = waveform[:, i:end_idx].contiguous()
        
        print(f"Processing chunk {i//chunk_samples + 1}/{(total_samples + chunk_samples - 1)//chunk_samples}")
        
        try:
            # Process chunk
            enhanced_chunk = enhance(model, df_state, chunk)
            enhanced_chunks.append(enhanced_chunk)
            
            # Clear GPU cache after each chunk
            torch.cuda.empty_cache()
            
        except RuntimeError as e:
            if "out of memory" in str(e):
                print(f"Memory error on chunk {i//chunk_samples + 1}, trying CPU processing...")
                # Fallback to CPU for this chunk
                chunk_cpu = chunk.cpu()
                model_cpu = model.cpu() if hasattr(model, 'cpu') else model
                enhanced_chunk = enhance(model_cpu, df_state, chunk_cpu)
                enhanced_chunks.append(enhanced_chunk.cuda() if torch.cuda.is_available() else enhanced_chunk)
                # Move model back to GPU
                if torch.cuda.is_available():
                    model = model.cuda()
            else:
                raise e
    
    # Concatenate all enhanced chunks
    enhanced_audio = torch.cat(enhanced_chunks, dim=1)
    
    # Save result
    output_path = AUDIO_OUTPUTS
    torchaudio.save(output_path, enhanced_audio, df_state.sr())
    

def transcribe(audio_in_path):
    print("Transcribe called")
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(audio_in_path)
    # print("transcribe result", result)
    return result

def format_transcript(transcript):
    final_transcript = []
    for item in transcript:
        final_transcript.append({
            "start": item["start"],
            "end": item["end"],
            "text": item["text"].strip()
            })
    return final_transcript


def export(merged_transcript_diarization, file_path=TRANSCRIPT_JSON):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(merged_transcript_diarization, f, ensure_ascii=False, indent=2)


def run(audio_in_path, meeting_metadata_path, output_file_name):
    try:
        boost_audio(audio_in_path)
        deep_filter_denoise_chunked(audio_in_path)
        transcript = transcribe(AUDIO_OUTPUTS)
        transcript = format_transcript(transcript["segments"])

        meeting_metadata = ""
        with open(meeting_metadata_path, "r") as f:
            meeting_metadata = json.load(f)
        
        transcript = [meeting_metadata] + transcript

        # export(transcript, "final_transcribed.json")
        output_transcript_path = audio_in_path.strip().split
        export(transcript, TRANSCRIPT_OUTPUT_PATH + "/" + output_file_name)
        
    except Exception as e:
        raise e



# if __name__ == "__main__":
#     directory = './'+FILE_DIR_NAME
#     files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

#     run(sys.argv[1], sys.argv[2])
#     # run("meetinAudioWav.wav")