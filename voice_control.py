import pyaudio
import wave
import time
import os
import sys
import keyboard
from faster_whisper import WhisperModel
from hlp.planner import UAVPlanner
from e2e.actor import UAVAgent

# 音频录制参数
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "cache/wav/temp_voice.wav"

# 确保缓存目录存在
os.makedirs("cache/wav", exist_ok=True)
os.makedirs("cache/txt", exist_ok=True)

class VoiceController:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        
    def record_audio(self):
        """使用PyAudio录制音频并保存为WAV文件"""
        # 开始录制
        stream = self.audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK)
        
        print("开始录制...按下空格键停止录制")
        frames = []
        
        # 录制音频数据直到按下空格键
        while True:
            data = stream.read(CHUNK)
            frames.append(data)
            
            # 检查是否按下空格键
            if keyboard.is_pressed('space'):
                print("检测到空格按键，正在停止录制...")
                break
        
        print("录制结束...")
        
        # 停止录制
        stream.stop_stream()
        stream.close()
        
        # 保存音频文件
        wave_file = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(self.audio.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b''.join(frames))
        wave_file.close()
        
        return WAVE_OUTPUT_FILENAME
    
    def close(self):
        """关闭音频资源"""
        self.audio.terminate()

def transcribe_audio(audio_file):
    """转写音频文件"""
    # 初始化模型
    # 检查CUDA是否可用，否则使用CPU
    try:
        import torch
        if torch.cuda.is_available():
            model = WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")
        else:
            model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
    except:
        model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
    
    # 转写
    segments, info = model.transcribe(audio_file, beam_size=5, language="zh")
    
    # 获取转写文本
    transcribed_text = ""
    for segment in segments:
        transcribed_text += segment.text
    
    return transcribed_text

def read_latest_transcription():
    """读取最新的转写文件"""
    # 从缓存文件夹获取所有转写文件
    cache_dir = "cache/txt"
    if not os.path.exists(cache_dir):
        return None
        
    files = [f for f in os.listdir(cache_dir) if f.startswith('transcription_') and f.endswith('.txt')]
    if not files:
        return None
    
    # 按时间排序并返回最新的
    latest_file = os.path.join(cache_dir, max(files, key=lambda f: os.path.getctime(os.path.join(cache_dir, f))))
    with open(latest_file, 'r', encoding='utf-8') as f:
        return f.read().strip()

if __name__ == "__main__":    
    controller = VoiceController()
    planner = UAVPlanner()
    agent = UAVAgent()
    
    try:
        while True:
            print("按下空格键开始录音，按下Ctrl+C退出程序...")
            keyboard.wait('space')  # 等待按下空格键
            audio_file = controller.record_audio()
            print("正在进行语音转写...")
            task = transcribe_audio(audio_file)
            print(f"转写结果: {task}")
            
            # 保存转写结果到文件
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"cache/txt/transcription_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(task)
            print(f"转写结果已保存到 {filename}")
            
            # 使用规划器处理转写结果
            print("正在生成任务计划...")
            plan = planner.query_llm(task)
            print(f"\n计划结果: {plan}")
            agent.run(plan)
            agent.next()
                    
            
    except KeyboardInterrupt:
        print("\n程序退出")
        controller.close()
        sys.exit(0)