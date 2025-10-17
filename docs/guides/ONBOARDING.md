# 🚀 Онбординг разработчика

> Пошаговое руководство для быстрого старта работы с проектом (30 минут)

---

## 📖 Шаг 1: Обзорная документация (5 минут)

Прочитай в следующем порядке:

1. **README.md** (корень проекта) - быстрый старт, команды, структура
2. **Этот файл** - пошаговый онбординг
3. **ARCHITECTURE.md** - архитектура системы (после настройки)

---

## 🛠️ Шаг 2: Настройка окружения (10 минут)

### 2.1 Требования

- **Python 3.11+** (проверь: `python --version`)
- **uv** - менеджер зависимостей ([установка](https://github.com/astral-sh/uv))
- **Git** - для клонирования репозитория

### 2.2 Установка

```bash
# 1. Клонирование (если еще не сделано)
git clone <repository-url>
cd systech-aidd-test

# 2. Установка зависимостей
make install
# или: uv sync --all-extras

# 3. Создание конфигурации
cp .env.example .env
```

### 2.3 Настройка .env

Отредактируй `.env` файл:

```ini
# Обязательные параметры
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENROUTER_API_KEY=sk-or-v1-your_key_here

# Опциональные (есть defaults)
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
BOT_NAME=SysTech AI Assistant
```

**Где получить токены:**
- Telegram: [@BotFather](https://t.me/botfather) в Telegram
- OpenRouter: [openrouter.ai](https://openrouter.ai/)

---

## ✅ Шаг 3: Проверка установки (5 минут)

### 3.1 Smoke test - запуск тестов

```bash
make test
```

**Ожидаемый результат:**
```
49 passed, 100% coverage ✅
```

### 3.2 Smoke test - проверка качества

```bash
make ci
```

**Ожидаемый результат:**
```
✅ lint passed
✅ format passed
✅ type-check passed
✅ test passed
✅ All CI checks passed!
```

### 3.3 Запуск бота

```bash
make run
```

**Ожидаемый результат в консоли:**
```
Starting systech-aidd-test application
Loaded system prompt from prompts/system_prompt.txt
LLM client initialized successfully
Starting bot in polling mode...
```

**Проверь работу:**
1. Найди своего бота в Telegram
2. Отправь `/start` - должно прийти приветствие
3. Отправь `/help` - должен прийти список команд
4. Отправь любое сообщение - должен прийти ответ от LLM
5. Ctrl+C для остановки

---

## 📚 Шаг 4: Изучение архитектуры (10 минут)

Теперь изучи:

1. **docs/guides/ARCHITECTURE.md** - архитектура компонентов
2. **docs/guides/CODEBASE_TOUR.md** - тур по коду с примерами
3. **docs/VISION.md** - полное техническое видение (reference)

---

## 🎯 Контрольный чеклист

- [ ] Python 3.11+ установлен
- [ ] uv установлен и работает
- [ ] Зависимости установлены (`make install`)
- [ ] Файл `.env` настроен с токенами
- [ ] `make test` проходит (49 тестов, 100% coverage)
- [ ] `make ci` проходит (все проверки зеленые)
- [ ] Бот запускается (`make run`)
- [ ] Бот отвечает в Telegram на команды
- [ ] Прочитана документация (ARCHITECTURE.md, CODEBASE_TOUR.md)

---

## 💡 Быстрая справка команд

### Разработка

```bash
make run          # Запуск бота
make test         # Запуск тестов
make lint         # Проверка кода
make format       # Форматирование
make type-check   # Проверка типов
make ci           # Все проверки (обязательно перед коммитом!)
```

### Навигация по коду

```
src/
├── main.py              # Точка входа ⭐
├── config.py            # Конфигурация
├── bot.py               # Telegram обработчики
├── llm_client.py        # OpenRouter интеграция
├── context_storage.py   # Хранилище контекста
├── messages.py          # Текстовые константы
└── logger.py            # Логирование
```

---

## 🆘 Частые проблемы

### Бот не отвечает

- Проверь токены в `.env`
- Проверь логи в `logs/bot.log`
- Убедись что бот запущен (`make run`)

### Тесты падают

```bash
make clean    # Очистить кэш
make install  # Переустановить зависимости
make test     # Запустить снова
```

### Ошибки линтера

```bash
make format   # Автоформатирование
make lint     # Проверка
```

Подробнее: **docs/guides/TROUBLESHOOTING.md** (если создан)

---

## 🎓 Следующие шаги

После успешного онбординга:

1. **Изучи процессы разработки:** docs/guides/DEVELOPMENT.md
2. **Изучи тестирование:** docs/guides/TESTING.md
3. **Выбери первую задачу:** docs/TASKLIST.md (история разработки)
4. **Попробуй изменить роль бота:** отредактируй `prompts/system_prompt.txt` и перезапусти

---

## 📞 Где искать помощь

1. **Документация проекта:**
   - `docs/guides/` - практические гайды
   - `docs/VISION.md` - техническое видение
   - `README.md` - быстрый старт

2. **Код:**
   - Все модули имеют docstrings
   - Тесты показывают примеры использования

3. **Логи:**
   - `logs/bot.log` - полные логи работы бота
   - Консоль - real-time события

---

**Готов к работе! Удачи в разработке! 🚀**


