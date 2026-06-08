import os
import time
import telebot
from groq import Groq
from dotenv import load_dotenv

# ── 1. Muhit o'zgaruvchilarini yuklash ────────────────────────────────────────
load_dotenv()

BOT_TOKEN = os.getenv("BOT_KEY")
GROQ_KEY  = os.getenv("GROQ_KEY")

# ── 2. Groq client ────────────────────────────────────────────────────────────
client = Groq(api_key=GROQ_KEY)
MODEL  = "llama-3.3-70b-versatile"   # Bepul, tez va kuchli model

# ── 3. Bot ob'ekti ────────────────────────────────────────────────────────────
bot = telebot.TeleBot(BOT_TOKEN)

# ── 4. Foydalanuvchi profillari ───────────────────────────────────────────────
user_profiles: dict[int, dict] = {}

SUPPORTED_LANGS = {"uz": "🇺🇿 O'zbek", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}

CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".java", ".c", ".cpp", ".cs",
    ".html", ".css", ".json", ".xml", ".yaml", ".yml",
    ".sql", ".sh", ".txt", ".md", ".go", ".rs", ".php", ".rb"
}

# ── 5. Yordamchi funksiyalar ──────────────────────────────────────────────────

def get_profile(user_id: int, first_name: str = "Foydalanuvchi") -> dict:
    if user_id not in user_profiles:
        user_profiles[user_id] = {
            "lang": "uz",
            "name": first_name,
            "questions_count": 0,
        }
    return user_profiles[user_id]


def system_prompt(lang: str) -> str:
    prompts = {
        "uz": (
            "Siz tajribali dasturlash mentorisiz. "
            "Javoblaringiz aniq, lo'nda va faqat O'ZBEK TILIDA bo'lsin. "
            "Kodlarni markdown bloklar ichida izohlar bilan yozing. "
            "Muammoning sababini va best practice'larni tushuntiring."
            "imloviy hatolarsiz aniq va ravon javob yozing."
        ),
        "ru": (
            "Вы опытный наставник по программированию. "
            "Отвечайте чётко, кратко и ТОЛЬКО НА РУССКОМ ЯЗЫКЕ. "
            "Форматируйте код в markdown-блоках с комментариями. "
            "Объясняйте причину проблемы и лучшие практики."
        ),
        "en": (
            "You are an experienced programming mentor. "
            "Answer clearly, concisely and ONLY IN ENGLISH. "
            "Format code in markdown blocks with comments. "
            "Explain the root cause and best practices."
        ),
    }
    return prompts.get(lang, prompts["uz"])


