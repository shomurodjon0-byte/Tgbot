import os
import time
import telebot
import google.generativeai as genai  # Eski, lekin serveringiz aniq taniyotgan kutubxona
from dotenv import load_dotenv

# 1. .env faylidan o'zgaruvchilarni yuklash
load_dotenv()

BOT_TOKEN = os.getenv("BOT_KEY")
AI_TOKEN = os.getenv("AI_KEY")

# 2. Eski SDK bo'yicha AI kalitini sozlash
genai.configure(api_key=AI_TOKEN)

# 3. Telegram bot ob'ektini yaratish
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 Salom! Men AI Memory Botman.\n\n"
        "Menga ixtiyoriy dasturlash savolingizni yozing, bajonidil javob beraman!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')  
        
        # Tizimli ko'rsatma (System Instruction) bilan modelni sozlash
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',  # Eng barqaror va tezkor model
            system_instruction=(
                "Siz sun'iy intellektga asoslangan, tajribali va yuqori malakali dasturlash mentorisiz. "
                "Javobingiz aniq, lo'nda va tushunarli o'zbek tilida bo'lsin. "
                "Agar kod yozsangiz, uni markdown kod bloklari ichida tushunarli izohlar bilan formatlang."
            )
        )
        
        # 4. So'rov yuborish
        response = model.generate_content(message.text)
        
        bot.reply_to(message, response.text)
        
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        bot.reply_to(message, "Kechirasiz, xatolik yuz berdi. Biroz kutib, qayta urinib ko'ring.")

print("Bot eski SDK bilan muvaffaqiyatli ishga tushdi...")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Tarmoq muammosi, 5 soniya kutamiz... Xato: {e}")
        time.sleep(5)
