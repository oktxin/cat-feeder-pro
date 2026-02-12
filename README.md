# 🐱 CatFeed Pro - Smart Cat Feeder Emulator

Современный веб-интерфейс для эмулятора умной кормушки для кошек с минималистичным Apple-style дизайном.

![CatFeed Pro](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Flask](https://img.shields.io/badge/flask-3.0.0-red)

## ✨ Возможности

- 🖥️ **4 страницы веб-интерфейса**:
  - Dashboard - 3D модель кормушки (Three.js) с управлением
  - Analytics - графики потребления и статистика
  - History - история кормлений с таблицей
  - Settings - настройки устройства и калибровка

- 🎨 **Современный дизайн**:
  - Минималистичный Apple-style интерфейс
  - Адаптивная верстка
  - Плавные анимации и переходы
  - Темная/светлая тема через CSS переменные

- ⚙️ **Функциональность**:
  - 3D визуализация кормушки с OrbitControls
  - Управление кормлением (10g, 20g, 50g порции)
  - Мониторинг датчиков (температура, еда, вода)
  - Расписание автоматического кормления
  - REST API для всех операций
  - Auto-update каждые 2 секунды

- 🌐 **IoT возможности**:
  - MQTT телеметрия (опционально)
  - Работает с MQTT брокером или без него
  - Эмуляция реального IoT устройства

## 📋 Требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)

## 🚀 Быстрый старт

### 1. Клонируйте репозиторий

```bash
git clone <your-repo-url>
cd smart-cat-feeder
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

### 3. Запустите эмулятор

```bash
cd device_emulator
python main.py
```

### 4. Откройте в браузере

```
http://localhost:5000
```

## 📁 Структура проекта

```
smart-cat-feeder/
├── device_emulator/
│   ├── templates/              # HTML шаблоны
│   │   ├── emulator_new.html   # Главная страница (Dashboard)
│   │   ├── analytics.html      # Страница аналитики
│   │   ├── history.html        # История кормлений
│   │   └── settings.html       # Настройки устройства
│   ├── static/
│   │   └── models/
│   │       └── scene.gltf      # 3D модель кормушки
│   ├── main.py                 # Точка входа
│   ├── web_interface.py        # Flask веб-сервер
│   ├── feeder.py               # Логика кормушки
│   ├── mqtt_client.py          # MQTT клиент
│   ├── sensors.py              # Эмуляция датчиков
│   └── config.py               # Конфигурация
├── requirements.txt            # Python зависимости
└── README.md                   # Документация
```

## 🌐 Доступные страницы

| Страница | URL | Описание |
|----------|-----|----------|
| Dashboard | `http://localhost:5000/` | Главная с 3D моделью и управлением |
| Analytics | `http://localhost:5000/analytics` | Графики потребления и статистика |
| History | `http://localhost:5000/history` | Таблица истории кормлений |
| Settings | `http://localhost:5000/settings` | Настройки и диагностика |

## 🔌 API Endpoints

### GET `/api/status`
Получить текущее состояние устройства

**Ответ:**
```json
{
  "device_id": "feeder_001",
  "food_level": 75,
  "water_level": 60,
  "temperature": 22.3,
  "battery_level": 88,
  "cat_detected": false,
  "motor_status": "idle",
  "door_open": false,
  "wifi_signal": -66,
  "firmware_version": "1.2.4"
}
```

### POST `/api/feed`
Покормить сейчас

**Запрос:**
```json
{
  "portion": 20
}
```

### POST `/api/sensors/food`
Установить уровень еды

**Запрос:**
```json
{
  "level": 50
}
```

### POST `/api/sensors/water`
Установить уровень воды

### POST `/api/schedule`
Обновить расписание кормлений

**Запрос:**
```json
{
  "times": [
    {"time": "07:00", "portion": 20},
    {"time": "12:30", "portion": 10},
    {"time": "20:00", "portion": 40}
  ]
}
```

### POST `/api/scale/tare`
Калибровка весов

## ⚙️ Конфигурация

Отредактируйте `device_emulator/config.py`:

```python
# Device settings
DEVICE_ID = "feeder_001"

# MQTT Broker (опционально)
MQTT_HOST = "localhost"
MQTT_PORT = 1883

# Intervals
TELEMETRY_INTERVAL = 30  # секунды
EVENT_CHECK_INTERVAL = 5  # секунды
```

## 🐛 Решение проблем

### MQTT Warning
Если видите:
```
WARNING - Failed to connect to MQTT broker. Continuing without MQTT telemetry.
```

Это **нормально**! Эмулятор работает полностью без MQTT. Если хотите MQTT:

1. Установите Mosquitto: https://mosquitto.org/download/
2. Запустите брокер: `mosquitto`

### Порт занят
Если порт 5000 занят, измените в `main.py`:
```python
web_thread = threading.Thread(
    target=run_web_interface,
    kwargs={'port': 8080},  # Измените порт
    daemon=True
)
```

## 🎨 Технологии

- **Backend**: Python, Flask, AsyncIO
- **Frontend**: HTML5, CSS3, JavaScript (ES6)
- **3D**: Three.js, OrbitControls, GLTFLoader
- **IoT**: MQTT (Paho MQTT)
- **Design**: Apple-style минимализм

## 📝 Лицензия

MIT License

**Приятного использования CatFeed Pro!** 🐱✨
