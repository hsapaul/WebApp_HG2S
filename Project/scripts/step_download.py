import youtube_dl  # Alternative is pytube
from youtubesearchpython import VideosSearch
import time


def get_yt_url(song, artist, extra):
    search_query = f"{song} {artist} {extra}"
    print("search_query:" + search_query)
    videosSearch = VideosSearch(search_query, limit=2)
    json = videosSearch.result()
    return json["result"][0]["link"]


def yt_download(yt_url, song_folder, extra, index):
    # Notation for everything except the original: Instrumental_
    if index > 0:
        extra = extra + "_"

    video_info = youtube_dl.YoutubeDL().extract_info(
        url=yt_url, download=False
    )

    options = {
        'format': 'bestaudio/best',
        'outtmpl': f"{song_folder}/{extra} %(title)s.%(ext)s (youtube_dl)",
        'keepvideo': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        },
            {'key': 'FFmpegMetadata'},
        ],
    }

    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info['webpage_url']])


def main(song, artist, song_folder):
    print("")
    print("YT DOWNLOAD (w/ youtube_dl)")

    # Download Original, Instrumental and isolated Vocals
    # download_version = ["(Audio)", "(Instrumental)", "(Acapella)"]
    download_version = ["(Audio)"]

    start_time = time.time()
    for index, e in enumerate(download_version):
        yt_url = get_yt_url(song, artist, e)
        yt_download(yt_url, song_folder, e, index)
    print("-- Downloading Audio took %s seconds ---" % (int(time.time() - start_time)))
