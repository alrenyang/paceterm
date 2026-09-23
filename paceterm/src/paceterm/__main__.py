import sys
from paceterm.app import PaceTermApp

def main():
    # 추후 여기에 argparse를 이용한 CLI 인자 처리 로직 추가
    app = PaceTermApp()
    app.run()

if __name__ == "__main__":
    sys.exit(main())