#!/bin/bash
# Backup script for Linux/macOS
# Run this script to create a backup of the database

cd "$(dirname "$0")"
python3 backup_db.py
