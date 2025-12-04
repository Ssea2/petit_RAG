import sys
import logging

from PySide6.QtWidgets import (QLineEdit, QPushButton, QApplication, QLabel,QScrollArea,QWidget, QMainWindow, QHBoxLayout, QFrame, QSizePolicy,
    QVBoxLayout)
from PySide6.QtCore import QObject, Signal, QThread, Slot, Qt

from custom_ragV2_choix_similarity import RAG_stack_GUI

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,              # Niveau minimal (DEBUG, INFO, WARNING…)
    format='[%(asctime)s] - [%(levelname)s] - %(message)s'
)

# Exemple de logs


class RAG_stack(QObject):
    word_ready = Signal(str)  # signal pour chaque mot/tronçon
    finished = Signal()

    def __init__(self, text):
        super().__init__()
        self.text = text

    @Slot()
    def run(self):
        stream, files = RAG_stack_GUI(input_query=self.text, history=[], llm="llama3.2:1b") # qwen3:0.6b-q4_K_M
        msg2=""
        for chunk in stream:
            rep = chunk['message']['content']
            msg2=str(rep)
            self.word_ready.emit(msg2)
        for file in files:
            msg2=(file + "\n")
            self.word_ready.emit(msg2)

        
        


class GUI_RAG(QMainWindow):
    

    def __init__(self, parent=None):
        super(GUI_RAG, self).__init__(parent)
        logging.info("démarage de l'application")
        # data 
        self.prompt = ""
        self.chat_style_RAG =  """
                border: 2px solid black;       
                background-color: lightblue;   
                padding: 5px;                  
                border-radius: 5px;            
            """
        self.chat_style_user =  """
                border: 2px solid black;       
                background-color: lightgreen;   
                padding: 5px;                  
                border-radius: 5px;            
            """

        # création de la page
        self.raw_window = QWidget(self)
        self.resize(500,500) 
        self.setCentralWidget(self.raw_window)      

        self.chat_window = QVBoxLayout(self.raw_window)

        self.show_chat()
        self.question_entry()
        
        

    def question_entry(self):
        # creation d'un box pour contenir l'entree es le boutton pour recup le prompt
        self.entry = QHBoxLayout()

        # creation de l'entrée qui a comme text de fons prompt ...
        self.prompt_entry = QLineEdit()
        self.prompt_entry.setPlaceholderText("Prompt...")

        # creation du boutton
        self.start_button = QPushButton()
        self.start_button.clicked.connect(self.get_prompt)
        self.prompt_entry.returnPressed.connect(self.get_prompt)

        # ajout des elements au a la box entry
        self.entry.addWidget(self.prompt_entry) 
        self.entry.addWidget(self.start_button)

        # ajout de la box dans dans le main
        self.chat_window.addLayout(self.entry)
    
    def show_chat(self):
        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_history_window = QWidget()
        self.chat_history_content = QVBoxLayout(self.chat_history_window)
        self.chat_history_content.setSpacing(20)
        self.chat_history_content.setContentsMargins(10, 10, 10, 10)  # left, top, right, bottom
        self.chat_history_content.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinAndMaxSize)

        
        self.chat_scroll_area.setWidget(self.chat_history_window)
        self.chat_window.addWidget(self.chat_scroll_area)
     


    def get_last_answer_id(self):
        last_id = self.chat_history_content.count()
        return last_id
    
    def get_Qlabel(self, id):
        last_Qlabel = self.chat_history_content.itemAt(id).widget()
        return last_Qlabel

    def get_prompt(self):
        logging.info("récupération du prompt")
        self.prompt=self.prompt_entry.text()
        self.prompt_entry.clear()

        msg =QLabel(self.prompt)
        msg.setStyleSheet(self.chat_style_user)
        msg.setWordWrap(True)
        msg.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        msg.setAlignment(Qt.AlignmentFlag.AlignTop)
        

        self.chat_history_content.addWidget(msg)
        
        
        self.RAG_thread()
    
    
    def RAG_thread(self):
        logging.info("démarage du thread => RAG")
        self.thread = QThread(self)
        self.worker = RAG_stack(self.prompt)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        
        self.worker.word_ready.connect(self.RAG_answer)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        logging.info("fin du thread => RAG")
    
    def RAG_answer(self, text):
        
        last_id = self.get_last_answer_id()
        last_id_idx = last_id-1
        if last_id%2==0:
            qlabel = self.get_Qlabel(last_id_idx)
            markdown_text = str(qlabel.text()+text)
            msg = qlabel.setText(markdown_text)
        else:
            msg = QLabel(text)
            msg.setStyleSheet(self.chat_style_RAG)
            msg.setWordWrap(True)
            msg.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            msg.setAlignment(Qt.AlignmentFlag.AlignTop)   

            self.chat_history_content.addWidget(msg) 
        # Défilement automatique vers le bas
        self.chat_scroll_area.verticalScrollBar().setValue(
            self.chat_scroll_area.verticalScrollBar().maximum()
        )

        
        

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = GUI_RAG()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec())