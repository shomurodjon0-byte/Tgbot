import time
import telebot
import google.generativeai as genai

# 🔥 SERVER CHALKAShIB KETMASLIGI UChUN TOKENLARNI TO'G'RIDAN-TO'G'RI ShUYERGA YOZAMIZ:
BOT_TOKEN = "Sizning_Telegram_Bot_Tokeningizni_Shu_Yerdagi_Qo_shtirnoq_Ichiga_Yozing"
AI_TOKEN = "Sizning_Gemini_API_Kalitingizni_Shu_Yerdagi_Qo_shtirnoq_Ichiga_Yozing"

# 1. AI kalitini sozlash
genai.configure(api_key=AI_TOKEN)

# 2. Telegram bot ob'ektini yaratish
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 Salom! Men muvaffaqiyatli ishga tushgan AI Memory Botman.\n\n"
        "Menga ixtiyoriy dasturlash savolingizni yozing!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')  
        
        # Tizimli ko'rsatma (System Instruction)
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=(
                "Siz sun'iy intellektga asoslangan, tajribali va yuqori malakali dasturlash mentorisiz. "
                "Javobingiz aniq, lo'nda va tushunarli o'zbek tilida bo'lsin. "
                "Agar kod yozsangiz, uni markdown kod bloklari ichida tushunarli izohlar bilan formatlang."
            )
        )
        
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
        
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        bot.reply_to(message, "Kechirasiz, xatolik yuz berdi. Qayta urinib ko'ring.")

print("Bot 100% muvaffaqiyatli ishga tushdi...")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Xatolik: {e}")
        time.sleep(5)
