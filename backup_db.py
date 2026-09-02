#!/usr/bin/env python3
"""Backup script for AI-Organizer SQLite database."""

import shutil
from datetime import datetime, timedelta
from pathlib import Path


def backup_database(
    db_path: Path,
    backup_dir: Path,
    max_backups: int = 10,
    keep_days: int = 30,
) -> None:
    """
    Create a timestamped backup of the database.

    Args:
        db_path: Path to the database file
        backup_dir: Directory to store backups
        max_backups: Maximum number of backups to keep
        keep_days: Delete backups older than this many days
    """
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return

    # Create backup directory if it doesn't exist
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{db_path.stem}_backup_{timestamp}{db_path.suffix}"
    backup_path = backup_dir / backup_name

    # Copy database file
    try:
        shutil.copy2(db_path, backup_path)
        backup_size = backup_path.stat().st_size / 1024  # KB
        print(f"Backup created: {backup_path} ({backup_size:.1f} KB)")
    except Exception as e:
        print(f"Error creating backup: {e}")
        return

    # Clean up old backups
    cleanup_old_backups(backup_dir, db_path.stem, max_backups, keep_days)


def cleanup_old_backups(
    backup_dir: Path, db_stem: str, max_backups: int, keep_days: int
) -> None:
    """Remove old backup files based on count and age."""
    # Get all backup files for this database
    pattern = f"{db_stem}_backup_*.db"
    backups = sorted(
        backup_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True
    )

    if not backups:
        return

    # Remove backups beyond max_backups limit
    if len(backups) > max_backups:
        for old_backup in backups[max_backups:]:
            old_backup.unlink()
            print(f"Removed old backup (count limit): {old_backup.name}")

    # Remove backups older than keep_days
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    for backup in backups:
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        if mtime < cutoff_date:
            backup.unlink()
            print(f"Removed old backup (age limit): {backup.name}")


def main():
    """Main backup routine."""
    # Paths
    project_root = Path(__file__).parent
    db_path = project_root / "backend" / "data" / "ai_organizer.db"
    backup_dir = project_root / "backups"

    print("=" * 60)
    print("AI-Organizer Database Backup")
    print("=" * 60)
    print(f"Database: {db_path}")
    print(f"Backup directory: {backup_dir}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    # Create backup
    backup_database(
        db_path=db_path,
        backup_dir=backup_dir,
        max_backups=10,  # Keep last 10 backups
        keep_days=30,  # Delete backups older than 30 days
    )

    print("-" * 60)
    print("Backup complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
