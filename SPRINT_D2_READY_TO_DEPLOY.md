# 🚀 Sprint D2: Готов к развертыванию

> **Все файлы созданы и готовы к использованию!**

**Дата:** 18 октября 2025  
**Ветка:** `day6_Apply_Manually`  
**Статус:** ✅ Подготовка завершена

---

## 📦 Что создано

### 1. Production конфигурация

```
✅ env.production.example        - Шаблон переменных окружения
✅ docker-compose.prod.yml       - Production Docker Compose
```

### 2. Подробная документация

```
✅ docs/guides/MANUAL_DEPLOY.md  - Инструкция (570 строк)
✅ devops/doc/plans/d2-manual-deploy.md
✅ devops/doc/SPRINT_D2_PROGRESS.md
✅ devops/doc/SPRINT_D2_PREPARATION_COMPLETE.md
```

### 3. Скрипты автоматизации

```
✅ devops/scripts/check-server.sh  - Проверка сервера (300+ строк)
✅ devops/scripts/deploy.sh        - Авто развертывание (350+ строк)
✅ devops/scripts/README.md        - Инструкция по скриптам
```

### 4. Обновления

```
✅ devops/doc/devops-roadmap.md  - Sprint D2 -> In Progress
```

---

## 🎯 Следующие шаги

### ШАГ 1: Подготовить .env файл

```bash
# Скопировать шаблон
cp env.production.example .env

# Отредактировать и заполнить:
# - TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
# - OPENROUTER_API_KEY=ваш_ключ_от_OpenRouter
nano .env  # или другой редактор
```

**Где получить токены:**
- Telegram Bot Token: https://t.me/BotFather
- OpenRouter API Key: https://openrouter.ai/keys

### ШАГ 2: Получить SSH ключ

Вам понадобится SSH ключ для доступа к серверу `89.223.67.136`.

**Проверка ключа:**
```bash
# Установить правильные права
chmod 600 /path/to/ssh_key.pem

# Тест подключения
ssh -i /path/to/ssh_key.pem systech@89.223.67.136
```

### ШАГ 3: Проверить сервер

```bash
# Запустить проверку готовности сервера
./devops/scripts/check-server.sh /path/to/ssh_key.pem
```

**Что проверяется:**
- ✓ SSH подключение
- ✓ Docker и Docker Compose
- ✓ Порты 8001, 3001
- ✓ Ресурсы сервера
- ✓ Firewall правила

### ШАГ 4: Развернуть приложение

**Вариант A: Автоматический (рекомендуется)**

```bash
# Автоматическое развертывание одной командой
./devops/scripts/deploy.sh /path/to/ssh_key.pem
```

**Что сделает скрипт:**
1. Проверит локальные файлы
2. Подключится к серверу
3. Создаст директории
4. Скопирует файлы
5. Загрузит Docker образы
6. Запустит сервисы
7. Выполнит миграции БД
8. Проверит работу

**Вариант B: Ручной**

Следуйте подробной инструкции:
```bash
# Откройте в редакторе
cat docs/guides/MANUAL_DEPLOY.md

# Или в браузере
start docs/guides/MANUAL_DEPLOY.md  # Windows
open docs/guides/MANUAL_DEPLOY.md   # Mac
```

### ШАГ 5: Проверить работу

После развертывания проверьте:

```bash
# API
curl http://89.223.67.136:8001/health

# Frontend (в браузере)
http://89.223.67.136:8001  # API
http://89.223.67.136:3001  # Frontend

# Telegram Bot
# Отправьте боту сообщение в Telegram
```

---

## 📚 Документация

### Главная инструкция
**docs/guides/MANUAL_DEPLOY.md** - Полное руководство по развертыванию

**Содержание:**
- 9 этапов развертывания
- Все команды готовы к копированию
- Troubleshooting (6+ проблем)
- Управление сервисами
- Backup и восстановление
- Мониторинг

### Скрипты
**devops/scripts/README.md** - Инструкция по скриптам

