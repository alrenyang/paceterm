from retroui import App, Terminal, VBox, HBox, Label, MenuBar, Menu, MenuItem

class PaceTermApp:
    def __init__(self):
        self.app = App(
            title="PaceTerm - Firmware CLI", 
            size=(120, 36), 
            theme="mono"
        )
        
        # retroui 내부 규격에 맞추어 키워드 인자 대신 위치 인자 또는 올바른 형태로 MenuItem 생성
        # (만약 MenuItem이 (text, callback) 형태의 위치 인자를 받거나 다른 이름을 쓴다면 아래와 같이 정의합니다)
        file_menu = Menu("파일(F)", [
            MenuItem("끝내기(X)", self.action_exit)
        ])
        
        port_menu = Menu("포트(P)", [
            MenuItem("포트 연결(O)...", self.action_open_port),
            MenuItem("연결 끊기", self.action_close_port)
        ])
        
        view_menu = Menu("보기(V)", [
            MenuItem("그래프 패널 토글(G)", self.action_toggle_plot)
        ])
        
        help_menu = Menu("도움말(H)", [
            MenuItem("도움말 보기", self.action_show_help)
        ])

        self.menu_bar = MenuBar(menus=[
            file_menu,
            port_menu,
            view_menu,
            help_menu
        ])

        self.terminal = Terminal()
        self._print_banner()

        self.status_bar = HBox(
            Label(" ○ disconnected │ 115200 8N1 │ TX· RX· │ 0B/s ")
        )

        self.root_layout = VBox(
            self.menu_bar,
            self.terminal,
            self.status_bar
        )
        
        self.app.set_root(self.root_layout)

    # --- 메뉴 액션 핸들러 메서드들 ---
    def action_exit(self):
        self.app.exit()

    def action_open_port(self):
        self.terminal.feed("\r\n[System] 포트 설정 대화상자 준비 중...\r\n")

    def action_close_port(self):
        self.terminal.feed("\r\n[System] 포트 연결 해제.\r\n")

    def action_toggle_plot(self):
        self.terminal.feed("\r\n[System] 그래프 패널 토글...\r\n")

    def action_show_help(self):
        self.terminal.feed("\r\n[Help] PaceTerm v0.1.0 - Firmware CLI Terminal\r\n")

    def _print_banner(self):
        logo = [
            "██████╗  █████╗  ██████╗███████╗",
            "██╔══██╗██╔══██╗██╔════╝██╔════╝",
            "██████╔╝███████║██║     █████╗  ",
            "██╔═══╝ ██╔══██║██║     ██╔══╝  ",
            "██║     ██║  ██║╚██████╗███████╗",
            "╚═╝     ╚═╝  ╚═╝ ╚═════╝╚══════╝ -term\r\n"
        ]
        for line in logo:
            self.terminal.feed(line + "\r\n")
            
        self.terminal.feed("펌웨어 CLI 시리얼 터미널 · v0.1.0\r\n")
        self.terminal.feed("STM32 타깃 보드 연결 대기 중...\r\n")
        self.terminal.feed("포트 연결을 위해 메뉴를 선택하거나 단축키를 입력하세요.\r\n\n")
        self.terminal.feed("cli# ")

    def run(self):
        self.app.run()