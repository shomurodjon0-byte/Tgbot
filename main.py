import os
import time
import telebot
import google.generativeai as genai
from dotenv import load_dotenv

# 1. .env faylidan o'zgaruvchilarni tizimga yuklash
load_dotenv()

# 2. Kalitlarni o'zgaruvchilarga olish
BOT_TOKEN = os.getenv("BOT_KEY")
AI_TOKEN = os.getenv("AI_KEY")

# 3. Google Gemini API ni sozlash
genai.configure(api_key=AI_TOKEN)
# Eng oxirgi va barqaror model versiyasi
# Eng oxirgi va tezkor Gemini modeli
model = genai.GenerativeModel('gemini-2.5-flash')
# 4. Telegram bot ob'ektini yaratish
bot = telebot.TeleBot(BOT_TOKEN)

# Start va Help buyruqlari uchun handler
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 Salom! Men Google Gemini AI bilan ishlaydigan botman.\n\n"
        "Menga ixtiyoriy savolingizni yozing, men yordam berishga tayyorman!"
    )
    bot.reply_to(message, welcome_text)

# Oddiy matnli xabarlar uchun handler
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Foydalanuvchiga bot o'ylayotganini bildirish
        bot.send_chat_action(message.chat.id, 'typing')  
        
        # Google Gemini AI ga so'rov yuborish
        # Tizimga dasturlash mentori ekanligini eslatib matn yuboramiz
        prompt = (
            "Siz sun'iy intellektga asoslangan, tajribali va yuqori malakali dasturlash mentorisiz. "
            "Foydalanuvchining savoliga quyidagi qoidalarga qat'iy amal qilgan holda javob bering:\n"
            "1. Javobingiz aniq, lo'nda va tushunarli o'zbek tilida bo'lsin.\n"
            "2. Agar kod yozsangiz, uni tushunarli izohlar (comments) bilan boyiting va markdown (kod bloklari) ichida chiroyli formatlang.\n"
            "3. Muammoni shunchaki hal qilib bermasdan, uning sababini va eng yaxshi amaliyotlarni (Best Practices) ham qisqacha tushuntiring.\n"
            "4. Murakkab atamalarni sodda tillar bilan, dasturchilar tushunadigan uslubda yetkazing.\n\n"
            f"Foydalanuvchi savoli:\n{message.text}"
        )
        response = model.generate_content(prompt)
        
        # Javobni olish
        javob = response.text
        
        # Foydalanuvchiga javobni qaytarish
        bot.reply_to(message, javob)
        
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        bot.reply_to(message, "Kechirasiz, xatolik yuz berdi. Biroz kutib, qayta urinib ko'ring.")

# Botni uzluksiz ishlash rejimiga tushirish
print("Bot muvaffaqiyatli ishga tushdi...")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Tarmoq muammosi, 5 soniya kutamiz... Xato: {e}")
        time.sleep(5)