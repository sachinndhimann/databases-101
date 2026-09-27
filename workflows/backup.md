# Workflow: Backup & Restore (PostgreSQL, this repo's docker-compose setup)

## Take a logical backup

```bash
docker exec db101-postgres pg_dump -U db101 -d db101 -F c -f /tmp/db101.dump
docker cp db101-postgres:/tmp/db101.dump ./backups/db101-$(date +%Y%m%d-%H%M%S).dump
```

`-F c` uses the custom format — compressed, and restorable selectively
(single tables, schema-only, etc.), unlike a plain `.sql` text dump.

## Restore into a fresh database

```bash
docker exec -i db101-postgres createdb -U db101 db101_restore_test
docker cp ./backups/db101-<timestamp>.dump db101-postgres:/tmp/restore.dump
docker exec db101-postgres pg_restore -U db101 -d db101_restore_test /tmp/restore.dump
```

## Schedule (example cron entry for a real deployment)

```
0 2 * * * /path/to/backup_script.sh >> /var/log/db101-backup.log 2>&1
```

Daily at 2am. For anything beyond a toy project, prefer point-in-time
recovery (continuous WAL archiving) over a single nightly dump — Chapter 8
`docs/production.md` explains why.

## Test the restore — this step is not optional

A backup you have never restored is unverified. At minimum, restore into a
scratch database monthly and run a row-count sanity check against a few
key tables.
