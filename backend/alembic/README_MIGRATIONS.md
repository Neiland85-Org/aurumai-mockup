# Alembic Database Migrations

This directory contains database migration scripts for the AurumAI backend using Alembic.

## 📋 Overview

Alembic manages database schema changes (migrations) in a version-controlled way, allowing you to:

- **Track** all changes to the database schema over time
- **Apply** migrations to upgrade the database
- **Rollback** changes if something goes wrong
- **Generate** migrations automatically from model changes

## 🚀 Quick Start

### Prerequisites

1. **Ensure PostgreSQL is running:**

   ```bash
   docker compose up -d postgres
   ```

2. **Activate virtual environment:**

   ```bash
   cd backend
   source .venv/bin/activate
   ```

3. **Verify connection:** Ensure `.env` file has correct database credentials.

### Apply Migrations

```bash
# From project root
make migrate

# Or from backend directory
cd backend
alembic upgrade head
```

This will apply all pending migrations and create/update database tables.

## 📝 Common Operations

### 1. Create a New Migration

**Automatic (recommended):**

```bash
# After modifying models in infrastructure/db/models.py
make migration msg="Add new column to machines"

# Or from backend directory
cd backend
alembic revision --autogenerate -m "Add new column to machines"
```

Alembic will:

- Compare current database state with models
- Generate migration code automatically
- Create a new file in `alembic/versions/`

**Manual (advanced):**

```bash
make migration-empty msg="Custom data migration"

# Or
cd backend
alembic revision -m "Custom data migration"
```

Use this when you need to write custom SQL or data transformations.

### 2. Apply Migrations

```bash
# Apply all pending migrations
make migrate

# Or apply one by one
cd backend
alembic upgrade +1  # Apply next migration
```

### 3. Rollback Migrations

```bash
# Rollback last migration
make migrate-rollback

# Or from backend directory
cd backend
alembic downgrade -1

# Rollback to specific version
alembic downgrade abc123def456

# Rollback all migrations
alembic downgrade base
```

### 4. View Migration Status

```bash
# Show current migration version
make migrate-current

# Show migration history
make migrate-history

# Or from backend directory
cd backend
alembic current
alembic history --verbose
```

## 📁 Directory Structure

```
backend/alembic/
├── versions/                    # Migration files (one per migration)
│   └── 698c22942be3_initial_migration_create_all_tables.py
├── env.py                       # Alembic environment configuration
├── script.py.mako              # Template for new migrations
├── README                       # Auto-generated Alembic README
└── README_MIGRATIONS.md         # This file

backend/
├── alembic.ini                  # Alembic configuration
└── infrastructure/
    └── db/
        ├── models.py            # SQLAlchemy models
        └── postgres_config.py   # Database configuration
```

## 🔍 Migration File Anatomy

Each migration file has two main functions:

```python
def upgrade() -> None:
    """Apply changes to upgrade the database schema."""
    op.create_table('users', ...)
    op.add_column('machines', ...)

def downgrade() -> None:
    """Reverse changes to downgrade the database schema."""
    op.drop_column('machines', ...)
    op.drop_table('users')
```

## 🎯 Best Practices

### 1. Always Review Auto-Generated Migrations

```bash
# After creating a migration
cat backend/alembic/versions/<migration_file>.py

# Check what will be applied
alembic upgrade head --sql  # Dry run (shows SQL without applying)
```

### 2. Test Migrations Locally First

```bash
# Apply migration
make migrate

# Test your application
make dev

# If something is wrong, rollback
make migrate-rollback

# Fix migration file and try again
make migrate
```

### 3. Never Edit Applied Migrations

❌ **DON'T:** Edit a migration that's already been applied in production  
✅ **DO:** Create a new migration to fix the issue

```bash
# Create a corrective migration
make migration msg="Fix column type in predictions table"
```

### 4. Include Data Migrations When Needed

```python
def upgrade() -> None:
    # Schema change
    op.add_column('machines', sa.Column('status', sa.String(20)))

    # Data migration
    op.execute("UPDATE machines SET status = 'active' WHERE operational = true")
    op.execute("UPDATE machines SET status = 'inactive' WHERE operational = false")

    # Drop old column
    op.drop_column('machines', 'operational')
```

