## step 01

# Python 3.12 버전을 기준으로 가상환경 생성 (3.10 이상 필요)
uv venv --python 3.12 .venv

# retro-ui 라이브러리와 paceterm 앱을 편집 가능 상태(-e)로 설치
uv pip install --python .venv/bin/python -e ./retro-ui -e ./paceterm


## step 02

# 가상환경의 python으로 paceterm 모듈 실행
.venv/bin/python -m paceterm




https://github.com/alrenyang/paceterm.git


echo "# paceterm" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/alrenyang/paceterm.git
git push -u origin main

git remote add origin https://github.com/alrenyang/paceterm.git
git branch -M main
git push -u origin main