import logging
import json
import schedule
import time
import os
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# 설정
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
USER_ID = None
DATA_FILE = "supplement_state.json"
CONFIG_FILE = "supplement_config.json"
PINNED_MSG_ID_FILE = "pinned_msg_id.txt"

default_routine = {
    "morning": [
        "투퍼데이 (1정)",
        "엘카르니틴",
        "비트뿌리 or 시트룰린",
        "아슈와간다",
        "글리신 + 테아닌 (선택)"
        "B Complex"
    ],
    "evening": [
        "투퍼데이 (1정)",
        "오메가3",
        "쏜 SAT",
        "인돌3카비놀",
        "아연 + 구리",
        "CoQ10",
        "NAC (선택)"
    ],
    "night": [
        "마그네슘 (글리시네이트 or 트레오네이트)"
    ]
}

default_times = {
    "morning": "09:00",
    "evening": "20:30",
    "night": "23:30"
}

reminder_delay_minutes = 50

# 파일 불러오기 및 저장
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

# 체크리스트 생성
def build_checklist(time_key, config):
    items = config["routine"][time_key]
    return "\n".join([f"☑️ {item}" for item in items])

def build_status_summary(state):
    return f"📆 Day {state['day']} 진행 현황\n✅ 아침: {'O' if state['morning'] else 'X'} | ✅ 저녁: {'O' if state['evening'] else 'X'} | ✅ 취침: {'O' if state['night'] else 'X'}"

# 알림 전송
async def send_checklist(bot, time_key):
    config = load_config()
    state = load_state()
    checklist = build_checklist(time_key, config)
    text = f"🕘 [Day {state['day']}] {time_key.upper()} 루틴입니다!\n\n{checklist}"
    buttons = [[InlineKeyboardButton("✅ 복용 완료", callback_data=f"{time_key}_done")]]
    markup = InlineKeyboardMarkup(buttons)
    msg = await bot.send_message(chat_id=USER_ID, text=text, reply_markup=markup)

    # 시간 기록
    now_str = datetime.now().isoformat()
    state["last_check"][time_key] = now_str
    save_state(state)

    # 핀 메시지 업데이트
    await update_pin(bot)

# 복용 완료 처리
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

# 핀 메시지 업데이트
async def update_pin(bot):
    state = load_state()
    summary = build_status_summary(state)
    msg = await bot.send_message(chat_id=USER_ID, text=summary)
    try:
        await bot.pin_chat_message(chat_id=USER_ID, message_id=msg.message_id, disable_notification=True)
    except:
        pass

# 시작 명령
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global USER_ID
    USER_ID = update.effective_chat.id
    await update.message.reply_text("✅ 영양제 루틴 봇을 시작합니다.")
    await update_pin(context.bot)

# 시간 설정
async def set_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 2 or args[0] not in ["morning", "evening", "night"]:
        await update.message.reply_text("❗ 사용법: /settime [morning|evening|night] [HH:MM]")
        return

    config = load_config()
    config["times"][args[0]] = args[1]
    save_config(config)
    await update.message.reply_text(f"⏰ {args[0].capitalize()} 알림 시간이 {args[1]}로 설정되었습니다.")

# 리마인더 체크
async def reminder_task(bot):
    state = load_state()
    for time_key in ["morning", "evening", "night"]:
        if not state[time_key] and time_key in state["last_check"]:
            last_time = datetime.fromisoformat(state["last_check"][time_key])
            if datetime.now() - last_time > timedelta(minutes=reminder_delay_minutes):
                checklist = build_checklist(time_key, load_config())
                text = f"⏰ [리마인더] {time_key.upper()} 루틴 체크 안 하셨습니다!\n\n{checklist}"
                buttons = [[InlineKeyboardButton("✅ 지금 복용 완료", callback_data=f"{time_key}_done")]]
                markup = InlineKeyboardMarkup(buttons)
                await bot.send_message(chat_id=USER_ID, text=text, reply_markup=markup)

# 스케줄러
def schedule_tasks(app):
    config = load_config()
    for time_key in ["morning", "evening", "night"]:
        schedule.every().day.at(config["times"][time_key]).do(lambda tk=time_key: app.create_task(send_checklist(app.bot, tk)))

    while True:
        schedule.run_pending()
        time.sleep(30)

# 주기적 리마인더 실행
def periodic_reminder(app):
    while True:
        time.sleep(60)
        app.create_task(reminder_task(app.bot))

# 실행
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("settime", set_time))
    app.add_handler(CallbackQueryHandler(button_handler))

    import threading
    threading.Thread(target=schedule_tasks, args=(app,), daemon=True).start()
    threading.Thread(target=periodic_reminder, args=(app,), daemon=True).start()

    app.run_polling()

if __name__ == "__main__":
    main()
