@echo off
chcp 65001 > nul
echo 하루 칼로리 계산기를 실행합니다...
echo 브라우저 창이 열릴 때까지 잠시만 기다려주세요.

:: 작성하신 가상환경 경로를 그대로 사용하여 Streamlit 실행
.\.venv\Scripts\python.exe -m streamlit run app.py

pause