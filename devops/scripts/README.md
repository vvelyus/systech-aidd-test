# Deployment Scripts

Вспомогательные скрипты для развертывания SysTech AI Assistant на production сервере.

## Скрипты

### check-server.sh

Проверка готовности сервера к развертыванию.

**Что проверяет:**
- SSH подключение
- Версии Docker и Docker Compose
- Права пользователя на Docker
- Доступность портов (8001, 3001)
- Существование рабочих директорий
- Доступ к GitHub Container Registry
- Ресурсы сервера (диск, память)
- Firewall правила

**Использование:**

```bash
# Из корня проекта
./devops/scripts/check-server.sh /path/to/ssh_key.pem

# Пример
./devops/scripts/check-server.sh ~/.ssh/systech-key.pem
```

**Вывод:**
- ✓ Зеленый - проверка пройдена
- ✗ Красный - критическая ошибка
- ! Желтый - предупреждение

### deploy.sh

Автоматическое развертывание на сервере.

**Что делает:**
1. Проверяет локальные файлы (.env, docker-compose.prod.yml)
2. Проверяет доступ к серверу
3. Создает рабочие директории на сервере
4. Копирует файлы на сервер
5. Загружает Docker образы из GHCR
6. Запускает сервисы
7. Выполняет миграции БД
8. Проверяет работоспособность

**Использование:**

```bash
# Убедитесь, что .env файл подготовлен!
./devops/scripts/deploy.sh /path/to/ssh_key.pem

# Пример
./devops/scripts/deploy.sh ~/.ssh/systech-key.pem
```

**Предварительные требования:**
- Файл `.env` с реальными токенами (скопировать из `env.production.example`)
- SSH ключ для доступа к серверу
- Файлы: `docker-compose.prod.yml`, `prompts/system_prompt.txt`

## Подготовка к использованию

### 1. Подготовка .env файла

```bash
# Скопируйте шаблон
cp env.production.example .env

# Отредактируйте .env и заполните:
# - TELEGRAM_BOT_TOKEN
# - OPENROUTER_API_KEY
nano .env
```

### 2. Проверка SSH ключа

```bash
# Проверка прав на ключ
chmod 600 /path/to/ssh_key.pem

# Тест подключения
ssh -i /path/to/ssh_key.pem systech@89.223.67.136
```

### 3. Запуск проверки

```bash
# Проверка готовности сервера
./devops/scripts/check-server.sh /path/to/ssh_key.pem
```

### 4. Развертывание

```bash
# Автоматическое развертывание
./devops/scripts/deploy.sh /path/to/ssh_key.pem

# Или следуйте ручной инструкции
# docs/guides/MANUAL_DEPLOY.md
```

## Параметры сервера

- **IP:** 89.223.67.136
- **Пользователь:** systech
- **Рабочая директория:** /opt/systech/vvelyus
- **Порты:** 8001 (API), 3001 (Frontend)

## Troubleshooting

### "Permission denied" при SSH

```bash
# Проверьте права на ключ
chmod 600 /path/to/ssh_key.pem

# Проверьте пользователя и IP
ssh -v -i /path/to/ssh_key.pem systech@89.223.67.136
```

### Скрипты не запускаются

```bash
# Для Linux/Mac - установите права на выполнение
chmod +x devops/scripts/*.sh

# Для Windows - используйте Git Bash или WSL
```

### Docker не доступен на сервере

Обратитесь к администратору сервера для установки Docker:
```bash
# На сервере
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

## Полезные команды после развертывания

```bash
# Просмотр логов
ssh -i /path/to/key.pem systech@89.223.67.136 \
  'cd /opt/systech/vvelyus && docker-compose -f docker-compose.prod.yml logs -f'

# Перезапуск сервисов
ssh -i /path/to/key.pem systech@89.223.67.136 \
  'cd /opt/systech/vvelyus && docker-compose -f docker-compose.prod.yml restart'

# Проверка статуса
ssh -i /path/to/key.pem systech@89.223.67.136 \
  'cd /opt/systech/vvelyus && docker-compose -f docker-compose.prod.yml ps'
```

## Дополнительная информация

- **Полная инструкция:** [docs/guides/MANUAL_DEPLOY.md](../../docs/guides/MANUAL_DEPLOY.md)
- **План спринта:** [devops/doc/plans/d2-manual-deploy.md](../doc/plans/d2-manual-deploy.md)
- **Прогресс:** [devops/doc/SPRINT_D2_PROGRESS.md](../doc/SPRINT_D2_PROGRESS.md)

---

**Sprint D2** - Manual Deploy  
**Дата создания:** 18 октября 2025

