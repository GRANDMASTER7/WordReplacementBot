import asyncio
import os
import json
import io
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEBUG = os.getenv("DEBUG", "False")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

DATA_PATH = "data/added_words.json"

def load_words():
    if not os.path.exists(DATA_PATH):
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_words(words):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

@dp.message(Command("add"))
async def cmd_add(message: Message):
    word = message.text.split(maxsplit=1)[-1].strip().lower()
    words = load_words()
    if word in words:
        await message.answer(f"⚠️ Слово '{word}' уже есть")
    else:
        words.append(word)
        save_words(words)
        await message.answer(f"✅ Добавлено: {word}")

@dp.message(Command("remove"))
async def cmd_remove(message: Message):
    word = message.text.split(maxsplit=1)[-1].strip().lower()
    words = load_words()
    if word in words:
        words.remove(word)
        save_words(words)
        await message.answer(f"🗑 Удалено: {word}")
    else:
        await message.answer(f"❌ Слово '{word}' не найдено")

@dp.message(Command("list"))
async def cmd_list(message: Message):
    words = load_words()
    if not words:
        await message.answer("📭 Список пуст")
    else:
        await message.answer("📋 Список слов:\n" + "\n".join(f"• {w}" for w in words))

@dp.message(Command("export"))
async def cmd_export(message: Message):
    words = load_words()
    text = "\n".join(words)
    file = io.BytesIO(text.encode())
    await message.answer_document(types.InputFile(file, filename="added_words.txt"))

@dp.message(Command("status"))
async def cmd_status(message: Message):
    words = load_words()
    await message.answer(f"📊 Статус:\n• Слов в списке: {len(words)}\n• DEBUG: {DEBUG}")

@dp.message(Command("menu"))
async def cmd_menu(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить", callback_data="add"),
         InlineKeyboardButton(text="🗑 Удалить", callback_data="remove")],
        [InlineKeyboardButton(text="📋 Список", callback_data="list"),
         InlineKeyboardButton(text="📤 Экспорт", callback_data="export")]
    ])
    await message.answer("📱 Меню управления:", reply_markup=kb)

@dp.callback_query(lambda c: c.data in ["add", "remove", "list", "export"])
async def handle_buttons(callback: types.CallbackQuery):
    if callback.data == "list":
        words = load_words()
        text = "📋 Список:\n" + "\n".join(f"• {w}" for w in words) if words else "📭 Список пуст"
        await callback.message.answer(text)
    elif callback.data == "export":
        words = load_words()
        file = io.BytesIO("\n".join(words).encode())
        await callback.message.answer_document(types.InputFile(file, filename="added_words.txt"))
    elif callback.data == "add":
        await callback.message.answer("✏️ Напиши: /add слово")
    elif callback.data == "remove":
        await callback.message.answer("✏️ Напиши: /remove слово")
    await callback.answer()

# ✅ Правильный запуск через async def main()
async def main():
    await dp.start_polling(bot)

# 🚀 Запуск через asyncio.run()
if __name__ == "__main__":
    asyncio.run(main())