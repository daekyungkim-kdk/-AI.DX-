@echo off
chcp 65001 > nul
echo ===================================================
echo   하루 칼로리 계산기 실행을 준비합니다...
echo ===================================================

:: .venv 폴더가 없는 경우에만 최초 1회 자동 생성 및 설치
if not exist ".venv" (
    echo [안내] 가상환경이 없어 최초 설정을 진행합니다. (약 1분 소요)
    python -m venv .venv
    echo [안내] 필요한 라이브러리를 자동으로 설치합니다...
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    echo [안내] 설치가 완료되었습니다!
)

echo 브라우저 창이 열릴 때까지 잠시만 기다려주세요...
.\.venv\Scripts\python.exe -m streamlit run app.py

pause