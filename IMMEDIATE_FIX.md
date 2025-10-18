# НЕМЕДЛЕННОЕ ИСПРАВЛЕНИЕ ФРОНТЕНДА

## Проблема
GitHub Actions постоянно падает с разными ошибками при сборке frontend образа.
После 4 попыток исправления - проблемы с Docker context и .dockerignore продолжаются.

## Решение
**Пересобрать образ локально на сервере** - это обходит все проблемы GitHub Actions.

## Команды для выполнения

### На сервере (через SSH):

```bash
# Подключиться к серверу
ssh root@89.223.67.136

# Перейти в директорию проекта
cd /root/systech-aidd-test

# Обновить код
git pull origin main

# Остановить текущий фронтенд
docker-compose -f docker-compose.prod.yml stop frontend
docker-compose -f docker-compose.prod.yml rm -f frontend

# ПЕРЕСОБРАТЬ фронтенд локально (это займет 3-5 минут)
docker-compose -f docker-compose.prod-rebuild.yml build --no-cache frontend

# Запустить новый контейнер
docker-compose -f docker-compose.prod-rebuild.yml up -d frontend

# Проверить логи
docker-compose -f docker-compose.prod-rebuild.yml logs -f frontend
```

### Или одной командой:

```bash
ssh root@89.223.67.136 "cd /root/systech-aidd-test && git pull && docker-compose -f docker-compose.prod.yml stop frontend && docker-compose -f docker-compose.prod-rebuild.yml build --no-cache frontend && docker-compose -f docker-compose.prod-rebuild.yml up -d frontend"
```

## Почему это сработает?

1. ✅ **Локальная сборка** не использует GitHub Actions
2. ✅ **Нет проблем с context** - Docker видит все файлы на диске
3. ✅ **Нет проблем с .dockerignore** - работает как ожидалось
4. ✅ **Быстро** - ~3-5 минут вместо отладки CI/CD
5. ✅ **Надежно** - уже проверенный метод

## После успешной сборки

### Проверить статус:
```bash
docker ps | grep frontend
docker logs systech-aidd-frontend-prod --tail=50
```

### Проверить в браузере:
- http://89.223.67.136:3001/dashboard
- http://89.223.67.136:3001/chat
- F12 → Console (не должно быть ошибок "Module not found")

## Время выполнения
- **Всего: 3-5 минут**
- Обновление кода: 10 секунд
- Остановка контейнера: 10 секунд  
- Сборка образа: 2-4 минуты
- Запуск контейнера: 30 секунд

## GitHub Actions - исправить позже

После того как фронтенд заработает, можно спокойно разобраться с GitHub Actions:
1. Изучить точные логи ошибки
2. Возможно, нужно использовать другой базовый образ
3. Или изменить стратегию сборки в CI/CD

Но сейчас главное - **запустить фронтенд в работу** как можно быстрее.

---

**СТАТУС**: Готово к выполнению  
**РИСК**: Минимальный  
**ВРЕМЯ**: 3-5 минут  
**РЕЗУЛЬТАТ**: Рабочий фронтенд без ошибок "Module not found"

