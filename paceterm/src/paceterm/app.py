from retroui import App, Terminal, VBox, HBox, Label, MenuBar, Menu, MenuItem, ComboBox, Button, Dialog
from paceterm.serial_port import SerialPort

class PaceTermApp:
    def __init__(self):
        self.app = App(
            title="PaceTerm - Firmware CLI", 
            size=(120, 36), 
            theme="mono"
        )
        
        self.serial_port = SerialPort(on_data_received=self.handle_serial_data)
        self.baudrate = 115200
        self.current_port_name = "disconnected"

        file_menu = Menu("파일(F)", [
            MenuItem("끝내기(X)", self.action_exit)
        ])
        
        port_menu = Menu("포트(P)", [
            MenuItem("포트 설정(O)...", self.action_open_port_dialog),
            MenuItem("연결 끊기", self.action_close_port)
        ])
        
        help_menu = Menu("도움말(H)", [
            MenuItem("도움말 보기", self.action_show_help)
        ])

        self.menu_bar = MenuBar(menus=[
            file_menu,
            port_menu,
            help_menu
        ])

        self.terminal = Terminal()
        self._print_banner()

        self.status_label = Label(" ○ disconnected │ 115200 8N1 │ TX· RX· │ 0B/s ")
        self.status_bar = HBox(self.status_label)

        self.root_layout = VBox(
            self.menu_bar,
            self.terminal,
            self.status_bar
        )
        
        self.app.set_root(self.root_layout)
        self.active_dialog = None

    def handle_serial_data(self, data: bytes):
        try:
            text = data.decode('utf-8', errors='replace')
            self.terminal.feed(text)
        except Exception:
            pass

    def action_exit(self):
        self.serial_port.close()
        self.app.exit()

    def action_open_port_dialog(self):
        """baram-term 원본 규격에 맞춘 포트 설정 다이얼로그를 엽니다."""
        if self.active_dialog is not None:
            return

        ports = SerialPort.list_ports()
        if not ports:
            ports = ["No Ports Found"]
            
        baudrates = ["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"]

        self.combo_port = ComboBox(items=ports)
        self.combo_baud = ComboBox(items=baudrates)

        port_row = HBox(Label("포트: "), self.combo_port)
        baud_row = HBox(Label("속도: "), self.combo_baud)
        
        def on_confirm():
            selected_port = getattr(self.combo_port, 'current_item', ports[0])
            selected_baud = getattr(self.combo_baud, 'current_item', "115200")
            
            close_my_dialog()
            if selected_port and selected_port != "No Ports Found":
                self._connect_to_port(selected_port, int(selected_baud))
        
        def on_cancel():
            close_my_dialog()

        # 다이얼로그 내부에서 사용할 단일 버튼 박스
        btn_box = HBox(
            Button(" 확인 ", on_click=on_confirm),
            Button(" 취소 ", on_click=on_cancel)
        )
        
        # 본문 레이아웃에 포트, 속도, 버튼을 순서대로 배치
        body_layout = VBox(port_row, baud_row, btn_box)
        
        # retroui의 Dialog 위젯 생성 (중복 버튼 생성을 막기 위해 순수 본문만 전달)
        self.active_dialog = Dialog("포트 설정", body_layout)

        def close_my_dialog():
            if self.active_dialog:
                if self.active_dialog in self.root_layout.children:
                    self.root_layout.children.remove(self.active_dialog)
                self.active_dialog = None
                if hasattr(self.root_layout, 'invalidate'):
                    self.root_layout.invalidate()

        self.root_layout.children.append(self.active_dialog)
        if hasattr(self.root_layout, 'invalidate'):
            self.root_layout.invalidate()

    def _connect_to_port(self, target_port, baudrate):
        self.baudrate = baudrate
        self.terminal.feed(f"\r\n[System] {target_port} ({self.baudrate}) 연결 시도 중...\r\n")
        
        success = self.serial_port.open(target_port, self.baudrate)
        if success:
            self.current_port_name = target_port
            self.status_label.text = f" ● {target_port} │ {self.baudrate} 8N1 │ TX· RX· │ 0B/s "
            self.terminal.feed(f"\r\n[System] {target_port} 연결 성공!\r\n")
        else:
            self.terminal.feed(f"\r\n[ERROR] {target_port} 연결 실패.\r\n")

    def action_close_port(self):
        self.serial_port.close()
        self.current_port_name = "disconnected"
        self.status_label.text = " ○ disconnected │ 115200 8N1 │ TX· RX· │ 0B/s "
        self.terminal.feed("\r\n[System] 포트 연결이 해제되었습니다.\r\n")

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
        self.terminal.feed("포트 설정 메뉴를 클릭하여 통신 포트를 연결하세요.\r\n\n")
        self.terminal.feed("cli# ")

    def run(self):
        self.app.run()