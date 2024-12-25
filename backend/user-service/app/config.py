import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') 
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_TOKEN_LOCATION = ['headers']  # Tokens will be in the Authorization headers
    JWT_HEADER_NAME = "Authorization"  # Default is "Authorization"
    JWT_HEADER_TYPE = "Bearer"  # Default is "Bearer"

    # LDAP_SERVER = "ldap://your-ad-server.com"  # AD server URL
    # LDAP_PORT = 389                          # Default LDAP port
    # LDAP_BASE_DN = "DC=yourcompany,DC=com"   # Base DN of your domain
    # LDAP_USER_DN = "CN=Users"
