import os
import time
import telebot
from dotenv import load_dotenv
# ESKI import google.generativeai O'RNIGA FAQAT SHUNI YOZING:
from genai import Client  

# 1. .env faylidan o'zgaruvchilarni yuklash
load_dotenv()

BOT_TOKEN = os.getenv("BOT_KEY")
AI_TOKEN = os.getenv("AI_KEY")

# 2. Yangi Google GenAI mijozini yaratish
ai_client = Client(api_key=AI_TOKEN)

# 3. Telegram bot ob'ektini yaratish
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 Salom! Men eng so'nggi Google GenAI SDK bilan ishlaydigan botman.\n\n"
        "Menga ixtiyoriy dasturlash yoki boshqa qiziqarli savolingizni yozing!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Foydalanuvchiga javob tayyorlanayotganini bildirish
        bot.send_chat_action(message.chat.id, 'typing')  
        
        # Mentor ko'rsatmalari (System Instruction)
        system_instruction = (
            "Siz sun'iy intellektga asoslangan, tajribali va yuqori malakali dasturlash mentorisiz. "
            "Javobingiz aniq, lo'nda va tushunarli o'zbek tilida bo'lsin. "
            "Agar kod yozsangiz, uni markdown kod bloklari ichida tushunarli izohlar (comments) bilan formatlang."
        )
        
        # 4. Yangi SDK formatida so'rov yuborish
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text,
            config={
                'system_instruction': system_instruction,
                'max_output_tokens': 700
            }
        )
        
        bot.reply_to(message, response.text)
        
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        bot.reply_to(message, "Kechirasiz, xatolik yuz berdi. Biroz kutib, qayta urinib ko'ring.")

# Botni uzluksiz ishlash rejimiga tushirish
print("Bot yangi SDK da muvaffaqiyatli ishga tushdi...")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Tarmoq muammosi, 5 soniya kutamiz... Xato: {e}")
        time.sleep(5)
