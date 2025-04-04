
import logging
import json
import schedule
import time
import os
import pytz
import asyncio
import threading
from functools import partial
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
USER_ID = int(os.environ.get("TELEGRAM_USER_ID"))
DATA_FILE = "supplement_state.json"
CONFIG_FILE = "supplement_config.json"

default_routine = {
    "morning": ["투퍼데이 (1정)", "엘카르니틴", "비트뿌리 or 시트룰린", "아슈와간다", "프로바이오틱스",
                "비오틴", "글리신 + 테아닌", "B Complex", "비타민 C 1000mg (공복)", "비타민 C 1000mg (아침 식후)"],
    "evening": ["투퍼데이 (1정)", "오메가3", "쏜 SAT", "인돌3카비놀", "아연 + 구리",
                "CoQ10", "NAC", "비타민 C 1000mg (저녁 식후)"],
    "night": ["마그네슘", "글리신 + 테아닌", "비타민 C 1000mg (취침 전)"]
}

default_times = {"morning": "09:00", "evening": "20:30", "night": "23:30"}
reminder_delay_minutes = 50

def load_state():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"day": 1, "morning": False, "evening": False, "night": False, "last_check": {}}

def save_state(state):
    with open(DATA_FILE, "w") as f:
        json.dump(state, f)

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        config = {"routine": default_routine, "times": default_times}
        save_config(config)
        return config

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def build_checklist(time_key, config):
    items = config["routine"][time_key]
    return "\n".join([f"☑️ {item}" for item in items])

def build_status_summary(state):
    return f"📆 Day {state['day']} 진행 현황\n✅ 아침: {'O' if state['morning'] else 'X'} | ✅ 저녁: {'O' if state['evening'] else 'X'} | ✅ 취침: {'O' if state['night'] else 'X'}"

async def send_checklist(bot, time_key, custom_day=None):
    config = load_config()
    state = load_state()
    day = state["day"] if custom_day is None else custom_day
    checklist = build_checklist(time_key, config)
    text = f"🕘 [Day {day}] {time_key.upper()} 루틴입니다!\n\n{checklist}"
    buttons = [[InlineKeyboardButton("✅ 지금 복용 완료", callback_data=f"{time_key}_done")]]
    markup = InlineKeyboardMarkup(buttons)
    await bot.send_message(chat_id=USER_ID, text=text, reply_markup=markup)
    state["last_check"][time_key] = datetime.now().isoformat()
    save_state(state)
    await update_pin(bot)

async def update_pin(bot):
    state = load_state()
    summary = build_status_summary(state)
    msg = await bot.send_message(chat_id=USER_ID, text=summary)
    try:
        await bot.pin_chat_message(chat_id=USER_ID, message_id=msg.message_id, disable_notification=True)
    except:
        pass

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = load_state()
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.endswith("_done"):
        time_key = data.replace("_done", "")
        state[time_key] = True
        save_state(state)

        if all([state["morning"], state["evening"], state["night"]]):
            state["day"] += 1
            state["morning"] = state["evening"] = state["night"] = False
            state["last_check"] = {}
            save_state(state)
            await query.edit_message_text(f"🎉 오늘 루틴 완료! Day {state['day']}로 넘어갑니다.")
        else:
            await query.edit_message_text(f"✅ {time_key.upper()} 루틴 완료! 다음 루틴 알림을 기다려 주세요.")

        await update_pin(context.bot)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global USER_ID
    USER_ID = update.effective_chat.id
    await update.message.reply_text("✅ 영양제 루틴 봇을 시작합니다.")
    await update_pin(context.bot)

