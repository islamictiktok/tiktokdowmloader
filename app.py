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

    api = TikTokApi()  # لا حاجة لاستخدام get_instance، استخدم TikTokApi مباشرة
    trending = api.trending(count=50)  # نستخدم count هنا للحصول على عدد معين من الفيديوهات

    max_videos = 50  # نحدد العدد الأقصى للفيديوهات
    for i, video in enumerate(trending['items']):  # استخدام 'items' للحصول على الفيديوهات
        if i >= max_videos:
            break
        try:
            url = video['video']['downloadAddr']  # الوصول لرابط تحميل الفيديو
            content = requests.get(url).content
            with open(f"{save_path}/video_{i+1}.mp4", "wb") as f:
                f.write(content)
        except Exception as e:
            print(f"خطأ في الفيديو رقم {i+1}: {e}")
            continue

    zip_path = f"{save_path}.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in os.listdir(save_path):
            zipf.write(os.path.join(save_path, file), arcname=file)

    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)
