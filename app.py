import os
import uuid
import requests
import zipfile
from TikTokApi import TikTokApi
from flask import Flask, send_file

app = Flask(__name__)

DOWNLOAD_DIR = 'downloads'  # المسار الذي ستخزن فيه الفيديوهات

@app.route("/download", methods=["GET"])
def download_videos():
    # خلق مجلد جديد باسم عشوائي
    folder_id = str(uuid.uuid4())[:8]
    save_path = os.path.join(DOWNLOAD_DIR, folder_id)
    os.makedirs(save_path, exist_ok=True)

    try:
        # الوصول إلى API الخاصة بـ TikTok
        api = TikTokApi()
        trending = api.trending(count=50)  # الحصول على التريندينغ

        max_videos = 50  # نحدد العدد الأقصى للفيديوهات
        for i, video in enumerate(trending):  # التكرار عبر الفيديوهات مباشرة
            if i >= max_videos:
                break

            try:
                # تحميل كل فيديو
                url = video['video']['downloadAddr']
                content = requests.get(url).content

                # حفظ الفيديو في المجلد
                with open(f"{save_path}/video_{i+1}.mp4", "wb") as f:
                    f.write(content)
            except Exception as e:
                print(f"خطأ في الفيديو رقم {i+1}: {e}")
                continue  # استكمال التحميل للفيديوهات التالية لو حصلت مشكلة مع أحدها

        # إنشاء ملف zip للملفات المحفوظة
        zip_path = os.path.join(DOWNLOAD_DIR, f"{folder_id}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in os.listdir(save_path):
                zipf.write(os.path.join(save_path, file), arcname=file)

        # إرجاع الملف المضغوط للمستخدم
        return send_file(zip_path, as_attachment=True)

    except Exception as e:
        return f"حدث خطأ: {e}"

if __name__ == "__main__":
    # قم بتحديد المنفذ باستخدام المتغير PORT في بيئة Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
