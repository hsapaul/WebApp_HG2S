from mido import MidiFile
from pyo import *
from time import sleep

# midi_file = r"C:\Users\franz\Desktop\800000_Drum_Percussion_MIDI_Archive[6_19_15]\Pop\pop 6.mid"
midi_file = r"C:\Users\franz\Desktop\midimidi_6.mid"

# SOUND SELECTION
kick_sample = r"C:\Users\franz\OneDrive - Astrovic\1. Galleries\1.1 Music Gallery\1.1.1 Sample Gallery\#DANCE\Vengeance - Total Dance Sounds Vol.1\VTDS1 Kicks\VTDS1 Electro House Kicks\VTDS1 Electro House Kick 001.wav"
snare_sample = r"C:\Users\franz\OneDrive - Astrovic\1. Galleries\1.1 Music Gallery\1.1.1 Sample Gallery\#DANCE\Vengeance - Total Dance Sounds Vol.1\VTDS1 Snares and Claps\VTDS1 Snares and Claps 008.wav"
hihat_sample = r"C:\Users\franz\OneDrive - Astrovic\1. Galleries\1.1 Music Gallery\1.1.1 Sample Gallery\#DANCE\Vengeance - Total Dance Sounds Vol.1\VTDS1 Cymbals\VTDS1 Closed Hihats\VTDS1 Closed Hihats 004.wav"
crash_sample = r"C:\Users\franz\OneDrive - Astrovic\1. Galleries\1.1 Music Gallery\1.1.1 Sample Gallery\#DANCE\Vengeance - Total Dance Sounds Vol.1\VTDS1 Cymbals\VTDS1 Crash\VTDS1 Crash 01.wav"

time_stamps = {"1_1": None, "1_2": None, "1_3": None, "1_4": None,
               "2_1": None, "2_2": None, "2_3": None, "2_4": None,
               "3_1": None, "3_2": None, "3_3": None, "3_4": None,
               "4_1": None, "4_2": None, "4_3": None, "4_4": None,

               "5_1": None, "5_2": None, "5_3": None, "5_4": None,
               "6_1": None, "6_2": None, "6_3": None, "6_4": None,
               "7_1": None, "7_2": None, "7_3": None, "7_4": None,
               "8_1": None, "8_2": None, "8_3": None, "8_4": None,

               "9_1": None, "9_2": None, "9_3": None, "9_4": None,
               "10_1": None, "10_2": None, "10_3": None, "10_4": None,
               "11_1": None, "11_2": None, "11_3": None, "11_4": None,
               "12_1": None, "12_2": None, "12_3": None, "12_4": None,

               "13_1": None, "13_2": None, "13_3": None, "13_4": None,
               "14_1": None, "14_2": None, "14_3": None, "14_4": None,
               "15_1": None, "15_2": None, "15_3": None, "15_4": None,
               "16_1": None, "16_2": None, "16_3": None, "16_4": None}


# EXTRA FUNCTIONS
def fill_in_timestamps(bpm):
    # BPM --> sixteenth note duration
    beats_per_minute = bpm
    beats_per_second = beats_per_minute / 60
    seconds_per_beat = 1 / beats_per_second
    seconds_per_sixteenth_note = seconds_per_beat / 4
    # Fill in time stamps by iterating over its dictionary
    for i in range(0, 4):
        for j in range(0, 4):
            time_stamps[f"{i + 1}_{j + 1}"] = seconds_per_sixteenth_note * (i * 4 + j)
    print(time_stamps["2_1"])
    return int(time_stamps["1_2"] * 1000)


# MAIN FUNCTIONS
def drum_midi_reader(midi_file):
    mid = MidiFile(midi_file).tracks[1][1:][:-1]

    samples_in_quarters = {"kick": [], "snare": [], "hihat": []}

    sample_point = 0

    for m in mid:
        sample_point += m.time
        # print(m.time, sample_point/96)
        if m.type == 'note_on':
            if m.note == 36:
                samples_in_quarters["kick"].append(sample_point / 96)
            elif m.note == 38:
                samples_in_quarters["snare"].append(sample_point / 96)
            elif m.note == 42:
                samples_in_quarters["hihat"].append(sample_point / 96)

    # Convert Sample Arrays to own Format (1_2) --> 1=quarter, 2=quarter in momentary quarter
    for key, value in samples_in_quarters.items():
        samples_in_quarters[key] = [f"{int(i) + 1}_{int((i - int(i)) * 4) + 1}" for i in value]

    return samples_in_quarters


def drum_midi_player(drum_midi_dict):
    # kick = drum_midi_dict['kick']
    # snare = drum_midi_dict['snare']
    # print('kick', kick)
    # print('snare', snare)
    bpm = 140
    sixteenth_note = fill_in_timestamps(bpm)
    s = Server(sr=48000, nchnls=2, buffersize=256, duplex=0).boot()
    s.start()
    sf = [SfPlayer(kick_sample, speed=1, loop=False, mul=0.4),
          SfPlayer(snare_sample, speed=1, loop=False, mul=0.2),
          SfPlayer(hihat_sample, speed=1, loop=False, mul=0.1)]

    print("Start Playing")
    for i in range(0, 8):
        # Iterate over one bar of time stamps
        for key, value in time_stamps.items():
            # print(time.time() - start_time)
            # Check Drum Pattern if a element should be played
            for key2, value2 in drum_midi_dict.items():
                # print(key2, value2, key, value)
                if key in value2:
                    if key2 == "kick":
                        sf[0].out(0)
                    if key2 == "snare":
                        sf[1].out(0)
                    if key2 == "hihat":
                        sf[2].out(0)
            sleep(sixteenth_note / 1000)


if __name__ == "__main__":
    samples_in_quarters = drum_midi_reader(midi_file)
    drum_midi_player(samples_in_quarters)
