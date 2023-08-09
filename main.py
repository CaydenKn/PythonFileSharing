from flask import Flask, request, render_template, jsonify, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
import os
import random
import string

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def generate_random_id():
    """Generate a random ID for the uploaded file."""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(8))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            random_id = generate_random_id()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], random_id + '_' + filename))
            return redirect(url_for('uploaded_file', file_id=random_id, filename=filename))
        else:
            return jsonify({'error': 'No file provided.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin')
def admin_dashboard():
    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        return render_template('admin_dashboard.html', files=files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploaded/<file_id>/<filename>')
def uploaded_file(file_id, filename):
    try:
        return render_template('view.html', file_id=file_id, filename=filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def get_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin/delete/<file_name>')
def delete_file(file_name):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            return redirect(url_for('admin_dashboard'))
        else:
            return jsonify({'error': 'File not found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/edit/<file_name>', methods=['GET', 'POST'])
def edit_file(file_name):
    try:
        if request.method == 'POST':
            new_filename = request.form.get('new_filename')
            if new_filename:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
                new_file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                os.rename(file_path, new_file_path)
                return redirect(url_for('admin_dashboard'))
        return render_template('edit.html', file_name=file_name)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()