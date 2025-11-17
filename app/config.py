import os
from dotenv import load_dotenv
load_dotenv()

WEB_ACCOUNT = os.getenv('WEB_ACCOUNT', "202235020138")
WEB_PASSWORD = os.getenv('WEB_PASSWORD', "Aa786452808!")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "jiujiu99")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "freeclass")
SECRET_MODIFY_KEY = os.getenv("SECRET_MODIFY_KEY", "change-me")
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"