async def set_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from schedule import clear
    args = context.args
    if len(args) != 2 or args[0] not in ["morning", "evening", "night"]:
        await update.message.reply_text("❗ 사용법: /settime [morning|evening|night] [HH:MM]")
        return
    config = load_config()
    config["times"][args[0]] = args[1]
    save_config(config)
    await update.message.reply_text(f"⏰ {args[0].capitalize()} 알림 시간이 {args[1]}로 설정되었습니다.")
    clear()
    loop = asyncio.get_event_loop()
    for time_key in ["morning", "evening", "night"]:
        kst_time = config["times"][time_key]
        utc_time = convert_kst_to_utc_string(kst_time)
        job = partial(asyncio.run_coroutine_threadsafe, send_checklist(context.bot, time_key), loop)
        schedule.every().day.at(utc_time).do(job)

async def reminder_task(bot):
    state = load_state()
    for time_key in ["morning", "evening", "night"]:
        if not state[time_key] and time_key in state["last_check"]:
            last_time = datetime.fromisoformat(state["last_check"][time_key])
            if datetime.now() - last_time > timedelta(minutes=reminder_delay_minutes):
                await send_checklist(bot, time_key)

KST = pytz.timezone("Asia/Seoul")

def convert_kst_to_utc_string(kst_time_str):
    kst_time = datetime.strptime(kst_time_str, "%H:%M")
    today = datetime.now(KST).date()
    kst_dt = KST.localize(datetime.combine(today, kst_time.time()))
    utc_dt = kst_dt.astimezone(pytz.utc)
    return utc_dt.strftime("%H:%M")

def schedule_tasks(app, loop):
    config = load_config()
    for time_key in ["morning", "evening", "night"]:
        kst_time = config["times"][time_key]
        utc_time = convert_kst_to_utc_string(kst_time)
        job = partial(asyncio.run_coroutine_threadsafe, send_checklist(app.bot, time_key), loop)
        schedule.every().day.at(utc_time).do(job)

    schedule.every().day.at(convert_kst_to_utc_string("08:00")).do(
        lambda: asyncio.run_coroutine_threadsafe(
            app.bot.send_message(chat_id=USER_ID, text="🌅 좋은 아침입니다! 오늘의 루틴을 확인해 주세요."), loop)
    )

    while True:
        schedule.run_pending()
        time.sleep(30)

def periodic_reminder(app, loop):
    while True:
        time.sleep(60)
        asyncio.run_coroutine_threadsafe(reminder_task(app.bot), loop)

async def show_times(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = load_config()
    times = config["times"]
    msg = (
        "🕰️ 현재 알림 시간 (KST 기준):\n"
        f"☀️ 아침: {times['morning']}\n"
        f"🌇 저녁: {times['evening']}\n"
        f"🌙 취침: {times['night']}"
    )
    await update.message.reply_text(msg)

async def test_alarm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_checklist(context.bot, "morning")

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and context.args[0] in ["morning", "evening", "night"]:
        await send_checklist(context.bot, context.args[0])
    else:
        await update.message.reply_text("❗ 사용법: /remind [morning|evening|night]")

async def forcecomplete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 1 or args[0] not in ["morning", "evening", "night"]:
        await update.message.reply_text("❗ 사용법: /forcecomplete [morning|evening|night]")
        return

    time_key = args[0]
    state = load_state()
    state[time_key] = True
    save_state(state)

    if all([state["morning"], state["evening"], state["night"]]):
        state["day"] += 1
        state["morning"] = state["evening"] = state["night"] = False
        state["last_check"] = {}
        save_state(state)
        await update.message.reply_text(f"🎉 오늘 루틴 완료! Day {state['day']}로 넘어갑니다.")
    else:
        await update.message.reply_text(f"✅ {time_key.upper()} 루틴 강제 완료!")

    await update_pin(context.bot)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("settime", set_time))
    app.add_handler(CommandHandler("showtimes", show_times))
    app.add_handler(CommandHandler("testalarm", test_alarm))
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(CommandHandler("forcecomplete", forcecomplete))
    app.add_handler(CallbackQueryHandler(button_handler))
    loop = asyncio.get_event_loop()
    threading.Thread(target=schedule_tasks, args=(app, loop), daemon=True).start()
    threading.Thread(target=periodic_reminder, args=(app, loop), daemon=True).start()
    app.run_polling()

if __name__ == "__main__":
    main()
