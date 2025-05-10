from flask import Flask, jsonify, send_file
from TikTokApi import TikTokApi
import uuid
import os
import shutil

app = Flask(__name__)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/download", methods=["GET"])
def download_videos():
    try:
        folder_id = str(uuid.uuid4())[:8]
        save_path = os.path.join(DOWNLOAD_DIR, folder_id)
        os.makedirs(save_path, exist_ok=True)

        api = TikTokApi()

        # بعض نسخ TikTokApi ترجع الترند كم كائن، مش dict
        trending = api.trending()

        # لو trending كائن وليس dict، استعمل `get_generator`
        if hasattr(trending, "__iter__"):
            videos = list(trending)
        elif hasattr(trending, "videos"):
            videos = trending.videos
        else:
            return jsonify({"error": "غير قادر على قراءة بيانات الترند"}), 500

        max_videos = 10

        for i, video in enumerate(videos):
            if i >= max_videos:
                break
            video_data = video.bytes()
            video_id = video.id
            with open(os.path.join(save_path, f"{video_id}.mp4"), "wb") as f:
                f.write(video_data)

        # ضغط الملفات
        zip_path = os.path.join(DOWNLOAD_DIR, f"{folder_id}.zip")
        shutil.make_archive(zip_path.replace(".zip", ""), 'zip', save_path)
        shutil.rmtree(save_path)

        return send_file(zip_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": f"حدث خطأ: {str(e)}"}), 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
