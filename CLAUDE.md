# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Архитектура

Проект — IoT-эмулятор умной кормушки для кошек, состоит из 5 независимых сервисов:

```
mosquitto/          # MQTT брокер (Eclipse Mosquitto 2)
device_emulator/    # Python + Flask — симулятор + эмулятор устройства
backend/            # Node.js/Express + TypeScript — MQTT → REST API + WebSocket
frontend/           # React + Vite + TypeScript — UI дашборд
telegram_bot/       # Python — Telegram-бот (пульт управления)
```

**Поток данных:** Эмулятор → MQTT → Backend (MQTTBridge) → SQLite (Prisma) → REST/WebSocket → Frontend / Telegram Bot

## Три компонента устройства

### 1. Симулятор (`http://localhost:5000/`)
Фото-реалистичный вид кормушки в стиле Art Deco (CSS 3D + Canvas). OLED-дисплей на canvas, LED-индикаторы, танки корма/воды с уровнями, детектор кота, панель управления со слайдерами.
- Шаблон: `device_emulator/templates/simulator.html`

### 2. Эмулятор (`http://localhost:5000/schematic`)
Интерактивная электрическая схема с двумя уровнями (блок-схема ↔ принципиальная). SVG + CSS-анимации сигналов. Компоненты: ESP32, HX711, SG90, HC-SR501, DHT22, INA219, SSD1306 OLED. Тултипы с характеристиками.
- Шаблон: `device_emulator/templates/schematic.html`

### 3. Пульт — Telegram Bot (`telegram_bot/`)
Полное управление через Telegram: /status, /feed, /schedule, /stats, /events, /settings. Inline-клавиатуры, графики (matplotlib), фоновые уведомления о событиях.
- Точка входа: `telegram_bot/bot.py`
- Конфиг: env `TELEGRAM_BOT_TOKEN`, `BACKEND_URL`, `DEVICE_ID`

## Запуск

### Полный стек (Docker)
```bash
TELEGRAM_BOT_TOKEN=your_token docker-compose up --build
# симулятор:   http://localhost:5000
# эмулятор:    http://localhost:5000/schematic
# frontend:    http://localhost:3000
# backend API: http://localhost:3001
# telegram:    @your_bot
```

### Отдельные сервисы (разработка)
```bash
# Эмулятор устройства
cd device_emulator && python main.py

# Backend
cd backend && npm install && npm run dev
# Первый запуск (создать БД): npm run prisma:push

# Frontend
cd frontend && npm install && npm run dev

# Telegram Bot
cd telegram_bot && pip install -r requirements.txt
TELEGRAM_BOT_TOKEN=xxx BACKEND_URL=http://localhost:3001 python bot.py
```

### Сборка
```bash
cd backend && npm run build    # tsc → dist/
cd frontend && npm run build   # tsc + vite → dist/
```

## Конфигурация

**Эмулятор** — `device_emulator/config.py`:
- `MQTT_HOST/PORT`, `DEVICE_ID` (также читаются из env)
- Параметры симуляции: скорость убывания еды/воды, вероятности событий, тайминги

**Backend** — env vars: `MQTT_HOST`, `MQTT_PORT`, `DATABASE_URL` (путь к SQLite), `PORT` (по умолчанию 3001)

**Frontend** — env vars: `VITE_API_URL`, `VITE_WS_URL`

**Telegram Bot** — env vars: `TELEGRAM_BOT_TOKEN`, `BACKEND_URL` (по умолчанию http://backend:3001), `DEVICE_ID`, `POLL_INTERVAL`

## Структура backend (`backend/src/`)

- `index.ts` — точка входа Express, регистрация роутов и WebSocket
- `mqtt/` — `MQTTBridge`: подписывается на MQTT-топики, парсит телеметрию/события, сохраняет в БД, рассылает через Socket.io
- `routes/` — REST-эндпоинты: devices, telemetry, events, schedules, settings
- `db/index.ts` — синглтон Prisma-клиента
- `websocket/index.ts` — настройка Socket.io
- `types/` — общие TypeScript-интерфейсы

MQTT-топики: `feeder/{deviceId}/telemetry`, `.../events`, `.../commands`, `.../status`

## Структура telegram_bot (`telegram_bot/`)

- `bot.py` — точка входа, регистрация хэндлеров
- `handlers/` — start, status, feed, schedule, stats, events, settings
- `services/api_client.py` — httpx-обёртка над backend REST API
- `services/chart_generator.py` — matplotlib графики
- `services/notifications.py` — фоновый polling событий
- `keyboards/` — InlineKeyboardMarkup билдеры

## Структура frontend (`frontend/src/`)

- `store/feederStore.ts` — Zustand-стор, централизованное состояние устройства
- `api/client.ts` — Axios-инстанс + подключение Socket.io
- `pages/` — Dashboard, Schedule, Statistics, Settings
- `components/` — переиспользуемые UI-компоненты

При загрузке делает REST-запрос, затем получает обновления в реальном времени через Socket.io.

## База данных (Prisma + SQLite)

Модели: `Device`, `Telemetry`, `Event`, `Schedule`, `Settings`

```bash
cd backend
npm run prisma:generate   # пересоздать клиент после изменений схемы
npm run prisma:push       # применить схему к БД (без файлов миграций)
```

Файл БД: `data/feeder.db` (монтируется как Docker volume в продакшене).

## Веб-интерфейс эмулятора

Flask UI на порту 5000:
- `/` — Симулятор (Art Deco, CSS 3D + Canvas OLED) — `simulator.html`
- `/schematic` — Эмулятор (SVG схема электроники) — `schematic.html`
- `/analytics` — Аналитика — `analytics.html`
- `/history` — История — `history.html`
- `/settings` — Настройки — `settings.html`

REST API: `GET /api/status`, `POST /api/feed` (`{"portion": 20}`), `POST /api/sensors/food`, `POST /api/sensors/water`, `POST /api/sensors/temperature`, `POST /api/cat/toggle`, `POST /api/door/toggle`, `POST /api/schedule`, `POST /api/motor/error`, `POST /api/motor/reset`, `POST /api/scale/tare`

## Аппаратная основа (эмулируемые компоненты)

| Компонент | Назначение | Интерфейс |
|-----------|-----------|-----------|
| ESP32-WROOM-32 | MCU + WiFi | — |
| HX711 + тензодатчик | Весы миски | GPIO4 (DOUT), GPIO5 (SCK) |
| SG90 серво | Дозатор корма | GPIO18 (PWM) |
| HC-SR501 PIR | Детектор кота | GPIO19 |
| DHT22 | Температура/влажность | GPIO23 |
| INA219 | Мониторинг батареи | I2C (0x40) |
| SSD1306 OLED 128×64 | Дисплей | I2C (0x3C) |
| AMS1117-3.3 | LDO стабилизатор | 5V→3.3V |
