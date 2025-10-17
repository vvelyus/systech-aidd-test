# Sprint 5 - Production Deployment Checklist

**Version:** 1.0.0
**Date:** 2025-10-17
**Target Deployment:** Production

---

## Pre-Deployment Verification

### Code Quality
- [ ] All tests passing: `pytest tests/ -v --cov=src`
- [ ] Code coverage > 80%: `pytest --cov-report=html`
- [ ] No TypeScript errors: `npm run type-check`
- [ ] No ESLint errors: `npm run lint`
- [ ] No Python linting errors: `pylint src/`

### Backend Tests
- [ ] Unit tests: 30/30 passing ✅
- [ ] Integration tests: 16/16 passing ✅
- [ ] Performance tests: 15/15 passing ✅
- [ ] Database migrations applied

### Frontend Tests
- [ ] E2E tests: 29/29 passing ✅
- [ ] Component rendering tests passing
- [ ] Responsive design verified (mobile/tablet/desktop)
- [ ] Dark mode tested (if enabled)

### Documentation
- [ ] API Contract complete: `frontend/doc/api-contract.md`
- [ ] Architecture documented: `docs/ARCHITECTURE_S5.md`
- [ ] Testing Guide complete: `docs/TESTING_GUIDE_S5.md`
- [ ] README updated with deployment instructions
- [ ] Known issues documented

---

## Database Preparation

### SQLite (Development)
- [ ] Database file: `data/messages.db`
- [ ] Tables created via migrations
- [ ] Indexes created:
  - [ ] `idx_chat_messages_session_id`
  - [ ] `idx_chat_sessions_user_id`
  - [ ] `idx_chat_messages_created_at`
- [ ] WAL mode enabled
- [ ] Test data loaded (optional)

### PostgreSQL (Production)
- [ ] Database created and permissions set
- [ ] Connection pooling configured (min: 5, max: 20)
- [ ] Indexes created
- [ ] Backups configured (daily automated)
- [ ] Replication tested (if applicable)
- [ ] Connection string: `postgresql://user:pass@host:5432/chat_db`

### Database Backups
- [ ] Backup strategy documented
- [ ] Automated backup job scheduled
- [ ] Backup retention policy: 30 days
- [ ] Backup restoration tested
- [ ] Encryption enabled for backups

---

## Secrets & Configuration

### Environment Variables
- [ ] `.env.production` created
- [ ] LLM API keys configured:
  - [ ] `LLM_API_KEY` set
  - [ ] `LLM_MODEL` specified (e.g., "gpt-4")
  - [ ] `LLM_BASE_URL` set (if using custom endpoint)
- [ ] Database URL: `DATABASE_URL`
- [ ] Redis URL (if caching enabled): `REDIS_URL`
- [ ] Debug mode disabled: `DEBUG=false`
- [ ] CORS origins configured:
  - [ ] `CORS_ORIGINS` restricted to domain(s)
- [ ] Rate limiting configured:
  - [ ] `RATE_LIMIT_WINDOW` = 60 (seconds)
  - [ ] `RATE_LIMIT_MAX_REQUESTS` = 100

### Secrets Management
- [ ] Secrets stored in secure vault (AWS Secrets Manager, HashiCorp Vault, etc.)
- [ ] Never commit `.env` file to Git
- [ ] `.gitignore` includes environment files
- [ ] Secret rotation policy defined
- [ ] Access logs for secret retrieval enabled

---

## API Server Configuration

### FastAPI Setup
- [ ] Uvicorn configured:
  - [ ] Workers: 4 (for production)
  - [ ] Timeout: 120 seconds
  - [ ] Keep-alive: 65 seconds
- [ ] ASGI server: Uvicorn or Gunicorn
- [ ] Worker process manager: Supervisor or systemd
- [ ] Port configured: 8000 (or custom)
- [ ] Health check endpoint: `/health`

### Load Balancer (nginx)
- [ ] nginx installed and configured
- [ ] SSL/TLS certificates installed
- [ ] Proxy settings:
  - [ ] `proxy_pass http://localhost:8000`
  - [ ] `proxy_set_header X-Real-IP $remote_addr`
  - [ ] `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for`
- [ ] Gzip compression enabled
- [ ] Cache headers configured
- [ ] Rate limiting: `limit_req`

