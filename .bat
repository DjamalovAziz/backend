@REM .bat

chcp 65001 > nul

del /f /q db.sqlite3 2>nul

pushd backend

for /f "delims=" %%i in ('dir /ad /s /b ^| findstr /i /e "__pycache__"') do (
    rmdir /s /q "%%i"
)

for /r %%i in (*_initial.py) do del /f /q "%%i" 2>nul

taskkill /f /im python.exe >nul 2>&1

python manage.py makemigrations

python manage.py migrate

python manage.py runserver

@REM uvicorn core.asgi:application --host 0.0.0.0 --port 8000

popd

pause