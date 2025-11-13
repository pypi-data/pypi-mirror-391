import cv2
from PIL import Image
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt

img = cv2.imread('sample.jpg') 

cropped = img[50:250, 100:300]

resized_cv = cv2.resize(cropped, (200, 200))

img_pil = Image.fromarray(cv2.cvtColor(resized_cv, cv2.COLOR_BGR2RGB))
reshaped = img_pil.resize((128, 128))

reshaped.save('output_image.jpg')

y, sr = librosa.load('sample_audio.wav') 

tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
chroma = librosa.feature.chroma_stft(y=y, sr=sr)

print(f"Tempo: {tempo:.2f} BPM")
print(f"Detected Beats: {len(beats)}")
print(f"Avg Spectral Centroid: {np.mean(spectral_centroid):.2f}")

plt.figure(figsize=(10, 4))
librosa.display.waveshow(y, sr=sr)
plt.title('Waveform')
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 4))
librosa.display.specshow(chroma, x_axis='time', y_axis='chroma', cmap='coolwarm')
plt.title('Chroma Pattern')
plt.colorbar()
plt.tight_layout()
plt.show()

cap = cv2.VideoCapture('sample_video.mp4')  

if not cap.isOpened():
    print("Error: video not found or cannot open")
else:
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("Total Frames in Video:", total_frames)

    frame_indices = range(0, total_frames, 50)
    for i in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imshow('Frame', gray)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
