import cv2
import numpy as np
from flask import Flask, render_template, request
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    uploaded_image_url = None

    if request.method == 'POST':
        if 'image' not in request.files:
            result = "ไม่พบไฟล์ภาพที่แนบมา"
            return render_template('index.html', result=result)

        file = request.files['image']
        if file.filename == '':
            result = "คุณยังไม่ได้เลือกไฟล์"
            return render_template('index.html', result=result)

        if file:
            filename = f"{uuid.uuid4().hex}.jpg"
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            uploaded_image_url = path

            image = cv2.imread(path)
            if image is not None:
                bgr_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                h_half, w_half = 300, 700
                x_center, y_center = bgr_image.shape[0] // 2, bgr_image.shape[1] // 2

                x1 = max(x_center - h_half, 0)
                x2 = min(x_center + h_half, bgr_image.shape[0])
                y1 = max(y_center - w_half, 0)
                y2 = min(y_center + w_half, bgr_image.shape[1])

                roi = bgr_image[x1:x2, y1:y2]

                if roi.size == 0:
                    result = "ไม่สามารถอ่านค่าจากภาพได้ (ROI ว่างหรืออยู่นอกขอบภาพ)"
                else:
                    blue_channel = roi[:, :, 2]
                    blue_intensity = np.mean(blue_channel)

                    if blue_intensity <= 51.00:
                        intensity_info = "ไม่พบวิตามินซี"
                    elif 50.99 <= blue_intensity <= 72.00:
                        intensity_info = "น้อยที่สุด (0.156 - 0.234)"
                    elif 71.99 <= blue_intensity <= 120.00:
                        intensity_info = "น้อยมาก (0.319 - 0.468)"
                    elif 119.99 <= blue_intensity <= 134.00:
                        intensity_info = "ค่อนข้างน้อย (0.624 - 0.936)"
                    elif 133.99 <= blue_intensity <= 140.00:
                        intensity_info = "น้อย (1.250 - 1.875)"
                    elif 139.99 <= blue_intensity <= 147.00:
                        intensity_info = "ปานกลาง (2.50 - 3.75)"
                    elif 146.99 <= blue_intensity <= 160.00:
                        intensity_info = "มาก (5.0 - 7.5)"
                    elif 159.99 <= blue_intensity <= 170.00:
                        intensity_info = "ค่อนข้างมาก (10 - 15)"
                    else:
                        intensity_info = "มากที่สุด (16 - 24)"

                    result = f"ความเข้มข้นของวิตามินซี: {intensity_info} มิลลิกรัมต่อมิลลิลิตร"
            else:
                result = "ไม่สามารถโหลดไฟล์ภาพได้"

    return render_template('index.html', result=result, image_path=uploaded_image_url)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
