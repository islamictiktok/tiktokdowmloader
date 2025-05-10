import os
import requests
import zipfile
import uuid
from flask import Flask, render_template, send_file
from TikTokApi import TikTokApi

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download")
def download_videos():
    folder_id = str(uuid.uuid4())[:8]
    save_path = os.path.join(DOWNLOAD_DIR, folder_id)
    os.makedirs(save_path, exist_ok=True)

    api = TikTokApi()
    videos = api.trending(count=200)

    for i, video in enumerate(videos):
        try:
            url = video.video.download_url
            content = requests.get(url).content
            with open(f"{save_path}/video_{i+1}.mp4", "wb") as f:
                f.write(content)
        except:
            continue

    zip_path = f"{save_path}.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in os.listdir(save_path):
            zipf.write(os.path.join(save_path, file), arcname=file)

    return send_file(zip_path, as_attachment=True)

# التعديل لتشغيل السيرفر على Render
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)
