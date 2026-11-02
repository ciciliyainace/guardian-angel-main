@echo off
setlocal
echo =======================================================
echo          SentinelAI Live Host Network Sensor Agent
echo =======================================================
cd /d "%~dp0"

if not exist sensor_config.json (
    echo [!] sensor_config.json not found.
    echo [*] Starting automatic enrollment against backend...
    python enroll.py
    if not exist sensor_config.json (
        echo [!] Enrollment failed or was cancelled. Exiting.
        pause
        exit /b 1
    )
)

echo [*] Starting live sensor agent...
python sensor_agent.py
pause
