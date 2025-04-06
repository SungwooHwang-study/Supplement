# 🧠 Telegram Supplement Routine Bot

Telegram을 통해 **영양제 복용 루틴**을 관리할 수 있는 봇입니다. 
아침/저녁/취침 루틴을 체크하며, 복용 완료 체크, 리마인더, 루틴 추가/삭제 등을 지원합니다.

## 🛠️ 기능 요약

| 명령어 | 설명 |
|--------|------|
| `/start` | 봇을 시작하고 현재 상태를 요약해줍니다. |
| `/settime [시간대] [HH:MM]` | 루틴 알림 시간을 설정합니다 (예: `/settime morning 09:30`) |
| `/showtimes` | 현재 알림 시간을 KST 기준으로 보여줍니다. |
| `/testalarm` | 테스트용 아침 루틴 알림을 즉시 전송합니다. |
| `/remind [시간대]` | 원하는 시간대의 루틴 알림을 즉시 다시 보냅니다. |
| `/forcecomplete [시간대]` | 루틴을 수동으로 완료 처리합니다. |
| `/add` | 루틴에 영양제를 **대화형으로 추가**합니다. |
| `/remove` | 루틴에 등록된 영양제를 **선택하여 삭제**합니다. |
| `/cancel` | `/add` 또는 `/remove` 실행 도중 중단할 수 있습니다. |

## 📦 기본 루틴 구조

```json
{
  "morning": ["투퍼데이", "엘카르니틴", "비타민 C (공복)", ...],
  "evening": ["오메가3", "쏜 SAT", "비타민 C (저녁식후)", ...],
  "night": ["마그네슘", "글리신 + 테아닌", "비타민 C (취침전)"]
}
```

## ⏰ 알림 스케줄

- 아침 알림: 기본 09:00 KST
- 저녁 알림: 기본 20:30 KST
- 취침 알림: 기본 23:30 KST
- 매일 아침 08:00 KST: "좋은 아침입니다!" 메시지 전송

## 💡 알림 예시

```
🕘 [Day 3] MORNING 루틴입니다!

☑️ 투퍼데이 (1정)
☑️ 엘카르니틴
☑️ 비타민 C (공복)
...
✅ 복용 완료 버튼
```

## 💾 상태 자동 저장

- `supplement_state.json`: 복용 여부 및 날짜
- `supplement_config.json`: 루틴 구성 및 시간 정보

## 🧪 개발 및 테스트

- Fly.io에서 배포 및 작동
- Fly Secrets 사용:
  ```bash
  fly secrets set TELEGRAM_BOT_TOKEN=your_bot_token TELEGRAM_USER_ID=your_user_id
  ```
