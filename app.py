from flask import Flask, request, send_file, jsonify
from flask_cors import CORS  # Add this import
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
from rembg import remove
import io
from PIL import Image

app = Flask(__name__)
CORS(app)  # Add this line to enable CORS

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def remove_background(input_path, output_path):
    try:
        with open(input_path, 'rb') as i:
            with open(output_path, 'wb') as o:
                input_data = i.read()
                output_data = remove(input_data)
                o.write(output_data)
        return True
    except Exception as e:
        print(f"Error removing background: {e}")
        return False

@app.route('/remove-background', methods=['POST'])
def process_image():
    # Check if the post request has the file part
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    
    # If user does not select file, browser may submit an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG are allowed.'}), 400
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)
    
    if file_length > MAX_FILE_SIZE:
        return jsonify({'error': f'File too large. Max size is {MAX_FILE_SIZE//(1024*1024)}MB.'}), 400
    
    # Save the uploaded file
    filename = secure_filename(file.filename)
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(upload_path)
    
    # Process the image
    output_filename = f"removed_bg_{filename}"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    
    if not remove_background(upload_path, output_path):
        return jsonify({'error': 'Failed to process image'}), 500
    
    # Return the processed image
    return send_file(
        output_path,
        mimetype='image/png',
        as_attachment=False,
        download_name=output_filename
    )

@app.route('/')
def home():
    return "Background Removal Service is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)