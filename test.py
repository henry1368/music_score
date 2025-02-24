import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
from pydub.playback import play
import pyaudio

# 加载音频文件
audio = AudioSegment.from_file("output.mp3")
all_samples = np.array(audio.get_array_of_samples())
sample_rate = audio.frame_rate
frame_count = audio.sample_width

# 初始化 PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(frame_count), channels=audio.channels, rate=sample_rate, output=True)

# 实时显示频谱
plt.ion()
fig, ax = plt.subplots()

chunk_size = 1024
# for i in range(0, len(samples), chunk_size):
#     chunk = samples[i:i + chunk_size]
#     stream.write(chunk.tobytes())

#     # 计算频谱
#     spectrum = np.fft.fft(chunk)
#     freq = np.fft.fftfreq(len(spectrum), d=1/sample_rate)
#     ax.clear()
#     ax.plot(freq[:len(freq)//2], np.abs(spectrum[:len(spectrum)//2]))
#     plt.pause(0.01)
for index in range(0, int(audio.frame_count())):
    stream.write(audio.get_frame(index))

    
    samples = all_samples[index*audio.frame_width:(index+1)*audio.frame_width]
    # 计算频谱
    spectrum = np.fft.fft(samples)
    print(audio.frame_width)
    freq = np.fft.fftfreq(len(spectrum), d=1/sample_rate)
    ax.clear()
    ax.plot(freq[:len(freq)//2], np.abs(spectrum[:len(spectrum)//2]))
    plt.pause(0.01)

stream.stop_stream()
stream.close()
p.terminate()

# import pyaudio
# import numpy as np
# import matplotlib.pyplot as plt
# from mutagen.flac import FLAC
# from pydub import AudioSegment
 
# def get_music_time_length(file):
#     """
#     除了重要部分，其他都不算太重要，其他的都是为后面项目的完整功能做的一个准备
#     :return:
#     """
#     music_object = FLAC(file)        # 重要
#     music_length = int(music_object.info.length)
#     minute = music_length // 60
#     second = music_length % 60
#     print(music_object)
#     print("声道数："+str(music_object.info.channels))        # 重要部分
#     print("音频采样频率："+str(music_object.info.sample_rate))        # 重要部分
#     print("音频采样大小:"+str(music_object.info.bits_per_sample))        # 重要部分
#     return str(minute) if minute > 10 else "0" + str(minute) + ":" + str(second)
 
 
# def test(file, format, channels, rate):
#     """
#     重要的函数，音频的播放基本都在这个函数中进行处理
#     """
#     p = pyaudio.PyAudio()
#     song = AudioSegment.from_file(file)
#     print(song.frame_width)
#     """
#     """
#     stream = p.open(format=p.get_format_from_width(song.frame_width),
#                     channels=song.channels,
#                     rate=song.frame_rate,
#                     output=True)
 
#     # 读取音频帧并进行播放
#     for index in range(0, int(song.frame_count())):
#         stream.write(song.get_frame(index))
 
#     # 停止数据流
#     stream.stop_stream()
#     stream.close()
    
#     # 关闭 PyAudio
#     p.terminate()
 
# if __name__ == '__main__':
#     # get_music_time_length("test2.flac")
#     test('test2.flac', 8, 1, 44100)