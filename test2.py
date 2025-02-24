import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
import pyaudio
import threading
import time
import queue

# 加载音频文件
audio = AudioSegment.from_file("skycity.mp4")
samples = np.array(audio.get_array_of_samples())
sample_rate = audio.frame_rate
frame_width = audio.sample_width

# 初始化 PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(frame_width),
                channels=audio.channels,
                rate=sample_rate,
                output=True)

# 实时显示频谱
plt.ion()
fig, ax = plt.subplots()

chunk_size = 1024
num_chunks = len(samples) // chunk_size
print(num_chunks)

# 创建队列用于音频块传递
audio_queue = queue.Queue()

def frequency_to_note_name(frequency):
    if frequency <= 0:
        return ""
    midi_number = 69 + 12 * np.log2(frequency / 440.0)
    midi_number = int(round(midi_number))

    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_number // 12) - 1
    note = note_names[midi_number % 12]
    return f"{note}{octave}"

def play_audio():
    time.sleep(1)
    for i in range(num_chunks):
        chunk = samples[i * chunk_size:(i + 1) * chunk_size]
        stream.write(chunk.tobytes())
        audio_queue.put(chunk)

    # 处理剩余的样本
    remaining_samples = samples[num_chunks * chunk_size:]
    if len(remaining_samples) > 0:
        stream.write(remaining_samples.tobytes())
        audio_queue.put(remaining_samples)

    stream.stop_stream()
    stream.close()
    p.terminate()
    audio_queue.put(None)  # 发送结束信号

def plot_spectrum():
    pren_note_name = ""
    annotations = []
    while True:
        chunk = audio_queue.get()
        if chunk is None:
            break

        spectrum = np.fft.fft(chunk)
        freq = np.fft.fftfreq(len(spectrum), d=1/sample_rate)
        
        # 清除现有的曲线
        while ax.lines:
            ax.lines.pop()
        
        # 清除现有的注释
        for annotation in annotations:
            annotation.remove()
        annotations.clear()
        
        # 绘制频谱，指定颜色为蓝色
        ax.plot(freq[:len(freq)//2], np.abs(spectrum[:len(spectrum)//2]), color='b')

        peak_freq = freq[np.argmax(np.abs(spectrum))]
        note_name = frequency_to_note_name(peak_freq)
        if note_name != pren_note_name:
            pren_note_name = note_name
            ax.set_title(f"Peak Frequency: {peak_freq:.2f} Hz ({note_name})")

        # 在波峰处显示音阶
        annotation = ax.annotate(note_name, xy=(peak_freq, np.max(np.abs(spectrum))), xytext=(peak_freq, np.max(np.abs(spectrum)) + 10),
                                 arrowprops=dict(facecolor='black', shrink=0.05))
        annotations.append(annotation)

        plt.pause(0.01)

# 创建并启动线程
audio_thread = threading.Thread(target=play_audio)
audio_thread.start()

#绘制频谱
plot_spectrum()

# 等待线程完成
audio_thread.join()