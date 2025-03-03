import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
import pyaudio
import threading
import time
import queue
from scipy.signal import find_peaks

# 加载音频文件
audio = AudioSegment.from_file("flower_dance.mp4")
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
plt.xlim((0,8000))

chunk_size = sample_rate//10 
num_chunks = len(samples) // chunk_size
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
    # time.sleep(1)
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
    annotations = []
    while True:
        chunk = audio_queue.get()
        if chunk is None:
            break

        spectrum = np.fft.fft(chunk,sample_rate*2)
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
        plt.xlabel('freq(Hz)')
        plt.ylabel('amplitude')

        # 找到多个波峰
        peaks, _ = find_peaks(np.abs(spectrum[:len(spectrum)//2]), height=0.5*np.max(np.abs(spectrum)))

        # 在波峰处显示音阶
        for peak in peaks:
            peak_freq = freq[peak]
            note_name = frequency_to_note_name(peak_freq)
            annotation = ax.annotate(note_name, xy=(peak_freq, ax.get_ylim()[1]), xytext=(peak_freq, ax.get_ylim()[1]),
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