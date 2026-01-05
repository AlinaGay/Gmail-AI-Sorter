# check_models.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key найден: {'Да' if api_key else 'Нет'}")

if not api_key:
    print("Ошибка: GEMINI_API_KEY не найден в .env файле")
    exit(1)

genai.configure(api_key=api_key)

print("\nДоступные модели для generateContent:")
print("-" * 50)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  {model.name}")