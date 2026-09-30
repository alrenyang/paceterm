import threading
import time
import serial
import serial.tools.list_ports

class SerialPort:
    def __init__(self, on_data_received=None):
        self.serial = serial.Serial()
        self.on_data_received = on_data_received
        self.is_connected = False
        self._thread = None
        self._stop_event = threading.Event()

    @staticmethod
    def list_ports():
        """시스템에 연결된 시리얼 포트 목록을 반환합니다."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def open(self, port, baudrate=115200):
        """지정된 포트와 보드레이트로 시리얼 연결을 엽니다."""
        if self.is_connected:
            self.close()

        try:
            self.serial.port = port
            self.serial.baudrate = baudrate
            self.serial.timeout = 0.1
            self.serial.open()
            
            self.is_connected = True
            self._stop_event.clear()
            
            # 백그라운드 수신 스레드 시작
            self._thread = threading.Thread(target=self._read_loop, daemon=True)
            self._thread.start()
            return True
        except Exception as e:
            print(f"[ERROR] 포트 오픈 실패 ({port}): {e}")
            self.is_connected = False
            return False

    def close(self):
        """시리얼 연결을 닫고 스레드를 종료합니다."""
        if not self.is_connected:
            return

        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)

        try:
            if self.serial.is_open:
                self.serial.close()
        except Exception as e:
            print(f"[ERROR] 포트 닫기 중 에러: {e}")
        
        self.is_connected = False

    def write(self, data: bytes):
        """타깃 보드로 데이터를 전송합니다."""
        if self.is_connected and self.serial.is_open:
            try:
                self.serial.write(data)
            except Exception as e:
                print(f"[ERROR] 데이터 전송 실패: {e}")

    def _read_loop(self):
        """백그라운드에서 데이터를 읽어와 콜백으로 전달하는 스레드 함수"""
        while not self._stop_event.is_set():
            try:
                if self.serial.is_open and self.serial.in_waiting > 0:
                    data = self.serial.read(self.serial.in_waiting)
                    if data and self.on_data_received:
                        self.on_data_received(data)
                else:
                    time.sleep(0.01)
            except Exception as e:
                print(f"[ERROR] 수신 스레드 에러: {e}")
                break
        
        self.is_connected = False