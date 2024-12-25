import os
from werkzeug.utils import secure_filename
from .config import Config

def save_profile_pic(file, username):
    filename = secure_filename(f"{username}_{file.filename}")
    file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(file_path)
    return filename