### SSL/TLS
- [ ] Certificate installed (from Let's Encrypt or CA)
- [ ] Certificate renewal automated (certbot)
- [ ] SSL protocols: TLSv1.2 minimum
- [ ] HTTPS redirect enabled
- [ ] HSTS header: `Strict-Transport-Security: max-age=31536000`

---

## Frontend Deployment

### Next.js Build
- [ ] Production build: `npm run build`
- [ ] Build verification: `npm run lint && npm run type-check`
- [ ] No build errors or warnings
- [ ] Build artifacts optimized (tree-shaking, code-splitting)
- [ ] Source maps generated for debugging

### Static Files
- [ ] Public assets accessible: `/public/*`
- [ ] CDN configured (optional):
  - [ ] CloudFront, Cloudflare, or similar
  - [ ] Cache policy: 1 year for versioned files
- [ ] Static site generation (SSG) for static pages

### API Integration
- [ ] Frontend `.env` updated:
  - [ ] `NEXT_PUBLIC_API_URL` = `https://api.example.com`
  - [ ] Correct API endpoints configured
- [ ] CORS headers from backend match frontend domain
- [ ] API calls use HTTPS in production

### Performance
- [ ] Image optimization enabled
- [ ] Font optimization configured
- [ ] Bundle size analyzed: `npm run analyze`
- [ ] Lighthouse score > 90
- [ ] Core Web Vitals targets met

---

## Monitoring & Logging

### Backend Logging
- [ ] Logging configured:
  - [ ] Format: JSON (for ELK/Splunk compatibility)
  - [ ] Level: INFO (production)
  - [ ] Output: Stdout or log file
- [ ] Log rotation configured
- [ ] Sensitive data (passwords, tokens) not logged
- [ ] Error tracking service: Sentry or similar
  - [ ] DSN configured
  - [ ] Release tracking enabled

### Frontend Logging
- [ ] Console errors captured
- [ ] User interactions tracked (analytics)
- [ ] Performance metrics sent to backend
- [ ] Error boundary configured

### Monitoring Metrics
- [ ] API response time tracked
- [ ] Error rate monitored (threshold: > 1%)
- [ ] Database query performance tracked
- [ ] LLM API latency monitored
- [ ] Memory usage monitored
- [ ] Disk space monitored

### Alerts
- [ ] Alert rules configured:
  - [ ] High error rate (> 5%)
  - [ ] Database connection pool exhausted
  - [ ] API response time > 10s
  - [ ] Disk space < 10%
- [ ] Notification channels configured:
  - [ ] Email alerts
  - [ ] Slack/Teams webhooks
  - [ ] PagerDuty (for critical alerts)

---

## Security Hardening

### Authentication
- [ ] Rate limiting on login endpoints
- [ ] CSRF protection enabled
- [ ] Session timeout configured: 1 hour
- [ ] Remember-me tokens: 30 days TTL
- [ ] JWT token rotation enabled (if using JWT)

### Authorization
- [ ] Admin endpoints protected
- [ ] Role-based access control (RBAC) tested
- [ ] SQL injection prevention verified:
  - [ ] Parameterized queries
  - [ ] Input validation
  - [ ] SQL keyword whitelisting
- [ ] XSS protection enabled

### Data Security
- [ ] Encryption in transit: HTTPS only
- [ ] Encryption at rest: Database encryption enabled
- [ ] Sensitive data fields encrypted:
  - [ ] API keys
  - [ ] Passwords (hashed)
  - [ ] User tokens
- [ ] PII data handling compliant

### Infrastructure Security
- [ ] Firewall rules configured
- [ ] SSH key-based auth (no passwords)
- [ ] Security groups configured:
  - [ ] API server: port 8000 from LB only
  - [ ] Database: port 5432 from API only
  - [ ] LB: ports 80/443 from internet
- [ ] DDoS mitigation enabled (optional)

---

## Performance Optimization

### Database
- [ ] Query performance baseline established
- [ ] Slow query log enabled
- [ ] Connection pool tuned
- [ ] Caching layer active (Redis optional)

### API
- [ ] Response time targets met:
  - [ ] LLM response < 3s
  - [ ] Text-to-SQL < 2s
  - [ ] History retrieval < 500ms
- [ ] Compression enabled (gzip)
- [ ] Request/response caching configured

### Frontend
- [ ] Page load time < 3s
- [ ] Time to Interactive (TTI) < 5s
- [ ] Largest Contentful Paint (LCP) < 2.5s
- [ ] Cumulative Layout Shift (CLS) < 0.1

---

## Rollback Plan

### Versioning
- [ ] Git tag created: `v1.0.0-s5`
- [ ] Release notes published
- [ ] Docker image tagged (if using containers)

### Rollback Procedure
- [ ] Previous version accessible
- [ ] Database rollback script tested
- [ ] Estimated rollback time < 15 minutes
- [ ] Team trained on rollback procedure

### Disaster Recovery
- [ ] Database backup restored successfully
- [ ] Recovery Time Objective (RTO): < 1 hour
- [ ] Recovery Point Objective (RPO): < 1 hour
- [ ] DR drill completed successfully

---

## Post-Deployment

### Smoke Tests
- [ ] API health check passes
- [ ] Chat message flow works
- [ ] Admin mode (Text-to-SQL) works
- [ ] History persistence verified
- [ ] Database connectivity verified
- [ ] LLM API connectivity verified

### User Acceptance Testing (UAT)
- [ ] Critical user flows tested
- [ ] Edge cases verified
- [ ] Performance acceptable to users
- [ ] UI renders correctly on target browsers

### Documentation
- [ ] Deployment guide updated
- [ ] Runbook created for operations team
- [ ] Known issues documented
- [ ] Contact information for support

### Communication
- [ ] Team notified of deployment
- [ ] Stakeholders informed
- [ ] Status page updated (if applicable)
- [ ] Release notes published

---

## Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| Developer | __________ | _____ | ✅ |
| QA Lead | __________ | _____ | ✅ |
| DevOps Lead | __________ | _____ | ✅ |
| Product Manager | __________ | _____ | ✅ |

---

## Notes

```
Deployment Timestamp: _______________________
Deployed By: _______________________________
Deployment Duration: ________________________
Any Issues Encountered: _____________________
_______________________________________________
```

---

## Deployment Commands

### Backend Deployment
```bash
# Stop current service
systemctl stop chat-api

# Deploy new version
git checkout v1.0.0-s5
uv install
alembic upgrade head

# Start service
systemctl start chat-api
systemctl status chat-api

# Verify
curl http://localhost:8000/health
```

### Frontend Deployment
```bash
# Build
npm run build

# Verify build
npm run lint && npm run type-check

# Deploy (example with Vercel)
vercel --prod

# Verify
curl https://chat.example.com/
```

### Database Backup Before Deployment
```bash
# SQLite
cp data/messages.db data/messages.db.backup.$(date +%s)

# PostgreSQL
pg_dump -U user chat_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

---

**Deployment Status:** ✅ Ready for Production
**Checklist Version:** 1.0
**Last Updated:** 2025-10-17
