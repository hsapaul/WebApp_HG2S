import matplotlib.pylab as plt
import seaborn as sns
import numpy as np
import librosa
import librosa.display
import IPython.display as ipd
from itertools import cycle
import os
import json
import soundfile as sf
import time

sns.set_theme(style="white", palette=None)
color_pal = plt.rcParams["axes.prop_cycle"].by_key()["color"]
color_cycle = cycle(plt.rcParams["axes.prop_cycle"].by_key()["color"])


def samples_pro_loop_calc(sr, song_bpm):
    beats_per_second = int(song_bpm) / 60
    seconds_for_8_bar = 32 / beats_per_second
    return seconds_for_8_bar * sr


def get_empty_space_at_start(stem_folder):
    # We won't check the vocals, because they also start before downbeat
    file_names = ["bass.wav", "other.wav", "drums.wav"]
    # list of when the certain audio files start
    empty_spaces_at_start = []
    for file in file_names:
        file_path = f"{stem_folder}\{file}"
        x, sr = librosa.load(file_path)
        onset_frames = librosa.onset.onset_detect(x, sr=sr, wait=1, pre_avg=1, post_avg=1, pre_max=1, post_max=1)
        onset_times = librosa.frames_to_time(onset_frames)
        empty_spaces_at_start.append(librosa.frames_to_time(onset_frames)[0])
        empty_spaces_at_start.sort()
        # remove extension, .mp3, .wav etc.
        file_name_no_extension, _ = os.path.splitext(file_path)
        output_name = file_name_no_extension + '.beatmap.txt'
        with open(output_name, 'wt') as f:
            f.write('\n'.join(['%.4f' % onset_time for onset_time in onset_times]))

    # Return first Item of list sorted after time size aka. where the song starts
    return empty_spaces_at_start[0]


def loops_and_images(song_folder):
    stem_folder = os.path.join(song_folder, "audiodata", "stems")

    # Section Loops Folder
    path_metadata = os.path.join(song_folder, "metadata")

    for file in os.listdir(path_metadata):
        with open(f"{path_metadata}\{file}", "r") as f:
            song_bpm = json.load(f)['BPM']

    # Sample Rate von 22050 --> Samples pro Sekunde
    sr = 22050
    # Wie viele Samples sind 8 Bars (32 Schläge) mit der Geschwindigkeit song_bpm?
    samples_for_8_bar = samples_pro_loop_calc(sr, song_bpm)
    # Bei welchem Sample beginnt der Song?
    empty_space_at_start = librosa.time_to_samples(get_empty_space_at_start(stem_folder))
    # Exportiere die ersten drei 8-Bar-Loops sowohl für "Vocals, Drums, Other and Bass" seperat
    for index, filename in enumerate(os.listdir(stem_folder)):
        if filename[-4:] == ".wav" and not filename[:5] == "loop_":
            audio_path = f"{stem_folder}\{filename}"
            y, sr = librosa.load(audio_path)
            # Export der ersten sechs Loops von jedem Stem
            for iterate in range(0, 4):
                # Get Start and End Point of Bar Loop
                loop_start_sample = empty_space_at_start + iterate * samples_for_8_bar
                loop_end_sample = empty_space_at_start + (iterate + 1) * samples_for_8_bar
                # Short Time Fourier Transform for Images and log function over volume
                D = librosa.stft(y[int(loop_start_sample):int(loop_end_sample)])
                S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
                S_db.shape
                # Plot Graph and Save Image
                fig, ax = plt.subplots(figsize=(10, 5))
                img = librosa.display.specshow(S_db, x_axis="time", y_axis='log', ax=ax)
                ax.set_title(f'{filename} Spectogram')
                fig.colorbar(img, ax=ax, format=f'%0.2f')
                base_folder = "\\".join(stem_folder.split("\\")[:-2])
                image_folder = f"{base_folder}\\imagedata"
                plt.savefig(f"{image_folder}\loop_{filename[:-4]}_{iterate}.png")
                # Export Loop
                sf.write(f'{stem_folder}\section_loops\loop_{filename[:-4]}_{iterate}.wav',
                         y[int(loop_start_sample):int(loop_end_sample)], 22050,
                         'PCM_24')




def main(song_folder):
    print("")
    print("LOOPS AND IMAGES")
    start_time = time.time()
    # Create Subfolder in audiodata
    path_sections_loop = os.path.join(song_folder, "audiodata\stems\section_loops")
    if not os.path.isdir(path_sections_loop):
        os.mkdir(path_sections_loop)
    loops_and_images(song_folder)
    print("-- Loops & Spectrograms took %s seconds ---" % (int(time.time() - start_time)))


if __name__ == "__main__":
    main(r"C:\Users\franz\Desktop\DrumCrawler\data\Songs\Drake - Headlines\audiodata\stems")
