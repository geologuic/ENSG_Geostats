@echo off
cd /d %~dp0

if not exist .venv (
    uv venv -p3.13 .venv
    if not exist .venv (
        echo Fatal Error: venv creation failed
        pause
        exit /b 1
    )
    call .venv\Scripts\activate
	uv sync
    if errorlevel 1 (
        echo Fatal Error: package installation failed
        pause
        exit /b 1
    )
    python -m ipykernel install --user --name=monenv --display-name "Python Geostat"
) else (
    call .venv\Scripts\activate
)

jupyter lab
pause