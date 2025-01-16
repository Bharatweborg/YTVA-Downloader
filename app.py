from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Ensure the 'temp' directory exists
TEMP_DIR = 'temp'
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR, exist_ok=True)

# Video download function
def download_video(url, video_quality):
    try:
        ydl_opts = {
            'format': f'bestvideo[height={video_quality}]+bestaudio/best',
            'outtmpl': f'{TEMP_DIR}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'cookiesfrombrowser': {
                'browser': 'chrome',  # Replace with 'firefox' or 'edge' if needed
            },
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp4')  # Ensure mp4 extension
            return filename
    except Exception as e:
        raise RuntimeError(f"Failed to download video: {str(e)}")

# Audio download function
def download_audio(url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '256',
            }],
            'outtmpl': f'{TEMP_DIR}/%(title)s.%(ext)s',
            'cookiesfrombrowser': {
                'browser': 'chrome',  # Replace with 'firefox' or 'edge' if needed
            },
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3')  # Ensure mp3 extension
            return filename
    except Exception as e:
        raise RuntimeError(f"Failed to download audio: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        url = request.form.get('url')
        download_type = request.form.get('type')
        quality = request.form.get('quality', '1080')  # Default to 1080p if not specified

        if not url or not download_type:
            return jsonify({"error": "URL and download type are required."}), 400

        if download_type not in ['video', 'audio']:
            return jsonify({"error": "Invalid download type."}), 400

        # Download the requested file
        filename = (
            download_video(url, quality) if download_type == 'video' else download_audio(url)
        )

        if os.path.exists(filename):
            response = send_file(filename, as_attachment=True)
            os.remove(filename)  # Clean up the file after sending
            return response
        else:
            return jsonify({"error": "File not found after download."}), 404

    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
