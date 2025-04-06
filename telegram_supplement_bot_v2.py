
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
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

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
    print(f"⏰ send_checklist 실행됨: {time_key} at {datetime.now()}")
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
        print(f"📅 스케줄 등록됨: {time_key} / KST: {kst_time} / UTC: {utc_time}")
        job = partial(asyncio.run_coroutine_threadsafe, send_checklist(app.bot, time_key), loop)
        schedule.every().day.at(utc_time).do(job)

    # 아침 메시지
    print("🌅 아침 루틴 메시지 등록됨")
    schedule.every().day.at(convert_kst_to_utc_string("08:00")).do(
        lambda: asyncio.run_coroutine_threadsafe(
            app.bot.send_message(chat_id=USER_ID, text="🌅 좋은 아침입니다! 오늘의 루틴을 확인해 주세요."), loop)
    )

    while True:
        try:
            print(f"🔁 schedule tick: {datetime.utcnow().isoformat()}")
            schedule.run_pending()
        except Exception as e:
            print(f"❌ 스케줄 실행 중 오류 발생: {e}")
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

# /remove 명령어
async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or args[0] not in ["morning", "evening", "night"]:
        await update.message.reply_text("❗ 사용법: /remove [morning|evening|night]")
        return

    time_key = args[0]
    config = load_config()
    items = config["routine"][time_key]

    if not items:
        await update.message.reply_text("❗ 삭제할 항목이 없습니다.")
        return

    buttons = [
        [InlineKeyboardButton(f"❌ {item}", callback_data=f"remove_{time_key}_{i}")]
        for i, item in enumerate(items)
    ]
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(f"🧹 {time_key.upper()} 루틴에서 삭제할 항목을 선택하세요:", reply_markup=markup)

# 삭제 콜백 처리
async def remove_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("remove_"):
        _, time_key, index = data.split("_")
        index = int(index)

        config = load_config()
        try:
            removed = config["routine"][time_key].pop(index)
            save_config(config)
            await query.edit_message_text(f"✅ `{removed}` 항목이 {time_key.upper()} 루틴에서 삭제되었습니다.")
        except IndexError:
            await query.edit_message_text("❗ 잘못된 인덱스입니다.")

# 상태를 정의
ADD_TIME, ADD_ITEM = range(2)

# /add 진입 시
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("☀️ 아침", callback_data="add_morning")],
        [InlineKeyboardButton("🌇 저녁", callback_data="add_evening")],
        [InlineKeyboardButton("🌙 취침", callback_data="add_night")]
    ]
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("➕ 어떤 시간대에 추가할까요?", reply_markup=markup)
    return ADD_TIME

# 시간대 버튼 클릭 후
async def add_time_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    time_key = query.data.replace("add_", "")
    context.user_data["add_time_key"] = time_key
    await query.edit_message_text(f"📝 `{time_key.upper()}` 루틴에 추가할 항목을 입력해 주세요:")
    return ADD_ITEM

# 항목 입력 처리
async def add_item_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time_key = context.user_data.get("add_time_key")
    new_item = update.message.text.strip()

    config = load_config()
    config["routine"][time_key].append(new_item)
    save_config(config)

    await update.message.reply_text(f"✅ `{new_item}` 항목이 `{time_key.upper()}` 루틴에 추가되었습니다.")
    return ConversationHandler.END

# 대화 취소 처리
async def add_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ 추가를 취소했습니다.")
    return ConversationHandler.END


def main():
    add_conv = ConversationHandler(
    entry_points=[CommandHandler("add", add)],
    states={
        ADD_TIME: [CallbackQueryHandler(add_time_selected, pattern="^add_")],
        ADD_ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_item_received)],
    },
    fallbacks=[CommandHandler("cancel", add_cancel)],
)

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("settime", set_time))
    app.add_handler(CommandHandler("showtimes", show_times))
    app.add_handler(CommandHandler("testalarm", test_alarm))
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(CommandHandler("forcecomplete", forcecomplete))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CallbackQueryHandler(remove_button_handler, pattern="^remove_"))
    app.add_handler(add_conv)


    loop = asyncio.get_event_loop()
    threading.Thread(target=schedule_tasks, args=(app, loop), daemon=True).start()
    threading.Thread(target=periodic_reminder, args=(app, loop), daemon=True).start()
    app.run_polling()

if __name__ == "__main__":
    main()