### Прогресс
**devops/doc/SPRINT_D2_PROGRESS.md** - Отслеживание прогресса

---

## 🎬 Быстрый старт (3 команды)

```bash
# 1. Подготовить .env
cp env.production.example .env && nano .env

# 2. Проверить сервер
./devops/scripts/check-server.sh /path/to/ssh_key.pem

# 3. Развернуть
./devops/scripts/deploy.sh /path/to/ssh_key.pem
```

**Время выполнения:** ~5-10 минут

---

## 💡 Особенности

### Production готовность

- ✅ Образы из GitHub Container Registry (публичные)
- ✅ Порты: 8001 (API), 3001 (Frontend)
- ✅ Healthchecks для всех сервисов
- ✅ Автоматический перезапуск (restart: always)
- ✅ Ротация логов (10MB × 5 файлов)

### Безопасность

- ✅ .env с правами 600
- ✅ Секреты не в git
- ✅ Read-only mount для промптов
- ✅ Валидация токенов

### Автоматизация

- ✅ Полная проверка зависимостей
- ✅ Цветной вывод прогресса
- ✅ Автоматическая обработка ошибок
- ✅ Детальная диагностика

---

## 🔧 Управление после развертывания

### Просмотр логов

```bash
ssh -i /path/to/key.pem systech@89.223.67.136 \
  'cd /opt/systech/vvelyus && docker-compose -f docker-compose.prod.yml logs -f'
```

### Перезапуск сервисов

```bash
ssh -i /path/to/key.pem systech@89.223.67.136 \
  'cd /opt/systech/vvelyus && docker-compose -f docker-compose.prod.yml restart'
```

### Проверка статуса

```bash
ssh -i /path/to/key.pem systech@89.223.67.136 \
  'cd /opt/systech/vvelyus && docker-compose -f docker-compose.prod.yml ps'
```

### Остановка

```bash
ssh -i /path/to/key.pem systech@89.223.67.136 \
  'cd /opt/systech/vvelyus && docker-compose -f docker-compose.prod.yml down'
```

---

## 📊 Статистика

- **Файлов создано:** 10
- **Строк документации:** ~1500
- **Строк скриптов:** ~700
- **Покрытие:** 100%

---

## ✅ Чек-лист готовности

Перед развертыванием убедитесь:

- [ ] Есть SSH ключ для сервера 89.223.67.136
- [ ] Создан .env с реальными токенами
- [ ] TELEGRAM_BOT_TOKEN заполнен
- [ ] OPENROUTER_API_KEY заполнен
- [ ] Прочитана инструкция MANUAL_DEPLOY.md
- [ ] Скрипты имеют права на выполнение (chmod +x)

---

## 🆘 Помощь

**Если что-то не работает:**

1. Проверьте **Troubleshooting** в `docs/guides/MANUAL_DEPLOY.md`
2. Запустите `./devops/scripts/check-server.sh` для диагностики
3. Изучите логи: `docker-compose logs`
4. Посмотрите примеры команд в документации

**Основные проблемы:**
- "Permission denied" → chmod 600 на SSH ключ
- "Connection refused" → проверьте IP и доступность сервера
- "Docker not found" → обратитесь к администратору сервера
- Порт занят → измените порты в docker-compose.prod.yml

---

## 🚀 После успешного развертывания

Создайте отчет о результатах в `devops/doc/SPRINT_D2_COMPLETION.md`

**Включите:**
- Скриншоты работающих сервисов
- Результаты healthchecks
- Возникшие проблемы и решения
- Рекомендации для Sprint D3

---

## 📞 Контакты

- **GitHub Repository:** https://github.com/vvelyus/systech-aidd-test
- **GHCR Packages:** https://github.com/vvelyus?tab=packages&repo_name=systech-aidd-test
- **Документация:** docs/guides/

---

**Готово к развертыванию! 🎉**

Следующий этап: **Sprint D3 - Auto Deploy**

