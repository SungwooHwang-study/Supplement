
# 🧠 Telegram Supplement Routine Bot

AI 기반 건강 루틴 관리 봇  
매일 정해진 시간에 영양제 복용 체크리스트를 텔레그램으로 알려주고,  
사용자가 버튼 클릭으로 복용을 기록하면 자동으로 Day를 관리해주는 건강 루틴 전용 봇입니다.

---

## 📦 주요 기능

- ✅ 시간별 복용 루틴 자동 알림 (아침 / 저녁 / 취침 전)
- ✅ "복용 완료" 버튼으로 체크
- ✅ 하루 3번 완료 시 Day +1
- 📌 텔레그램 핀 메시지로 현재 진행 상태 표시 (아이폰 위젯 대응)
- 🔔 복용 누락 시 자동 리마인더 전송
- 🔄 루틴 누락 시 Day 유지 (자동 보정)
- ⏰ `/settime` 명령어로 시간 변경 가능

---

## 🚀 설치 및 실행

### 1. GitHub 클론

```bash
git clone https://github.com/your-username/supplement-routine-bot.git
cd supplement-routine-bot
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env` 또는 Railway 대시보드에서 아래 환경변수를 추가하세요:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

---

## 🧑‍💻 실행

```bash
python telegram_supplement_bot_v2.py
```

---

## ☁️ Railway 배포 방법

1. Railway 계정 생성 및 로그인 [https://railway.app](https://railway.app)
2. **New Project > Deploy from GitHub Repo**
3. `TELEGRAM_BOT_TOKEN` 환경 변수 설정
4. 자동 빌드 및 실행 완료 🎉

---

## 🧾 명령어 요약

| 명령어 | 기능 |
|--------|------|
| `/start` | 루틴 시작 및 사용자 등록 |
| `/settime [시간대] [HH:MM]` | 루틴 알림 시간 변경 <br>예: `/settime morning 07:45` |

---

## 📱 iPhone 위젯 활용법

- 텔레그램 앱에서 대화방 핀 고정 시  
  ➜ 현재 루틴 진행 상황이 위젯에 미리보기 형태로 표시됨  
  ➜ 아이폰 홈화면에서 직접 루틴 상태 확인 가능

---

## 📄 라이선스

MIT License. 자유롭게 사용하고 커스터마이징하세요.
