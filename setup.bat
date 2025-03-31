:: filepath: /c:/Users/ty/Desktop/Best Programs I Created/Youtube Download Script/setup.bat
@echo off
echo Setting up Python environment...

:: Create new virtual environment
python -m venv venv

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install requirements
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo Environment setup complete!
echo.
echo Now you can run: .\build.bat
pause