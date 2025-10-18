# Быстрое исправление ошибки "Module not found" во фронтенде

## Проблема
```
Module not found: Can't resolve '@/lib/api'
GET http://89.223.67.136:3001/dashboard 500 (Internal Server Error)
```

## Решение в 3 шага

### ШАГ 1: Локально (на Windows)

```powershell
# В директории проекта
.\fix-frontend.ps1
```

Или вручную:
```powershell
git add devops/Dockerfile.frontend frontend/web/next.config.ts
git commit -m "fix: Исправление Dockerfile фронтенда для production"
git push origin main
```

### ШАГ 2: На сервере (через SSH)

```bash
cd /root/systech-aidd-test
bash fix-frontend.sh
```

Или вручную:
```bash
cd /root/systech-aidd-test
git pull origin main
docker-compose -f docker-compose.prod.yml stop frontend
docker-compose -f docker-compose.prod-rebuild.yml build --no-cache frontend
docker-compose -f docker-compose.prod-rebuild.yml up -d frontend
```

### ШАГ 3: Проверка

Откройте в браузере:
- http://89.223.67.136:3001/dashboard
- http://89.223.67.136:3001/chat

✅ **Не должно быть ошибок "Module not found"**
✅ **Страница должна загрузиться**
✅ **Dashboard должен показывать данные**

## Что исправлено?

1. ✅ **Dockerfile**: Multi-stage build для production
2. ✅ **Next.js config**: Standalone output для Docker
3. ✅ **Path aliases**: Правильная резолвция `@/lib/*`

## Время выполнения
- Локально: 1 минута
- На сервере: 3-5 минут (сборка образа)
- **Всего: ~5-6 минут**

## Логи (если что-то не работает)

```bash
# Посмотреть логи фронтенда
docker-compose -f docker-compose.prod-rebuild.yml logs -f frontend

# Проверить статус
docker ps | grep frontend

# Проверить доступность
curl http://localhost:3000
```

## Откат (если нужно)

```bash
# Вернуться к предыдущей версии
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

---

**📖 Подробная документация**: См. `FRONTEND_MODULE_FIX.md`
