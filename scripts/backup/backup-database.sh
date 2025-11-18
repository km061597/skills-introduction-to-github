#!/bin/bash
#
# SmartAmazon Database Backup Script
# Backs up PostgreSQL database with compression and optional S3 upload
#
# Usage: ./backup-database.sh [--upload-s3]
#

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/var/backups/smartamazon}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="smartamazon_db_${TIMESTAMP}.sql.gz"

# Database connection (from environment or .env file)
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-smartamazon}"
DB_USER="${POSTGRES_USER:-postgres}"
DB_PASSWORD="${POSTGRES_PASSWORD}"

# S3 configuration (optional)
S3_BUCKET="${BACKUP_S3_BUCKET:-}"
UPLOAD_S3=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --upload-s3)
            UPLOAD_S3=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_requirements() {
    log_info "Checking requirements..."

    if ! command -v pg_dump &> /dev/null; then
        log_error "pg_dump not found. Please install PostgreSQL client tools."
        exit 1
    fi

    if ! command -v gzip &> /dev/null; then
        log_error "gzip not found. Please install gzip."
        exit 1
    fi

    if [[ "$UPLOAD_S3" == true ]] && ! command -v aws &> /dev/null; then
        log_error "aws CLI not found. Please install AWS CLI for S3 upload."
        exit 1
    fi
}

create_backup_dir() {
    if [[ ! -d "$BACKUP_DIR" ]]; then
        log_info "Creating backup directory: $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
    fi
}

backup_database() {
    log_info "Starting database backup..."
    log_info "Database: $DB_NAME"
    log_info "Backup file: $BACKUP_FILE"

    # Set password for pg_dump
    export PGPASSWORD="$DB_PASSWORD"

    # Perform backup with compression
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --format=plain \
        --no-owner \
        --no-acl \
        --verbose \
        2>&1 | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"; then

        log_info "Backup completed successfully"

        # Get backup size
        BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)
        log_info "Backup size: $BACKUP_SIZE"

        # Unset password
        unset PGPASSWORD

        return 0
    else
        log_error "Backup failed"
        unset PGPASSWORD
        return 1
    fi
}

upload_to_s3() {
    if [[ "$UPLOAD_S3" == true && -n "$S3_BUCKET" ]]; then
        log_info "Uploading backup to S3: s3://${S3_BUCKET}/"

        if aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" "s3://${S3_BUCKET}/database/" --storage-class STANDARD_IA; then
            log_info "S3 upload successful"
        else
            log_error "S3 upload failed"
            return 1
        fi
    fi
}

cleanup_old_backups() {
    log_info "Cleaning up backups older than $RETENTION_DAYS days..."

    # Local cleanup
    find "$BACKUP_DIR" -name "smartamazon_db_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete

    local deleted=$(find "$BACKUP_DIR" -name "smartamazon_db_*.sql.gz" -type f -mtime +${RETENTION_DAYS} | wc -l)
    log_info "Deleted $deleted old local backups"

    # S3 cleanup (if configured)
    if [[ -n "$S3_BUCKET" ]]; then
        log_info "Cleaning up old S3 backups..."

        RETENTION_DATE=$(date -d "${RETENTION_DAYS} days ago" +%Y-%m-%d)
        aws s3 ls "s3://${S3_BUCKET}/database/" | while read -r line; do
            CREATE_DATE=$(echo "$line" | awk '{print $1}')
            FILE_NAME=$(echo "$line" | awk '{print $4}')

            if [[ "$CREATE_DATE" < "$RETENTION_DATE" ]]; then
                aws s3 rm "s3://${S3_BUCKET}/database/${FILE_NAME}"
                log_info "Deleted old S3 backup: $FILE_NAME"
            fi
        done
    fi
}

verify_backup() {
    log_info "Verifying backup integrity..."

    if gzip -t "${BACKUP_DIR}/${BACKUP_FILE}"; then
        log_info "Backup file integrity verified"
        return 0
    else
        log_error "Backup file is corrupted!"
        return 1
    fi
}

send_notification() {
    local status=$1
    local message=$2

    # Send notification via webhook (Slack, Discord, etc.)
    if [[ -n "${WEBHOOK_URL:-}" ]]; then
        curl -X POST "$WEBHOOK_URL" \
            -H 'Content-Type: application/json' \
            -d "{\"text\": \"Database Backup $status: $message\"}" \
            > /dev/null 2>&1 || true
    fi
}

# Main execution
main() {
    log_info "========================================="
    log_info "SmartAmazon Database Backup"
    log_info "========================================="
    log_info "Timestamp: $(date)"
    log_info ""

    check_requirements
    create_backup_dir

    if backup_database; then
        if verify_backup; then
            upload_to_s3
            cleanup_old_backups

            log_info ""
            log_info "========================================="
            log_info "Backup completed successfully!"
            log_info "========================================="
            log_info "Backup location: ${BACKUP_DIR}/${BACKUP_FILE}"

            send_notification "SUCCESS" "Database backup completed: ${BACKUP_FILE}"
            exit 0
        else
            log_error "Backup verification failed"
            send_notification "FAILED" "Backup verification failed"
            exit 1
        fi
    else
        log_error "Backup operation failed"
        send_notification "FAILED" "Backup operation failed"
        exit 1
    fi
}

# Run main function
main
