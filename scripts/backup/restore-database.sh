#!/bin/bash
#
# SmartAmazon Database Restore Script
# Restores PostgreSQL database from backup
#
# Usage: ./restore-database.sh <backup-file.sql.gz>
#

set -euo pipefail

# Configuration
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-smartamazon}"
DB_USER="${POSTGRES_USER:-postgres}"
DB_PASSWORD="${POSTGRES_PASSWORD}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if backup file is provided
if [[ $# -eq 0 ]]; then
    log_error "Usage: $0 <backup-file.sql.gz>"
    exit 1
fi

BACKUP_FILE="$1"

# Validate backup file exists
if [[ ! -f "$BACKUP_FILE" ]]; then
    log_error "Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Confirmation prompt
log_warning "========================================="
log_warning "WARNING: This will OVERWRITE the database"
log_warning "========================================="
log_warning "Database: $DB_NAME"
log_warning "Backup file: $BACKUP_FILE"
echo ""
read -p "Are you sure you want to continue? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
    log_info "Restore cancelled by user"
    exit 0
fi

log_info "Starting database restore..."

# Set password
export PGPASSWORD="$DB_PASSWORD"

# Restore database
if gunzip -c "$BACKUP_FILE" | psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"; then
    log_info "Database restored successfully!"
    unset PGPASSWORD
    exit 0
else
    log_error "Database restore failed"
    unset PGPASSWORD
    exit 1
fi