### 5. Keep Migrations Small and Focused

✅ **GOOD:** One migration per logical change  
❌ **BAD:** Combining unrelated changes in one migration

## ⚠️ Common Issues

### Issue 1: "Target database is not up to date"

**Problem:** Someone else applied migrations you don't have.

**Solution:**

```bash
# Pull latest code
git pull

# Apply missing migrations
make migrate
```

### Issue 2: "Can't locate revision identified by 'head'"

**Problem:** Alembic can't find migration files.

**Solution:**

```bash
# Ensure you're in the backend directory
cd backend

# Verify alembic.ini exists
ls -la alembic.ini

# Try again
alembic upgrade head
```

### Issue 3: Migration fails with SQL error

**Problem:** Migration has invalid SQL or conflicts with existing data.

**Solution:**

```bash
# 1. Check the error message
alembic upgrade head

# 2. Rollback if partially applied
make migrate-rollback

# 3. Fix the migration file
nano alembic/versions/<migration_file>.py

# 4. Try again
make migrate
```

### Issue 4: "Database connection failed"

**Problem:** PostgreSQL is not running or credentials are wrong.

**Solution:**

```bash
# 1. Check PostgreSQL is running
docker ps | grep postgres

# 2. Start if not running
docker compose up -d postgres

# 3. Verify credentials in .env
cat .env | grep DB_

# 4. Test connection
docker exec -it aurumai-postgres-dev psql -U aurumai -d aurumai
```

## 🔄 Workflow Example

### Scenario: Add a new field to the machines table

**1. Update the model:**

```python
# backend/infrastructure/db/models.py
class MachineModel(Base):
    # ... existing fields ...
    maintenance_schedule = Column(String(100))  # NEW
```

**2. Generate migration:**

```bash
make migration msg="Add maintenance_schedule to machines"
```

**3. Review the generated migration:**

```bash
cat backend/alembic/versions/*_add_maintenance_schedule_to_machines.py
```

**4. Apply the migration:**

```bash
make migrate
```

**5. Verify in database:**

```bash
make db
# In psql:
\d machines  # Describe table structure
```

**6. Test your application:**

```bash
make dev
```

**7. Commit the migration:**

```bash
git add backend/alembic/versions/*_add_maintenance_schedule_to_machines.py
git add backend/infrastructure/db/models.py
git commit -m "feat: Add maintenance_schedule field to machines"
```

## 🚨 Production Deployment

### Pre-Deployment Checklist

- [ ] All migrations tested locally
- [ ] Migration files committed to git
- [ ] Backup database before applying migrations
- [ ] Review migration SQL with `alembic upgrade head --sql`
- [ ] Plan rollback strategy if something goes wrong

### Deployment Steps

```bash
# 1. Backup database
docker exec aurumai-postgres-prod pg_dump -U aurumai aurumai > backup_$(date +%Y%m%d).sql

# 2. Pull latest code
git pull origin main

# 3. Apply migrations
cd backend
source .venv/bin/activate
alembic upgrade head

# 4. Restart application
docker compose -f docker-compose.prod.yml restart backend

# 5. Verify
docker compose -f docker-compose.prod.yml logs backend
```

### Rollback in Production

```bash
# If something goes wrong:

# 1. Rollback migration
cd backend
alembic downgrade -1

# 2. Restart application
docker compose -f docker-compose.prod.yml restart backend

# 3. Restore from backup if needed
docker exec -i aurumai-postgres-prod psql -U aurumai aurumai < backup_20251115.sql
```

## 📚 Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [TimescaleDB Hypertables](https://docs.timescale.com/use-timescale/latest/hypertables/)

## 🆘 Getting Help

If you encounter issues:

1. Check this README
2. Review Alembic logs: `alembic upgrade head --verbose`
3. Check application logs: `make logs`
4. Ask the team via email
5. Create an issue in the repository

---

**Last Updated:** 15 de noviembre de 2025  
**Maintainer:** DevOps Team
