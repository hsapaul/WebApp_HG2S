from pedalboard.pedalboard import Pedalboard, load_plugin
from pedalboard.io import AudioFile

audio_path = r"C:\Users\franz\Desktop\DrumCrawler\data\Songs\Drake - Toosie Slide\audiodata\stems\section_loops\loop_drums_2.wav"
output_audio_path = r"C:\Users\franz\Desktop\DrumCrawler\data\Songs\Drake - Toosie Slide\audiodata\stems\section_loops\loop_drums_2_new.wav"

plugin_path = r"C:\Program Files\Common Files\VST3\Boogex.vst3"
plugin_path_2 = r"C:\Program Files\Common Files\VST3\Endlesss.vst3"
plugin_path_3 = r"C:\Program Files\Common Files\VST3\SpliceBridge.vst3"


def open():
    with AudioFile(audio_path) as f:
        audio = f.read(f.frames)

        plugin = load_plugin(plugin_path)
        # for p in plugin.parameters:
        #     print(p)

        # CHANGE PARAMETERS IN PLUGIN
        plugin.preqlo_db = -2.4
        plugin.preqmid_db = 5.0
        plugin.preqhi_db = 3.7
        plugin.drive_db = 20.0

        plugin.show_editor()
