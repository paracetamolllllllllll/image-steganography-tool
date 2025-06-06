from flask import Flask, render_template, request, send_file, flash
from steg_utils import encode_message, decode_message, encrypt_message, decrypt_message
from werkzeug.utils import secure_filename
import os
import io

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this to a stronger key for production
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode', methods=['POST'])
def encode():
    file = request.files['image']
    message = request.form['message']
    password = request.form['password']

    if not file or not message or not password:
        flash("Please provide all inputs.")
        return render_template('index.html')

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    try:
        encrypted_message = encrypt_message(message, password)
        encoded_img = encode_message(input_path, encrypted_message)

        output_io = io.BytesIO()
        encoded_img.save(output_io, format='PNG')
        output_io.seek(0)
        return send_file(output_io, mimetype='image/png', as_attachment=True, download_name='encoded_image.png')
    except Exception as e:
        flash(f"❌ Failed to encode: {str(e)}")
        return render_template('index.html')

@app.route('/decode', methods=['POST'])
def decode():
    file = request.files['image']
    password = request.form['password']

    if not file or not password:
        flash("Please provide both image and password.")
        return render_template('index.html')

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    try:
        hidden_message = decode_message(input_path)
        decrypted = decrypt_message(hidden_message, password)
        flash(f"✅ Decoded Message: {decrypted}")
    except Exception as e:
        flash(f"❌ Failed to decode or decrypt message:\n{str(e)}")

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
