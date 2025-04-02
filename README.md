# 🧠 Telegram Supplement Routine Bot

이 텔레그램 봇은 개인의 영양제 복용 루틴을 체크리스트로 제공하고, 설정된 시간에 맞춰 자동으로 알림을 보내주는 봇입니다.
매일 아침/저녁/취침 전 루틴을 관리하고, 일정 시간 내 미복용 시 리마인더도 전송합니다.

---

## ✅ 주요 기능

- `/start`: 루틴 봇을 시작하고 상태 메시지를 고정합니다.
- `/settime [morning|evening|night] HH:MM`: 각 루틴의 알림 시간을 설정합니다 (한국시간 기준).
- `/showtimes`: 현재 설정된 알림 시간을 보여줍니다.
- 버튼을 통해 복용 완료 체크 가능 (아침 / 저녁 / 취침 전)
- 하루 3회 복용 완료 시 자동으로 Day +1 진행
- 복용 미체크 시 리마인더 자동 전송 (기본 50분 후)
- 서버 재시작 시에도 스케줄 자동 복원

---

## 🛠️ 환경 변수 (Fly.io secrets)

- `TELEGRAM_BOT_TOKEN`: 텔레그램 봇 API 토큰
- `TELEGRAM_USER_ID`: 메시지를 받을 사용자 ID (봇과 대화 시 확인 가능)

```bash
fly secrets set TELEGRAM_BOT_TOKEN=your_token_here TELEGRAM_USER_ID=123456789
```

---

## 🧪 테스트 명령어

- `/testalarm`: 스케줄과 무관하게 즉시 알림 메시지를 수동 전송합니다.

---

## 🕒 스케줄

- 매일 설정된 시간(KST)을 UTC로 변환하여 스케줄 등록됩니다.
- `schedule` + `asyncio.run_coroutine_threadsafe()` 방식으로 구현
- 루틴 시간이 지나도 복용 버튼을 누르지 않으면 리마인더가 발송됩니다.

---

## 💡 향후 추가 가능 기능

- 루틴 복용 내역 PDF 요약본 전송
- `/reset` 명령어로 Day 초기화
- 여러 사용자 지원 및 관리자 모드