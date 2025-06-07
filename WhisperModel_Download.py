import whisper

model = whisper.load_model("medium")
result = model.transcribe("your_audio_file.wav")
print(result["text"])
