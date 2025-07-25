import torchaudio
from df.enhance import enhance, init_df
import logging
import os
import time



class Denoiser:
    """
    Denoise speech
    """

    def __init__(
        self,
        verbose: bool = False
    ):
        """
        Args:
          verbose    – True to log detailed progress
        """
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        self.model = None  # Lazy loading - model will be loaded on first use
        
        # Configure logging based on verbosity
        if verbose:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
    
    def _load_model(self) -> None:
        """
        Load the DeepFilterV3 model if not already loaded.
        """
        try:
            
            if self.model is None:
                self.logger.info(f"Loading DeepFilterV3 model")
                model, df_state, _ = init_df()
                self.model = model
                self.df_state = df_state
            
        except Exception as e:
            self.logger.error(f"Failed to load DeepFilterV3 model: {str(e)}")
            raise RuntimeError(f"Failed to load DeepFilterV3 model: {str(e)}")

    def denoise(
        self,
        wav_path: str,
        output_path: str
    ) -> str:
        """
        Run Whisper on the given WAV file.

        Args:
          wav_path     – path to 16 kHz mono WAV

        Returns:
          output_path

        Raises:
          FileNotFoundError if wav_path missing
          RuntimeError on model load or inference error
        """
        # Check if input file exists
        if not os.path.isfile(wav_path):
            raise FileNotFoundError(f"Input WAV file not found: {wav_path}")
        
        # Load model if not already loaded
        self._load_model()
        
        
        # Log start of denoising
        self.logger.info(f"Starting denoising of {wav_path}")
        
        
        start_time = time.time()
        
        try:
            # Run Whisper transcription
            # Load audio using torchaudio
            waveform, sample_rate = torchaudio.load(wav_path)

            # Ensure mono audio (DeepFilterNet expects single channel)
            if waveform.shape[0] > 1:
                waveform = waveform.mean(dim=0, keepdim=True)

            # Resample to DeepFilterNet's expected sample rate if needed
            if sample_rate != self.df_state.sr():
                resampler = torchaudio.transforms.Resample(sample_rate, self.df_state.sr())
                waveform = resampler(waveform)

            # Enhance the audio
            enhanced_audio = enhance(self.model, self.df_state, waveform)
            
            # Log completion
            denoise_time = time.time() - start_time
            self.logger.info(f"Denoising completed in {denoise_time:.2f} seconds")

            # save output audio to outputfile
            # Save the result
            torchaudio.save(output_path, enhanced_audio, self.df_state.sr())

            return output_path
            
            
            
        except Exception as e:
            self.logger.error(f"Denoising failed: {str(e)}")
            print(e)
            raise RuntimeError(f"Denoising failed: {str(e)}")
    