from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "/uploads"  # This path is persistent on Render
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# MongoDB connection
uri = "mongodb+srv://cybok:0500868021Yaw@cluster0.mpkoedf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("✅ Connected to MongoDB!")
except Exception as e:
    print("❌ Connection error:", e)

db = client["image_app"]
images_col = db["images"]

# ✅ Route to homepage (index.html)
@app.route('/')
def index():
    return render_template("index.html")

# Route to serve uploaded image file
@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# Upload form
@app.route('/upload.html', methods=["GET"])
def show_upload():
    return render_template("upload.html")

# Upload action
@app.route('/upload', methods=["POST"])
def upload():
    file = request.files.get("image")
    if not file or file.filename == '':
        return "❌ No file selected", 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    images_col.insert_one({
        "filename": filename,
        "uploaded_at": datetime.utcnow()
    })

    return redirect(url_for("view_images"))

# View uploaded images
@app.route('/images.html', methods=["GET"])
def view_images():
    images = list(images_col.find().sort("uploaded_at", -1))
    return render_template("images.html", images=images)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create folder if it doesn't exist
    app.run(debug=True)
