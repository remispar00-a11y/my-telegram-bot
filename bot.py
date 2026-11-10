"""
بوت تيليجرام أساسي وقابل للتوسع
يعتمد على مكتبة python-telegram-bot (الإصدار 20+)

التثبيت:
    pip install python-telegram-bot --upgrade

التشغيل:
    1. احصل على توكن من @BotFather على تيليجرام
    2. ضع التوكن في متغير البيئة TELEGRAM_BOT_TOKEN
       أو استبدله مباشرة في المتغير BOT_TOKEN أدناه
    3. شغّل: python bot.py
"""

import os
import json
import logging
from datetime import datetime

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ----------------------------------------------------------------------
# الإعدادات
# ----------------------------------------------------------------------

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "ضع_التوكن_هنا")

NOTES_FILE = os.path.join(os.path.dirname(__file__), "notes.json")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# تخزين بسيط للملاحظات (ملف JSON محلي - يمكن استبداله بقاعدة بيانات لاحقاً)
# ----------------------------------------------------------------------

def load_notes() -> dict:
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_notes(notes: dict) -> None:
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


# ----------------------------------------------------------------------
# الأوامر
# ----------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "صديقي"
    await update.message.reply_text(
        f"أهلاً {name}! 👋\n\n"
        "أنا بوتك الخاص. هذه أوامري الحالية:\n"
        "/help - عرض المساعدة\n"
        "/note <نص> - حفظ ملاحظة\n"
        "/notes - عرض كل ملاحظاتك\n"
        "/clear - حذف كل ملاحظاتك\n\n"
        "أو فقط اكتب لي أي شيء وسأرد عليك."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "قائمة الأوامر:\n"
        "/start - رسالة الترحيب\n"
        "/help - هذه القائمة\n"
        "/note <نص> - حفظ ملاحظة جديدة\n"
        "/notes - عرض كل ملاحظاتك المحفوظة\n"
        "/clear - حذف كل ملاحظاتك\n\n"
        "يمكنك أيضاً كتابة أي رسالة عادية وسأرد عليها."
    )


async def add_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = " ".join(context.args)

    if not text:
        await update.message.reply_text("اكتب الملاحظة بعد الأمر، مثال:\n/note اشتري خبزاً غداً")
        return

    notes = load_notes()
    notes.setdefault(user_id, [])
    notes[user_id].append({
        "text": text,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_notes(notes)

    await update.message.reply_text("تم حفظ الملاحظة ✅")


async def list_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    notes = load_notes().get(user_id, [])

    if not notes:
        await update.message.reply_text("لا توجد ملاحظات محفوظة بعد.")
        return

    lines = [f"{i+1}. {n['text']}  ({n['date']})" for i, n in enumerate(notes)]
    await update.message.reply_text("ملاحظاتك:\n" + "\n".join(lines))


async def clear_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    notes = load_notes()
    notes[user_id] = []
    save_notes(notes)
    await update.message.reply_text("تم حذف كل ملاحظاتك 🗑️")


# ----------------------------------------------------------------------
# الرد على أي رسالة نصية عادية (هنا تربط لاحقاً أي نموذج ذكاء اصطناعي)
# ----------------------------------------------------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # TODO: هنا يمكنك استدعاء أي API خارجي للرد بذكاء بدل هذا الرد الثابت
    reply = f"استلمت رسالتك: \"{user_text}\"\n(اربط هنا أي نموذج ذكاء اصطناعي للرد الذكي)"

    await update.message.reply_text(reply)


# ----------------------------------------------------------------------
# نقطة التشغيل
# ----------------------------------------------------------------------

def main():
    if BOT_TOKEN == "ضع_التوكن_هنا":
        print("⚠️  ضع توكن البوت في متغير البيئة TELEGRAM_BOT_TOKEN أو داخل الملف مباشرة.")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("note", add_note))
    app.add_handler(CommandHandler("notes", list_notes))
    app.add_handler(CommandHandler("clear", clear_notes))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 البوت يعمل الآن...")
    app.run_polling()


if __name__ == "__main__":
    main()
