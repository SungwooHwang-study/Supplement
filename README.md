# Supplement Routine Telegram Bot

A personal Telegram bot that helps you manage your supplement intake with daily routine checklists and reminders.

## ✨ Features

- ✅ Interactive checklist buttons (morning/evening/night)
- 🔔 Scheduled daily reminders (adjustable by `/settime`)
- 🔁 Automatic day transition after completing all routines
- 🌅 Good morning message at 08:00 KST
- 🔃 `/remind [time]` to manually resend checklist (morning, evening, night)
- 🛠️ `/forcecomplete [time]` to mark routine done manually
- 🕰️ `/showtimes` to display current alarm times
- 🧪 `/testalarm` to send test checklist

## 📦 File Structure

- `supplement_state.json`: Tracks day & routine completion status
- `supplement_config.json`: Stores routine items & alarm times
- `telegram_supplement_bot_v2.py`: Main bot logic

## 🛠️ Setup

1. Set secrets on [Fly.io](https://fly.io):
    ```bash
    fly secrets set TELEGRAM_BOT_TOKEN=<your_bot_token>
    fly secrets set TELEGRAM_USER_ID=<your_user_id>
    ```

2. Deploy with Fly.io:
    ```bash
    fly deploy
    ```

3. Start bot by sending `/start` in Telegram.

## 🔄 Commands

| Command               | Description |
|------------------------|-------------|
| `/start`              | Start the bot |
| `/settime time HH:MM` | Set routine time (e.g., `/settime morning 09:30`) |
| `/showtimes`          | Show current alarm times |
| `/testalarm`          | Send a test checklist |
| `/remind time`        | Manually resend checklist |
| `/forcecomplete time` | Force complete a routine time manually |

## ⏰ Timezone

All alarm times are set in **KST (Asia/Seoul)** and internally converted to UTC for scheduling.

## 📌 Notes

- If you miss a day, you can manually remind yourself or force complete a section.
- You can adjust times anytime with `/settime`.
- The bot uses `schedule` + `asyncio` with threads for async reminders.

---

> Created with ❤️ for personal supplement habit tracking