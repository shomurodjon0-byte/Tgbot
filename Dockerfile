FROM python:3.11-slim

WORKDIR /app

# Kutubxonalar ro'yxatini konteyner ichiga ko'chiramiz
COPY requirements.txt .

# Railway xotirasidan (keshdan) foydalanmasligi uchun toza o'rnatamiz
RUN pip install --no-cache-dir -r requirements.txt

# main.py va qolgan barcha fayllarni ko'chiramiz
COPY . .

# Botni ishga tushirish buyrug'i
CMD ["python", "main.py"]
