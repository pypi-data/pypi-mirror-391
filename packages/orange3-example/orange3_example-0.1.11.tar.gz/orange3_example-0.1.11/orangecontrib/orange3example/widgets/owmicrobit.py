# -*- coding: utf-8 -*-
from Orange.widgets.widget import OWWidget, Input
import Orange.data
from Orange.data import StringVariable

from AnyQt.QtWidgets import QTextEdit, QPushButton, QComboBox, QLabel, QHBoxLayout, QWidget, QVBoxLayout, QCheckBox
from orangecontrib.orange3example.utils import microbit


class OWMicrobit(OWWidget):
    name = "Microbit Communicator"
    description = "Send data to Microbit through serial port"
    icon = "../icons/machine-learning-03-svgrepo-com.svg"
    priority = 20

    class Inputs:
        text_data = Input("Text Input", Orange.data.Table)

    def __init__(self):
        super().__init__()

        self.text_data = None

        # 포트 선택 UI
        port_layout = QHBoxLayout()
        port_widget = QWidget()
        port_widget.setLayout(port_layout)

        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        port_layout.addWidget(self.port_combo)

        self.refresh_button = QPushButton("새로고침")
        self.refresh_button.clicked.connect(self.refresh_ports)
        port_layout.addWidget(self.refresh_button)

        self.connect_button = QPushButton("연결")
        self.connect_button.clicked.connect(self.connect_to_microbit)
        port_layout.addWidget(self.connect_button)

        self.status_label = QLabel("연결되지 않음")
        port_layout.addWidget(self.status_label)

        self.controlArea.layout().addWidget(port_widget)

        # 전송 텍스트 입력
        self.send_box = QTextEdit()
        self.send_box.setPlaceholderText("마이크로비트로 보낼 텍스트를 입력하세요")
        self.send_box.setMaximumHeight(80)
        self.controlArea.layout().addWidget(self.send_box)

        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        
        self.send_button = QPushButton("전송")
        self.send_button.clicked.connect(self.send_to_microbit)
        button_layout.addWidget(self.send_button)
        
        self.auto_send_checkbox = QCheckBox("자동 전송")
        self.auto_send_checkbox.setChecked(True)
        button_layout.addWidget(self.auto_send_checkbox)
        
        self.controlArea.layout().addLayout(button_layout)

        # 로그 출력창
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(100)
        self.controlArea.layout().addWidget(self.log_box)

        # 초기 포트 목록 로드
        self.refresh_ports()

    def log(self, text):
        self.log_box.append(text)

    def refresh_ports(self):
        self.port_combo.clear()
        self.log("포트 새로고침 중...")
        if microbit:
            try:
                ports = microbit.list_ports()
                if ports:
                    self.port_combo.addItems(ports)
                    self.log(f"사용 가능한 포트: {', '.join(ports)}")
                else:
                    self.log("사용 가능한 포트가 없습니다.")
            except Exception as e:
                self.log(f"포트 검색 실패: {str(e)}")
        else:
            self.log("microbit 모듈이 로드되지 않았습니다.")

    def connect_to_microbit(self):
        if not microbit:
            self.status_label.setText("microbit 모듈 없음")
            self.log("microbit 모듈이 없습니다.")
            return

        port = self.port_combo.currentText()
        try:
            microbit.connect(port)
            self.status_label.setText(f"연결됨 ({port})")
            self.log(f"{port} 포트에 연결되었습니다.")
                
        except Exception as e:
            self.status_label.setText(f"연결 실패")
            self.log(f"연결 실패: {str(e)}")

    @Inputs.text_data
    def set_text_data(self, data):
        """[수정] 입력 텍스트 처리 로직 개선"""
        if data is None:
            self.log("입력 데이터가 None입니다.")
            self.text_data = None
            if not self.auto_send_checkbox.isChecked():
                self.send_box.clear()
            return
            
        if not isinstance(data, Orange.data.Table):
            self.log(f"예상하지 못한 데이터 타입: {type(data)}")
            return
            
        self.text_data = data
        text = ""
        
        try:
            # [수정] 모든 문자열 변수(속성, 클래스, 메타)에서 텍스트 추출
            all_vars = data.domain.variables + data.domain.metas
            string_vars = [var for var in all_vars if isinstance(var, StringVariable)]
            
            if string_vars:
                text_content = []
                for row in data:
                    row_texts = []
                    for var in string_vars:
                        value = str(row[var]) 
                        if value != "?" and value: # '?' 또는 빈 값 제외
                            row_texts.append(value)
                    if row_texts:
                        text_content.append(" ".join(row_texts))
                        
                if text_content:
                    text = "\n".join(text_content)
                else:
                    self.log("문자열 변수는 있으나 유효한 텍스트가 없습니다.")
            else:
                self.log("입력 테이블에 문자열(String) 변수가 없습니다.")

            if text:
                self.log(f"입력 데이터를 수신했습니다: {text}")
                if self.auto_send_checkbox.isChecked():
                    self.send_text_to_microbit(text)
                else:
                    self.send_box.setPlainText(text)
            else:
                self.log("입력에서 추출된 텍스트가 없습니다.")
                if not self.auto_send_checkbox.isChecked():
                    self.send_box.clear()
                    
        except Exception as e:
            self.log(f"입력 텍스트 추출 실패: {e}")

    def send_text_to_microbit(self, text: str):
        """마이크로비트로 텍스트 전송 (단방향)"""
        if not text:
            self.log("전송할 텍스트가 없습니다.")
            return

        if not microbit:
            self.log("microbit 모듈이 없습니다.")
            return

        if not microbit.is_connected():
            self.log("포트가 연결되지 않았습니다.")
            return

        try:
            # 비-블로킹 전송만 사용
            if hasattr(microbit, 'send_text'):
                success = microbit.send_text(text)
                if success:
                    self.log(f"전송됨: {text}")
                else:
                    self.log("전송 실패")
            else:
                self.log("오류: 'send_text' 함수가 microbit 모듈에 없습니다.")
                
        except Exception as e:
            self.log(f"전송 중 오류 발생: {str(e)}")

    def send_to_microbit(self):
        text = self.send_box.toPlainText().strip()
        self.send_text_to_microbit(text)