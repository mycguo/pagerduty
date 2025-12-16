# Neon Database Setup for Render

Your Neon database is now configured! Follow these steps to connect it to your Render deployment.

## Your Neon Database

**Connection String:**
```
postgresql://neondb_owner:npg_QsL4KFJj7EUq@ep-snowy-king-ahfkl6oz-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

**Benefits:**
- ✅ **No expiration** - Unlike Render's free DB (90 days), Neon is permanent
- ✅ **3GB storage** - More than Render's free tier (1GB)
- ✅ **Autoscaling** - Scales to zero when not in use
- ✅ **Free tier** - No cost for your use case

## Setup Instructions

### Step 1: Add DATABASE_URL to Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Select your service**: `web-monitoring-dashboard`
3. **Click "Environment" tab** in the left sidebar
4. **Click "Add Environment Variable"**
5. **Add the variable:**
   - **Key:** `DATABASE_URL`
   - **Value:**
     ```
     postgresql://neondb_owner:npg_QsL4KFJj7EUq@ep-snowy-king-ahfkl6oz-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
     ```
6. **Click "Save Changes"**

### Step 2: Deploy

Render will automatically redeploy your service with the new database connection.

**Watch the logs for:**
```
=========================================
Migrating Default Monitors to PostgreSQL
=========================================
✓ Connected to PostgreSQL database
✓ Found 5 monitors to migrate
  ✓ Migrated: Wikipedia Health Check
  ✓ Migrated: Example.com Basic Test
  ...
Migration Complete: 5/5 monitors migrated
```

Then:
```
[Storage] Using PostgreSQL for data persistence
[Storage] PostgreSQL connection successful
[Storage] Loaded 5 monitors
```

### Step 3: Verify

1. Open your Render app URL
2. Check that your monitors are visible
3. Try creating a new monitor - it should persist across restarts!

## What Changed

### Before (Render Free DB)
- Database expires after 90 days
- 1GB storage
- Manual renewal required

### After (Neon DB)
- **No expiration** ✨
- 3GB storage
- Automatic, permanent persistence

## Troubleshooting

### "Failed to connect to PostgreSQL"

**Check connection string:**
- Make sure you copied the entire connection string
- Verify no extra spaces or line breaks
- Connection string should start with `postgresql://`

**Check Neon database status:**
- Log in to Neon console: https://console.neon.tech
- Verify the database is active (not paused)

### "Database already contains X monitors"

This is normal! It means:
- Migration script detected existing monitors
- Skipped migration to avoid duplicates
- Your data is preserved

### App still using file storage

Check Render logs for:
```
[Storage] Using file-based storage
```

This means DATABASE_URL isn't set correctly. Double-check:
1. Variable name is exactly `DATABASE_URL` (case-sensitive)
2. Value is the full connection string
3. Service was redeployed after adding the variable

## Managing Your Neon Database

### Neon Console
Access at: https://console.neon.tech

**Features:**
- View database size and connection stats
- SQL Editor for direct queries
- Backups (automatic and manual)
- Branching (copy database for testing)

### Backup Your Monitors

Even with Neon's reliability, regular backups are good practice:

```bash
# From your local machine
python scripts/backup_monitors.py
```

This creates timestamped backups in `backups/` directory.

### Monitor Database Size

Check in Neon Console → Your Project → Dashboard

**Free tier limits:**
- 3GB storage
- 512MB RAM
- Shared compute

For this monitoring app, you'll likely use **less than 10MB** even with thousands of test runs.

## Next Steps

1. ✅ Configure DATABASE_URL in Render (see Step 1 above)
2. ✅ Wait for deployment to complete
3. ✅ Verify monitors are loading
4. Optional: Set up Slack/Email alerts
   - Add `SLACK_WEBHOOK_URL` environment variable in Render Dashboard
   - For email alerts, add SMTP environment variables (see `.env.example`)
5. Optional: Schedule regular backups

## Questions?

**Can I use this locally?**
Yes! Add to your `.env` file:
```
DATABASE_URL=postgresql://neondb_owner:npg_QsL4KFJj7EUq@ep-snowy-king-ahfkl6oz-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

**Will I lose my current monitors?**
No! The migration script only runs if the database is empty. Existing monitors are preserved.

**Can I switch back to Render's database?**
Yes, but not recommended due to 90-day expiration. Just remove DATABASE_URL from environment variables.

**What if I exceed free tier limits?**
Very unlikely for monitoring use case. Neon will email you if you approach limits.
