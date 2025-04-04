# 💊 Telegram Supplement Routine Bot

개인 영양제 루틴 관리를 위한 Telegram 봇입니다. 매일 아침/저녁/취침 전 복용해야 하는 영양제를 체크리스트 형태로 알림 받고, 완료 여부를 기록합니다.

---

## 🧠 주요 기능

### ✅ 루틴 알림 기능
- 아침, 저녁, 밤 시간에 맞춰 복용해야 할 루틴을 알림 형태로 발송
- 버튼을 눌러 복용 완료 체크 가능
- 하루 3회 모두 완료 시 `Day +1` 진행

### ⏰ 시간별 알림 시간 설정
- `/settime [morning|evening|night] [HH:MM]` 명령어로 한국시간 기준 변경 가능
- `/showtimes` 명령어로 현재 알림 시간 확인

### 🔁 루틴 미완료 리마인더
- 체크하지 않은 루틴이 50분 이상 지난 경우 리마인더 알림 자동 발송

### 💬 매일 아침 자동 인삿말
- 매일 아침 9시에 현재 루틴 현황을 자동으로 알려줍니다.

### 🛠 복구 기능 (`/복구` 또는 `/restore`)
- 하루 내 또는 전날 깜빡 잊은 루틴 복용을 수동으로 완료할 수 있도록 안내
- 완료되지 않은 시간대만 표시됨

---

## 🚀 실행 방법

```bash
git clone https://github.com/yourname/supplement-bot.git
cd supplement-bot
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=your_token
export TELEGRAM_USER_ID=your_id
python telegram_supplement_bot_v2.py
```

---

## ☁️ Fly.io 배포
- `fly.toml`, `Dockerfile` 제공
- GitHub Actions 자동 ping용 `.github/workflows/keepalive.yml` 포함

---

## 📁 파일 구조

```
.
├── telegram_supplement_bot_v2.py   # 봇 메인 파일
├── keepalive_server.py             # Fly.io 슬립 방지용 ping 서버
├── .github/workflows/keepalive.yml # GitHub Actions로 자동 ping
├── supplement_state.json           # 루틴 상태 저장
├── supplement_config.json          # 루틴 구성 및 시간 저장
├── README.md                       # 이 파일
```

---

## 🧪 테스트 명령어
- `/testalarm` : 수동 알림 테스트용

---

## 🧑‍💻 만든 이유
루틴을 깜빡하거나 다시 체크하지 못하는 일이 잦아, 매일 반복되는 복용 루틴을 **버튼 하나로 간단하게 관리**하고 싶었습니다.