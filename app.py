from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Ensure the 'temp' directory exists
if not os.path.exists('temp'):
    os.makedirs('temp', exist_ok=True)

# Video download function
def download_video(url, video_quality):
    try:
        # Check for cookies.txt
        cookiefile = 'cookies.txt'
        if not os.path.exists(cookiefile):
            raise FileNotFoundError("Cookie file 'cookies.txt' not found.")

        ydl_opts = {
            'format': f'bestvideo[height={video_quality}]+bestaudio/best',
            'outtmpl': f'temp/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'cookiefile': cookiefile,  # Use the path to your cookies file
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp4')  # Adjust for mp4
            return filename
    except Exception as e:
        raise RuntimeError(f"Failed to download video: {str(e)}")

# Audio download function
def download_audio(url):
    try:
        # Check for cookies.txt
        cookiefile = 'cookies.txt'
        if not os.path.exists(cookiefile):
            raise FileNotFoundError("Cookie file 'cookies.txt' not found.")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '256',
            }],
            'outtmpl': f'temp/%(title)s.%(ext)s',
            'cookiefile': cookiefile,  # Use the path to your cookies file
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3')  # Adjust for mp3
            return filename
    except Exception as e:
        raise RuntimeError(f"Failed to download audio: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        url = request.form['url']
        download_type = request.form['type']
        quality = request.form.get('quality', '1080')  # Default to 1080p if not specified

        if download_type not in ['video', 'audio']:
            return jsonify({"error": "Invalid download type."}), 400

        if download_type == 'video':
            filename = download_video(url, quality)
        else:
            filename = download_audio(url)

        if os.path.exists(filename):
            response = send_file(filename, as_attachment=True)
            os.remove(filename)  # Clean up after sending the file
            return response
        else:
            return jsonify({"error": "File not found after download."}), 404

    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)