from pydub import  AudioSegment

mp4file = "test.mp4"
mp3file = "output.mp3"

audio = AudioSegment.from_file(mp4file, format="mp4")
audio.export(mp3file, format="mp3")

print(f"output{mp3file}")