def ask_groq(prompt_text: str, lang: str) -> str:
    """Groq API ga so'rov yuborib javob qaytaradi."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt(lang)},
            {"role": "user",   "content": prompt_text},
        ],
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content


# ── 6. /start va /help ────────────────────────────────────────────────────────
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    profile = get_profile(message.from_user.id, message.from_user.first_name)
    text = (
        f"👋 Salom, *{profile['name']}*!\n\n"
        "Men Groq AI asosida ishlaydigan dasturlash mentoriminan.\n\n"
        "📌 *Buyruqlar:*\n"
        "• /lang — tilni o'zgartirish (🇺🇿 🇷🇺 🇬🇧)\n"
        "• /profile — profilingizni ko'rish\n"
        "• /help — yordam\n\n"
        "💡 *Nima qila olaman?*\n"
        "• Har qanday savollarga javob beraman\n"
        "• Fayl yoki kodingizni tahlil qilaman\n"
        "• O'zbek, Rus va Ingliz tillarida javob beraman\n\n"
        "Savolingizni yozing yoki fayl yuboring! 🚀"
    )
    bot.reply_to(message, text, parse_mode="Markdown")


# ── 7. /lang — til tanlash ────────────────────────────────────────────────────
@bot.message_handler(commands=["lang"])
def choose_language(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("🇺🇿 O'zbek", "🇷🇺 Русский", "🇬🇧 English")
    bot.reply_to(
        message,
        "🌐 Tilni tanlang / Выберите язык / Choose language:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, set_language)


def set_language(message):
    lang_map = {
        "🇺🇿 O'zbek": "uz",
        "🇷🇺 Русский": "ru",
        "🇬🇧 English": "en",
    }
    chosen = lang_map.get(message.text)
    profile = get_profile(message.from_user.id, message.from_user.first_name)

    if chosen:
        profile["lang"] = chosen
        confirmations = {
            "uz": "✅ Til o'zgartirildi: 🇺🇿 O'zbek",
            "ru": "✅ Язык изменён: 🇷🇺 Русский",
            "en": "✅ Language changed: 🇬🇧 English",
        }
        bot.reply_to(message, confirmations[chosen],
                     reply_markup=telebot.types.ReplyKeyboardRemove())
    else:
        bot.reply_to(message, "❌ Noma'lum til. /lang buyrug'ini qayta yuboring.",
                     reply_markup=telebot.types.ReplyKeyboardRemove())


# ── 8. /profile ───────────────────────────────────────────────────────────────
@bot.message_handler(commands=["profile"])
def show_profile(message):
    profile = get_profile(message.from_user.id, message.from_user.first_name)
    lang_label = SUPPORTED_LANGS.get(profile["lang"], "—")
    text = (
        f"👤 *Profil*\n\n"
        f"• Ism: *{profile['name']}*\n"
        f"• Til: *{lang_label}*\n"
        f"• Savollar soni: *{profile['questions_count']}*\n\n"
        "Tilni o'zgartirish uchun /lang"
    )
    bot.reply_to(message, text, parse_mode="Markdown")


# ── 9. Fayl tahlili ───────────────────────────────────────────────────────────
@bot.message_handler(content_types=["document"])
def handle_document(message):
    profile = get_profile(message.from_user.id, message.from_user.first_name)
    doc = message.document
    file_name = doc.file_name or "file"
    _, ext = os.path.splitext(file_name.lower())

    if ext not in CODE_EXTENSIONS:
        bot.reply_to(
            message,
            f"⚠️ `{file_name}` qo'llab-quvvatlanmaydi.\n"
            f"Ruxsat etilgan: {', '.join(sorted(CODE_EXTENSIONS))}",
            parse_mode="Markdown",
        )
        return

    if doc.file_size and doc.file_size > 1_000_000:
        bot.reply_to(message, "⚠️ Fayl hajmi 1 MB dan oshmasligi kerak.")
        return

    bot.send_chat_action(message.chat.id, "typing")

    try:
        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)
        code_text = downloaded.decode("utf-8", errors="replace")

        user_note = f"\nFoydalanuvchi izoh: {message.caption}" if message.caption else ""
        prompt = (
            f"Quyidagi `{file_name}` faylini tahlil qil:{user_note}\n\n"
            f"```{ext.lstrip('.')}\n{code_text}\n```\n\n"
            "1. Kodning umumiy maqsadini tushuntir.\n"
            "2. Xatolar yoki potensial muammolarni ko'rsat.\n"
            "3. Yaxshilash tavsiyalarini ber.\n"
            "4. Kerak bo'lsa, to'g'rilangan kod ko'rsat."
        )

        answer = ask_groq(prompt, profile["lang"])
        profile["questions_count"] += 1
        bot.reply_to(message, answer)

    except UnicodeDecodeError:
        bot.reply_to(message, "⚠️ Faylni o'qib bo'lmadi. Faqat matnli fayllar qabul qilinadi.")
    except Exception as e:
        print(f"Fayl xatoligi: {e}")
        bot.reply_to(message, f"❌ Xatolik: {str(e)}")


# ── 10. Matnli xabar ──────────────────────────────────────────────────────────
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    profile = get_profile(message.from_user.id, message.from_user.first_name)
    bot.send_chat_action(message.chat.id, "typing")

    try:
        answer = ask_groq(message.text, profile["lang"])
        profile["questions_count"] += 1
        bot.reply_to(message, answer)

    except Exception as e:
        print(f"Xatolik: {e}")
        error_msgs = {
            "uz": f"❌ Xatolik: {str(e)}",
            "ru": f"❌ Ошибка: {str(e)}",
            "en": f"❌ Error: {str(e)}",
        }
        bot.reply_to(message, error_msgs.get(profile["lang"], error_msgs["uz"]))


# ── 11. Ishga tushirish ───────────────────────────────────────────────────────
print("✅ Bot muvaffaqiyatli ishga tushdi (Groq AI)...")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"⚠️  Tarmoq muammosi, 5 soniya kutamiz... Xato: {e}")
        time.sleep(5)
