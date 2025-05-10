import os
import uuid
import shutil
from flask import Flask, send_file, jsonify
from TikTokApi import TikTokApi

app = Flask(__name__)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/download", methods=["GET"])
def download_videos():
    try:
        # إنشاء مجلد مؤقت للتنزيل
        folder_id = str(uuid.uuid4())[:8]
        save_path = os.path.join(DOWNLOAD_DIR, folder_id)
        os.makedirs(save_path, exist_ok=True)

        # تهيئة الـ API
        api = TikTokApi()

        # تحميل فيديوهات الترند
        trending_videos = api.trending()  # بدون أي arguments

        max_videos = 10  # حدد عدد الفيديوهات اللي دايرها
        count = 0

        for video in trending_videos:
            if count >= max_videos:
                break

            video_data = video.bytes()  # تحميل بيانات الفيديو
            video_id = video.id
            filename = os.path.join(save_path, f"{video_id}.mp4")

            with open(filename, "wb") as f:
                f.write(video_data)

            count += 1

        # ضغط المجلد
        zip_path = shutil.make_archive(save_path, 'zip', save_path)

        return send_file(zip_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
