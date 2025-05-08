import os
import tensorflow as tf
from flask import Flask, request, render_template, redirect
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image

# Inisialisasi Flask app
app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MODEL_PATH = 'model_ikan.h5'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load model
model = None
try:
    print(f"Memuat model dari {MODEL_PATH}...")
    model = tf.keras.models.load_model(MODEL_PATH)
    print("✅ Model berhasil dimuat.")
except Exception as e:
    print(f"❌ Gagal memuat model: {e}")

# Cek ekstensi file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Fungsi klasifikasi
def classify_image(image_path):
    print(f"Melakukan klasifikasi gambar: {image_path}")
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize((224, 224))  # Resize gambar sesuai dengan input model
        img_array = np.array(img)
        print(f"Ukuran gambar setelah resize: {img_array.shape}")
        
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        img_array = np.expand_dims(img_array, axis=0)  # Tambahkan batch axis

        prediction = model.predict(img_array)[0][0]
        print(f"Nilai prediksi: {prediction}")

        label = "Segar" if prediction > 0.5 else "Tidak Segar"
        confidence = prediction if prediction > 0.5 else 1 - prediction
        print(f"Label: {label}, Confidence: {confidence}")
        
        return label, float(confidence)
    except Exception as e:
        print(f"❌ Terjadi kesalahan saat klasifikasi gambar: {e}")
        return "Error", 0.0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        print("❌ Tidak ada file yang diupload.")
        return redirect('/')
    file = request.files['file']
    if file.filename == '':
        print("❌ Nama file kosong.")
        return redirect('/')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        print(f"File berhasil diupload: {filepath}")

        if model is not None:
            label, confidence = classify_image(filepath)
            print(f"Prediksi selesai: {label}, Confidence: {confidence}")
            return render_template('result.html', filename=filename, label=label, confidence=confidence)
        else:
            print("❌ Model tidak tersedia.")
            return "Model tidak tersedia"
    else:
        print("❌ File tidak valid atau tidak diizinkan.")
        return redirect('/')

if __name__ == "__main__":
    print("✅ Flask app dimulai.")
    app.run(debug=True, port=5001)
