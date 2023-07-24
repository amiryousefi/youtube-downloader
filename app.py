import os

from flask import Flask, request, render_template
from datetime import datetime
from pytube import YouTube, Playlist, Channel
from pytube.exceptions import AgeRestrictedError

app = Flask(__name__)


@app.route('/video', methods=['GET', "POST"])
def video_downloader():

    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':

        video_url = request.form.get('video_url')

        if video_url:

            video = download_video(video_url)

            if video:
                return render_template('index.html', video=video)

            return "DL error", 500

        return "Invalid data", 422


@app.route('/playlist', methods=['GET', "POST"])
def playlist_downloader():
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':

        playlist_url = request.form.get('playlist_url')

        playlist = Playlist(playlist_url)

        playlist_video_urls = playlist.video_urls

        downloaded_videos = []

        videos_with_error = []

        for video_url in playlist_video_urls:

            try:
                video = download_video(video_url)

                downloaded_videos.append(video)
            except Exception as e:
                videos_with_error.append(video_url)
                continue

        return render_template('index.html',
                               downloaded_videos=downloaded_videos,
                               videos_with_error=videos_with_error
                               )


@app.route('/channel', methods=['GET', "POST"])
def channel_downloader():
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':

        channel_url = request.form.get('channel_url')

        channel = Channel(channel_url)

        channel_video_urls = channel.video_urls

        downloaded_videos = []

        videos_with_error = []

        for video_url in channel_video_urls:

            try:
                video = download_video(video_url)

                downloaded_videos.append(video)
            except Exception as e:
                videos_with_error.append(video_url)
                continue

        return render_template('index.html',
                               downloaded_videos=downloaded_videos,
                               videos_with_error=videos_with_error
                               )


def download_video(video_url):
    download_started_at = datetime.now()

    video = YouTube(video_url)
    # video = YouTube(video_url, use_oauth=True, allow_oauth_cache=True)

    file_path = f"static/{video.video_id}.mp4"

    try:

        youtube_streams = video.streams.get_highest_resolution()

        youtube_streams.download(output_path='static/', filename=f"{video.video_id}.mp4")

    except AgeRestrictedError:
        age_restricted = "yes"

    download_ended_at = datetime.now()

    check_exist = os.path.exists(file_path)

    data = {
        'video': video,
        'download_started_at': download_started_at.strftime("%d/%m/%Y %H:%M:%S"),
        'download_ended_at': download_ended_at.strftime("%d/%m/%Y %H:%M:%S"),
        'downloaded_in': (download_ended_at - download_started_at).seconds

    }

    return data if check_exist else False


if __name__ == '__main__':
    app.run()
