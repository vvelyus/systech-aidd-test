# Admin Mode Timeout Fix - Deployment Instructions

## Overview

This deployment fixes the admin mode timeout issues that prevented complex statistical queries from completing.

## Files Modified

### Backend (Python)
```
src/api/main.py                 # ChatService timeout: 60s→90s, text2sql_timeout: 15s→30s
src/api/chat_service.py         # Admin mode timeouts: Text2SQL 30s, SQL exec 40s, LLM 90s
src/text2sql.py                 # SQL generation timeout: 5s→15s
```

### Frontend (TypeScript/React)
```
frontend/web/src/lib/api.ts    # Added timeout configuration and AbortController
```

## Pre-Deployment Checklist

- [ ] Code review completed
- [ ] All linter checks pass
- [ ] Tests run successfully
- [ ] Backup of current version created
- [ ] Staging environment available
- [ ] Monitoring and logging ready

## Deployment Steps

### 1. Backend Deployment

```bash
# Navigate to project root
cd C:\_dev\systech-aidd\systech-aidd-test

# Stop running services
# (Using docker-compose or appropriate method)

# Copy modified files
cp src/api/main.py /backup/main.py.backup
cp src/api/chat_service.py /backup/chat_service.py.backup
cp src/text2sql.py /backup/text2sql.py.backup

# Files are already in place, verify changes
git diff src/api/main.py
git diff src/api/chat_service.py
git diff src/text2sql.py

# Restart services
docker-compose up -d
# or
python -m uvicorn src.api.main:app --reload --port 8000
```

### 2. Frontend Deployment

```bash
# Navigate to frontend
cd frontend/web

# Verify changes
git diff src/lib/api.ts

# Build frontend
npm run build
# or
pnpm run build

# Deploy to appropriate environment
npm run deploy
# or copy build output to production server
```

### 3. Verification Steps

#### Backend Verification

```bash
# Check API is running
curl http://localhost:8000/

# Check logs for initialization
tail -f logs/bot.log | grep "ChatService initialized"

# Look for: "ChatService initialized with timeouts: request=90.0s, text2sql=30.0s"
```

#### Frontend Verification

```bash
# Check if timeouts are properly loaded
# In browser console:
# - Open dev tools (F12)
# - Check network tab for timeout values
# - Send a message to admin mode
# - Verify request takes up to 180s if needed
```

#### Functional Test

1. **Simple Query Test**
   - Mode: Admin
   - Query: "Сколько всего сообщений?"
   - Expected: Immediate response (< 10s)
   - Status: ✓

2. **Medium Query Test**
   - Mode: Admin
   - Query: "Сколько сообщений было отправлено на этой неделе?"
   - Expected: Response within 60s
   - Status: ✓

3. **Complex Query Test**
   - Mode: Admin
   - Query: "Покажи топ-5 пользователей по количеству сообщений с процентом"
   - Expected: Response within 180s
   - Status: ✓

## Rollback Plan

If issues occur after deployment:

### Quick Rollback

```bash
# Revert Python files
git checkout src/api/main.py
git checkout src/api/chat_service.py
git checkout src/text2sql.py

# Revert TypeScript file
git checkout frontend/web/src/lib/api.ts

# Restart services
docker-compose restart
```

### Manual Rollback (if git not available)

Restore from backup:
```bash
cp /backup/main.py.backup src/api/main.py
cp /backup/chat_service.py.backup src/api/chat_service.py
cp /backup/text2sql.py.backup src/text2sql.py
```

## Monitoring Post-Deployment

### Key Metrics to Watch

1. **Timeout Errors**
   ```bash
   grep -E "timeout|Timeout|TIMEOUT" logs/bot.log
   ```
   Expected: Should see fewer errors compared to before

2. **Admin Mode Usage**
   - Track how many queries are sent in admin mode
   - Track average response time
   - Track error rate

3. **Database Performance**
   - Monitor query execution times
   - Watch for slow queries
   - Check connection pool status

### Log Patterns to Monitor

✅ **Expected Patterns (Good):**
```
ChatService initialized with timeouts: request=90.0s, text2sql=30.0s
Processing message in admin mode...
SQL query executed successfully, X rows returned
```

❌ **Problem Patterns (Bad):**
```
Request timed out (too complex query)
Admin mode timeout on attempt N
LLM timeout after XXs
```

## Performance Benchmarks

After deployment, expected performance:

| Query Type | Expected Time | Max Time | Success Rate |
|-----------|---------------|----------|--------------|
| Simple    | 2-5s          | 10s      | 99.9%        |
| Medium    | 10-30s        | 60s      | 99%          |
| Complex   | 30-90s        | 180s     | 95%          |

## Support Information

If issues occur:

1. **Check Logs:**
   - Backend: `logs/bot.log`
   - Frontend: Browser DevTools Console

2. **Verify Timeouts:**
   - Backend: Search for timeout values in logged messages
   - Frontend: Check TIMEOUT_CONFIG in `frontend/web/src/lib/api.ts`

3. **Contact:**
   - Include logs from last 30 minutes
   - Include specific query that failed
   - Include error message and timestamp

## Documentation

- Detailed technical report: `TIMEOUT_FIX_REPORT.md`
- Summary: `ADMIN_MODE_TIMEOUT_FIX_SUMMARY.md`
- This file: `DEPLOYMENT_INSTRUCTIONS.md`

## Success Criteria

After deployment, the fix is successful if:

✅ Admin mode queries complete without "Request timed out" errors
✅ Complex queries have adequate time to process
✅ Error messages include timeout information
✅ Frontend provides visual feedback during long requests
✅ No performance degradation in normal mode
✅ Retry logic handles transient failures gracefully

---

**Deployment Date:** _______________
**Deployed By:** _______________
**Status:** ☐ Successful ☐ Rolled Back ☐ Partial
