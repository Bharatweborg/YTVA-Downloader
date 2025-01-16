from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

# Video download function
def download_video(url, video_quality):
    ydl_opts = {
        'format': f'bestvideo[height={video_quality}]+bestaudio/best',
        'outtmpl': f'temp/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'cookiefile': 'cookies.txt',  # Use the path to your cookies file
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace('.webm', '.mp4')  # Adjust for mp4
        return filename

# Audio download function
def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '256',
        }],
        'outtmpl': f'temp/%(title)s.%(ext)s',
        'cookiefile': 'cookies.txt',  # Use the path to your cookies file
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace('.webm', '.mp3')  # Adjust for mp3
        return filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    download_type = request.form['type']
    quality = request.form.get('quality')

    # Ensure the 'temp' directory exists
    if not os.path.exists('temp'):
        os.makedirs('temp', exist_ok=True)

    if download_type == 'video':
        filename = download_video(url, quality)
    elif download_type == 'audio':
        filename = download_audio(url)
    else:
        return "Invalid download type."

    # Check if the file exists and send it
    if os.path.exists(filename):
        return send_file(filename, as_attachment=True)
    else:
        return "File not found", 404

    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
