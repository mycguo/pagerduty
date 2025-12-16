# Database Expiration Guide

## 90-Day Limitation

Render's free PostgreSQL database expires after **90 days**. This is a hard limit and the database will be **deleted**, not just disabled.

## What Happens When It Expires

1. **Database deleted** - All monitor configurations and test history are permanently lost
2. **App falls back to file storage** - The app will continue running but data won't persist
3. **Monitors reset** - You'll only have the default monitors from `default_monitors.json`

You'll see this in Render logs:
```
[Storage] ERROR: Failed to connect to PostgreSQL: connection error
[Storage] Falling back to file storage
[Storage] Using file-based storage (data will not persist on Render free tier)
```

## Solutions

### Option 1: Renew Free Database Every 90 Days (Free)

**Steps to renew:**

1. **Before expiration**, backup your monitors:
   ```bash
   python scripts/backup_monitors.py
   ```
   This creates `backups/monitors_backup_YYYYMMDD_HHMMSS.json`

2. **In Render Dashboard:**
   - Go to your database
   - Delete the expired/expiring database
   - Create a new free PostgreSQL database with the same name

3. **Redeploy your web service:**
   - Render will auto-deploy and connect to the new database
   - Default monitors will be restored automatically

4. **Restore custom monitors:**
   ```bash
   DATABASE_URL="your-new-database-url" python scripts/backup_monitors.py --restore backups/monitors_backup_latest.json
   ```

**Pros:** Free
**Cons:** Manual process every 90 days, data loss if you forget

### Option 2: Upgrade to Paid Database ($7/month)

**Steps:**

1. In Render Dashboard, upgrade your database from "Free" to "Starter" plan
2. No code changes needed - same DATABASE_URL will work

**Update `render.yaml`:**
```yaml
databases:
  - name: monitoring-db
    databaseName: monitoring
    user: monitoring_user
    plan: starter  # Changed from 'free'
```

**Pros:** Set it and forget it, no data loss
**Cons:** $7/month cost

### Option 3: Use External Free Database (Free, No Expiration)

Use a database service with a better free tier:

**Supabase (Recommended):**
- 500MB storage
- No expiration
- Excellent uptime
- Sign up: https://supabase.com

**Neon (Alternative):**
- 3GB storage
- No expiration
- Serverless Postgres
- Sign up: https://neon.tech

**Steps:**
1. Create database on external service
2. Get connection string (PostgreSQL URL)
3. In Render Dashboard, add/update environment variable:
   ```
   DATABASE_URL=postgresql://user:password@host.com:5432/dbname
   ```
4. Redeploy

**Pros:** Free, no expiration, more storage
**Cons:** Slight latency increase (external connection)

### Option 4: Git-Based Backup (Automated)

Store monitor configurations in your Git repository automatically.

**Coming soon** - I can implement an automatic backup system that commits monitor changes to Git.

## Backup Script Usage

### Create Backup

```bash
# Local development
source .venv/bin/activate
python scripts/backup_monitors.py

# On Render (using web console or manual trigger)
DATABASE_URL=$DATABASE_URL python3 scripts/backup_monitors.py
```

Creates:
- `backups/monitors_backup_YYYYMMDD_HHMMSS.json` - Timestamped backup
- `backups/monitors_backup_latest.json` - Always latest version

### Restore from Backup

```bash
# Local development
source .venv/bin/activate
python scripts/backup_monitors.py --restore backups/monitors_backup_latest.json

# On Render (after database renewal)
DATABASE_URL=$DATABASE_URL python3 scripts/backup_monitors.py --restore backups/monitors_backup_latest.json
```

## Monitoring Expiration

Render sends email notifications:
- **14 days** before expiration
- **7 days** before expiration
- **1 day** before expiration

Set calendar reminders for yourself as backup!

## Recommended Approach

**For personal/testing:** Option 1 (renew every 90 days) or Option 3 (external free database)

**For production:** Option 2 (paid database) - Don't risk data loss

## Recovery Checklist

If the database expired and you lost data:

- [ ] Check `backups/` directory for recent backups
- [ ] Create new database (Render or external)
- [ ] Update DATABASE_URL if needed
- [ ] Redeploy application
- [ ] Restore from backup if available
- [ ] Recreate custom monitors if no backup exists
- [ ] Set calendar reminder for next expiration

## Prevention Tips

1. **Run backups weekly:**
   ```bash
   # Add to cron or set calendar reminder
   python scripts/backup_monitors.py
   ```

2. **Store backups in Git:**
   ```bash
   git add backups/
   git commit -m "Weekly monitor backup"
   git push
   ```

3. **Set calendar reminders** for 75 days after database creation

4. **Consider upgrading to paid** if monitors are critical

## Questions?

- How much data do I have? Check database size in Render Dashboard
- Can I extend the 90 days? No, it's a hard limit on free tier
- Will I lose test history? Yes, unless you backup before expiration
- Can I export test runs? Not currently implemented, only monitors

## Need Help?

Check logs on Render to verify which storage backend is active:
- `[Storage] Using PostgreSQL for data persistence` = ✓ Good
- `[Storage] Using file-based storage` = ⚠️ Not persistent on Render
