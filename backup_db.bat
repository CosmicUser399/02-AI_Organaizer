@echo off
REM Backup script for Windows
REM Run this script to create a backup of the database

cd /d "%~dp0"
python backup_db.py
pause
