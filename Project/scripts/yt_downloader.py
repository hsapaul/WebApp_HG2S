from pytube import YouTube


def download_video(url, path):
    yt = YouTube(url)
    # Title of video
    print("Title: ", yt.title)
    # Number of views of video
    print("Number of views: ", yt.views)
    # Length of the video
    print("Length of video: ", yt.length,"seconds")
    # Description of video
    print("Description: ", yt.description)
    # Rating
    print("Ratings: ", yt.rating)
    ys = yt.streams.get_highest_resolution()
    ys.download(path)



