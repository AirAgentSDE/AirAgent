import pyaudio
import wave
import time
import os
import sys
import keyboard
from faster_whisper import WhisperModel
from hlp.planner import UAVPlanner
from e2e.actor import UAVAgent

# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "cache/temp_voice.wav"

class VoiceController:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        # Ensure cache directory exists
        os.makedirs("cache", exist_ok=True)
        
    def record_audio(self):
        """Record audio using PyAudio and save as WAV file"""
        # Start recording
        stream = self.audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK)
        
        print("Starting recording... Press spacebar to stop recording")
        frames = []
        
        # 录制音频数据直到按下空格键
        while True:
            data = stream.read(CHUNK)
            frames.append(data)
            
            # Check if spacebar is pressed
            if keyboard.is_pressed('space'):
                print("Spacebar detected, stopping recording...")
                break
        
        print("Recording ended...")
        
        # Stop recording
        stream.stop_stream()
        stream.close()
        
        # Save audio file
        wave_file = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(self.audio.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b''.join(frames))
        wave_file.close()
        
        return WAVE_OUTPUT_FILENAME
    
    def close(self):
        """Close audio resources"""
        self.audio.terminate()

def transcribe_audio(audio_file):
    """Transcribe audio file"""
    # Initialize model
    # Check if CUDA is available, use CPU if not
    try:
        import torch
        if torch.cuda.is_available():
            model = WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")
        else:
            model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
    except:
        model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
    
    # Transcribe
    segments, info = model.transcribe(audio_file, beam_size=5, language="zh")
    
    # Get transcribed text
    transcribed_text = ""
    for segment in segments:
        transcribed_text += segment.text
    
    return transcribed_text

def read_latest_transcription():
    """Read the latest transcription file"""
    # Get all transcription files from cache folder
    cache_dir = "cache"
    if not os.path.exists(cache_dir):
        return None
        
    files = [f for f in os.listdir(cache_dir) if f.startswith('transcription_') and f.endswith('.txt')]
    if not files:
        return None
    
    # Sort by time and return the latest
    latest_file = os.path.join(cache_dir, max(files, key=lambda f: os.path.getctime(os.path.join(cache_dir, f))))
    with open(latest_file, 'r', encoding='utf-8') as f:
        return f.read().strip()

if __name__ == "__main__":
    # Ensure cache directory exists
    os.makedirs("cache", exist_ok=True)
    
    controller = VoiceController()
    planner = UAVPlanner()
    agent = UAVAgent()
    
    try:
        while True:
            print("Press spacebar to start recording, press Ctrl+C to exit program...")
            keyboard.wait('space')  # Wait for spacebar press
            audio_file = controller.record_audio()
            print("Transcribing...")
            text = transcribe_audio(audio_file)
            print(f"Transcription result: {text}")
            
            # Save transcription result to file
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"cache/transcription_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Transcription result saved to {filename}")
            
            # Use planner to process transcription result
            print("Planning task...")
            plan_result = planner.generate_response(text)
            print(f"\nPlanning result: {plan_result}")
            
            # Extract plan and pass to actor for execution
            try:
                plan = planner.extract_plan(plan_result)
                agent.run("; ".join(plan))
                    
            except Exception as e:
                print(f"Error executing plan: {e}")
            
    except KeyboardInterrupt:
        print("\nProgram exit")
        controller.close()
        sys.exit(0)