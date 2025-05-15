from flask import Flask, request, jsonify
import face_recognition
import os
import uuid
import logging
import numpy as np
import json
import mysql.connector
from werkzeug.utils import secure_filename

# Flask app setup
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MySQL connection function
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password",  # ⬅️ غيّرها حسب الإعدادات
        database="face_recognition_system"
    )

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_known_faces_from_db():
    """Load face encodings and usernames from the database."""
    encodings = []
    names = []
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT username, face_encoding FROM users WHERE status = 'active'")
        users = cursor.fetchall()
        for user in users:
            encoding_array = np.array(json.loads(user['face_encoding']))
            encodings.append(encoding_array)
            names.append(user['username'])
            logger.info(f"Loaded encoding for user: {user['username']}")
        cursor.close()
        conn.close()
    except Exception as e:
        logger.exception("Failed to load known faces from DB")
    return encodings, names

# Load known faces at startup
known_face_encodings, known_face_names = load_known_faces_from_db()

@app.route('/')
def index():
    return jsonify({"message": "Identity verification service is running. Send an image via POST to /verify."})

@app.route('/verify', methods=['POST'])
def verify():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided with key "image".'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file type.'}), 400

    try:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(save_path)
        logger.info(f"Uploaded image saved as: {unique_filename}")

        # Load and process the uploaded image
        image = face_recognition.load_image_file(save_path)
        encodings = face_recognition.face_encodings(image)

        # Clean up uploaded file
        os.remove(save_path)

        if not encodings:
            logger.warning("No face detected in uploaded image.")
            return jsonify({'error': 'No face detected in the image.'}), 400

        uploaded_encoding = encodings[0]

        if not known_face_encodings:
            return jsonify({'error': 'No known faces in the database.'}), 500

        distances = face_recognition.face_distance(known_face_encodings, uploaded_encoding)
        best_match_index = np.argmin(distances)
        best_distance = distances[best_match_index]

        threshold = 0.6
        if best_distance < threshold:
            matched_name = known_face_names[best_match_index]
            confidence = round((1.0 - best_distance) * 100, 2)
            logger.info(f"Match found: {matched_name} (Confidence: {confidence}%)")

            # Save matched image path and result to the database
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET last_verified = NOW(), last_image_path = %s WHERE username = %s", 
                               (save_path, matched_name))
                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                logger.error(f"Error while updating verification record in DB: {str(e)}")

            return jsonify({
                'matched': True,
                'name': matched_name,
                'confidence': confidence
            })
        else:
            logger.info("No match found.")
            return jsonify({
                'matched': False,
                'name': "Unknown",
                'confidence': round((1.0 - best_distance) * 100, 2)
            })

    except Exception as e:
        logger.exception("Error while processing the image.")
        return jsonify({'error': 'Internal server error occurred.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
