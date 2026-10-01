from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from paceterm import __version__
from paceterm import settings as config_store
from paceterm.i18n import LANGUAGES, set_language, tr
from paceterm.serial_port import DEMO_PORT, list_ports



def _attach_console() -> None:
    """콘솔 없이 묶은 실행 파일에서도 글자를 낼 곳을 마련한다.

    윈도우는 콘솔 없이(`--windowed`) 빌드하면 sys.stdout 이 None 이라 `--list` 의 print 도,
    argparse 의 오류/도움말도 AttributeError 로 죽는다. 셸에서 실행했다면 그 셸의 콘솔에
    붙어 거기에 출력하고, 탐색기에서 더블클릭했다면 붙을 콘솔이 없으므로 조용히 버린다
    (창만 뜨는 것이 맞다). 어느 쪽이든 print 가 예외를 내지 않는 상태로 만든다.
    """
    if os.name == "nt" and sys.stdout is None:
        try:
            import ctypes

            if ctypes.windll.kernel32.AttachConsole(-1):  # -1 = 부모 프로세스의 콘솔
                sys.stdout = open("CONOUT$", "w", encoding="utf-8", buffering=1)
                sys.stderr = open("CONOUT$", "w", encoding="utf-8", buffering=1)
        except (OSError, AttributeError):
            pass
    for name in ("stdout", "stderr"):
        if getattr(sys, name, None) is None:
            setattr(sys, name, open(os.devnull, "w", encoding="utf-8"))

def _report_fatal(message: str) -> None:
    """시작하다 죽었을 때 알린다. 콘솔이 없으면 이것 말고는 알릴 방법이 없다."""
    try:
        import pygame

        pygame.display.message_box("pace-term", message, message_type="error")
    except Exception:  # 상자도 못 띄우는 상황이면 더 할 수 있는 것이 없다
        pass

def main(argv: list[str] | None = None) -> int:
    # 추후 여기에 argparse를 이용한 CLI 인자 처리 로직 추가
    _attach_console()
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["ctl"]:
        # 실행 중인 baram-term 에 붙는 제어 명령 (ctl.py). 창을 띄우지 않고 pygame 도 올리지 않는다
        from paceterm import ctl

        return ctl.main(argv[1:])
    parser = argparse.ArgumentParser(
        prog="pcae-term",
        description="firmware CLI serial terminal",
        epilog="pcae-term ctl --help: control a running pcae-term from another program",
    )
    parser.add_argument("port", nargs="?", help="serial port or pyserial URL (loop://, socket://host:port)")
    parser.add_argument("-b", "--baud", type=int)
    parser.add_argument("--demo", action="store_true", help=f"connect to the built-in fake firmware ({DEMO_PORT})")
    parser.add_argument("--list", action="store_true", help="list serial ports and exit")
    parser.add_argument("--theme")
    parser.add_argument("--font-size", type=int)
    parser.add_argument("--size", help="window size in cells, COLSxROWS")
    parser.add_argument("--lang", choices=LANGUAGES)
    parser.add_argument("--config", type=Path, help=f"settings file (default: {config_store.default_path()})")
    parser.add_argument("--version", action="version", version=f"pcae-term {__version__}")
    args = parser.parse_args(argv)

    config_path = args.config or config_store.default_path()
    config, load_error = config_store.load(config_path)
    if args.lang:
        config.lang = args.lang
    set_language(config.lang or None)

    if args.list:
        for port in list_ports():
            print(port)
        return 0

    if args.demo:
        config.port = DEMO_PORT
    elif args.port:
        config.port = args.port
    if args.baud:
        config.baud = args.baud
    if args.theme:
        config.theme = args.theme
    if args.font_size:
        config.font_size = args.font_size
    if args.size:
        config.cols, config.rows = (int(v) for v in args.size.lower().split("x"))

    from paceterm.app import PaceTermApp

    try:
        term = PaceTermApp(
            config.port_settings(),
            theme=config.theme,
            font_size=config.font_size,
            size=(config.cols, config.rows),
            config=config,
            config_path=config_path,
        )
        if load_error:
            term.notice(tr("notice.settings_load_failed", error=load_error), error=True)
        term.run()

    except Exception as e:
        # 콘솔 없이 실행하면 여기서 죽어도 화면에 아무것도 남지 않는다 (폰트 못 찾음 등).
        # 상자로 알리고, 콘솔이 있으면 트레이스백도 그대로 보이도록 다시 올린다
        _report_fatal(f"{type(e).__name__}: {e}")
        raise
    return 0

    # app = PaceTermApp()
    # app.run()

if __name__ == "__main__":
    sys.exit(main())