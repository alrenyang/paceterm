## step 01

# Python 3.12 버전을 기준으로 가상환경 생성 (3.10 이상 필요)
uv venv --python 3.12 .venv

# retro-ui 라이브러리와 paceterm 앱을 편집 가능 상태(-e)로 설치
uv pip install --python .venv/bin/python -e ./retro-ui -e ./paceterm