import os
from dotenv import load_dotenv

load_dotenv()

botToken = os.getenv('BOT_TOKEN')
admin_id = os.getenv('ADMIN_ID')