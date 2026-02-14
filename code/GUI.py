import sys
import logging
import markdown
import chromadb

from chromadb.utils.embedding_functions import OllamaEmbeddingFunction


from PySide6.QtWidgets import (QLineEdit, QPushButton, QApplication, QLabel,QScrollArea,QWidget, QMainWindow, QHBoxLayout, QFileDialog, QSizePolicy, QDialog,
    QCheckBox, QDialogButtonBox, QVBoxLayout, QTextEdit, QMessageBox)
from PySide6.QtCore import QObject, Signal, QThread, Slot, Qt, QUrl

from RAG_tools import RAG_Answer, RAG_Upload, RAG_Delete

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,              # Niveau minimal (DEBUG, INFO, WARNING…)
    format='[%(asctime)s] - [%(levelname)s] - %(message)s'
)

# Exemple de logs
from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel
from PySide6.QtCore import Qt, QPoint

class NotificationOverlay(QWidget):
    def __init__(self, parent):
        super().__init__(parent) # Parent est ta MainWindow
        
        # Style pour le look "Overlay"
        self.setStyleSheet("""
            background-color: rgba(40, 40, 40, 220); 
            border: 1px solid #555;
            border-radius: 8px;
        """)
        
        layout = QVBoxLayout(self)
        self.label = QLabel("Action en cours...")
        self.label.setStyleSheet("color: white; border: none;")
        self.progress = QProgressBar()
        self.progress.setFixedHeight(15)
        
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        
        self.setFixedSize(200, 70)
        
        # On le place en haut à gauche avec une petite marge
        self.move(10, 10) 
        self.hide() # Caché par défaut

    def update_progress(self, val):
        self.progress.setValue(val)
        self.show()
        if val >= 100: self.hide()

class RAG_stack(QObject):
    word_ready = Signal(str)  # signal pour chaque mot/tronçon
    finished = Signal()

    def __init__(self, text, db):
        super().__init__()
        self.text = text
        self.rag = RAG_Answer(db, llm="qwen3:0.6b-q4_K_M", top_n_result=30)

    def run(self):
        stream, files = self.rag.rag_stack(self.text)
        print(files)
        for chunk in stream:
            rep = chunk['message']['content']
            msg2=str(rep)
            self.word_ready.emit(msg2)
        msg2 = """
         <p><h4> **SOURCE : **<h4></p>
        """
        self.word_ready.emit(msg2)
        for file in set(files):
            url = QUrl.fromLocalFile(file).toString()
            #print(url)
            html = f'<a href="{url}" style="text-decoration:none; color:blue;">{url}</a>' #f'<p><a href="{url}">{url}</a><p>'
            #print(file)
            msg2=html
            self.word_ready.emit(msg2)
        self.finished.emit()

class Upload_data(QObject):
    finished = Signal()
    progress = Signal(int)

    def __init__(self, db, embeding_model, paths):
        super().__init__()
        #print("TAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        self.paths = paths
        self.rag_upload = RAG_Upload(db=db, embeding_model=embeding_model)

    def run(self):
        self.progress.emit(0)
        self.rag_upload.get_document(self.paths)
        self.progress.emit(25)
        self.rag_upload.split_document()
        self.progress.emit(50)
        self.rag_upload.fill_db()
        self.progress.emit(75)
        self.finished.emit()
        self.progress.emit(100)


class Files_list2remove(QDialog):
    def __init__(self, items, title="éléments à supprimer", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        
        # 1. Mise en page principale
        self.layout = QVBoxLayout(self)
        self.checkboxes = []

        # 2. Création des cases à cocher à partir de la liste
        for item in items:
            cb = QCheckBox(item)
            self.layout.addWidget(cb)
            self.checkboxes.append(cb)

        # 3. Ajout des boutons OK / Annuler
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttons.accepted.connect(self.accept) # Ferme et renvoie True
        self.buttons.rejected.connect(self.reject) # Ferme et renvoie False
        self.layout.addWidget(self.buttons)

    def get_selected(self):
        """Retourne la liste des textes des cases cochées."""
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]
    
    def get_tokeep(self):
        return [cb.text() for cb in self.checkboxes if not cb.isChecked()]


class GUI_RAG(QMainWindow):
    

    def __init__(self, db, embeding_model, parent=None):
        super(GUI_RAG, self).__init__(parent)
        logging.info("démarage de l'application")
        # data 
        self.prompt = ""
        self.answertmp = ""
        self.chat_style_RAG =  """
                border: 2px solid black;       
                background-color: lightblue;                     
                border-radius: 5px;     
                padding: 5px; 
                margin: 0px;    
            """
        self.chat_style_user =  """
                border: 2px solid black;       
                background-color: lightgreen;                    
                border-radius: 5px;            
                padding: 5px; 
                margin: 0px; 
            """
        self.db = db
        self.embeding_model = embeding_model


        # création de la page
        self.raw_window = QWidget(self)
        self.resize(500,500) 
        self.setCentralWidget(self.raw_window)      

        self.chat_window = QVBoxLayout(self.raw_window)

        self.show_chat()
        self.question_entry()     

        # initialisation de la bar 
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False) 
        self.statusBar().addPermanentWidget(self.progress_bar)



        

    def question_entry(self):
        # creation d'un box pour contenir l'entree es le boutton pour recup le prompt
        self.entry = QHBoxLayout()

        # creation de l'entrée qui a comme text de fons prompt ...
        self.prompt_entry = QTextEdit()
        self.prompt_entry.setPlaceholderText("Prompt...")
        self.prompt_entry.setLineWrapMode(QTextEdit.WidgetWidth)
        self.prompt_entry.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        # creation du bouton envoie du prompt
        self.start_buton = QPushButton("=>")
        self.start_buton.clicked.connect(self.get_prompt)
        #self.prompt_entry.returnPressed.connect(self.get_prompt)

        # creation du bouton upload data
        self.upload_buton = QPushButton("+")
        self.upload_buton.clicked.connect(self.link_data)

        # bouton pour supprimer des element de la bdd 
        self.remove_buton = QPushButton("-")
        self.remove_buton.clicked.connect(self.get_data2remove)
        

        # ajout des elements au a la box entry
        self.entry.addWidget(self.prompt_entry) 
        self.entry.addWidget(self.start_buton)
        self.entry.addWidget(self.upload_buton)
        self.entry.addWidget(self.remove_buton)

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
        self.prompt=self.prompt_entry.toPlainText()
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
        self.worker = RAG_stack(self.prompt, self.db)
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
            text = str(self.answertmp+text)
            self.answertmp=text
            html = markdown.markdown(text)
            msg = qlabel.setText(html)
        else:
            self.answertmp=""
            html = markdown.markdown(text)
            msg = QLabel(html)
            msg.setStyleSheet(self.chat_style_RAG)
            msg.setWordWrap(True)
            msg.setOpenExternalLinks(True) 
            
            msg.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            msg.setAlignment(Qt.AlignmentFlag.AlignTop)   
            msg.setTextFormat(Qt.TextFormat.RichText)  # Important pour le HTML
            msg.setOpenExternalLinks(True) 

            self.chat_history_content.addWidget(msg) 
        # Défilement automatique vers le bas
        self.chat_scroll_area.verticalScrollBar().setValue(
            self.chat_scroll_area.verticalScrollBar().maximum()
        )

    def link_data(self):
        files_path, _ = QFileDialog.getOpenFileNames(
            self,
            "Sélectionner les fichiers à importer",
            "",
            "Tous les fichiers (*.*)"
        )
        logging.info("démarage du thread => UPLOAD")
        #print("path", files_path)
        # Dans ton __init__ ou ta fonction de lancement
        # Affichage de la barre
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.statusBar().showMessage("Importation en cours...")


        self.thread_upload = QThread(self)
        self.worker_upload = Upload_data(self.db, self.embeding_model , files_path)
        self.worker_upload.moveToThread(self.thread_upload)
        self.worker_upload.progress.connect(self.progress_bar.setValue)

        self.thread_upload.started.connect(self.worker_upload.run)
        
        self.worker_upload.finished.connect(self.thread_upload.quit)
        self.worker_upload.finished.connect(self.worker_upload.deleteLater)
        self.thread_upload.finished.connect(self.thread_upload.deleteLater)
        self.thread_upload.finished.connect(lambda: self.statusBar().showMessage("Importation finit"))
        self.thread_upload.start()

        logging.info("fin du thread => UPLOAD")
        
    def get_data2remove(self):
        app = QApplication.instance() or QApplication(sys.argv)
        
        deletetools = RAG_Delete(self.db)
        ma_liste = deletetools.get_files_saved()

        # Initialisation et affichage de la pop-up
        if len(ma_liste) >=1: 
            dialog = Files_list2remove(ma_liste)
            
            if dialog.exec() == QDialog.Accepted:
                selection = dialog.get_selected()
                tokeep = dialog.get_tokeep()
                print("to keep", tokeep)
                print(f"Éléments cochés : {selection}")
                deletetools.remove_data(tokeep)    
            else:
                print("Action annulée")
                return []
        else:
            QMessageBox.warning(None, "Attention", "BDD vide")

if __name__ == '__main__':
    embm = "nomic-embed-text"
    embedding_model = OllamaEmbeddingFunction(
        model_name=embm,     # ou "mxbai‑embed‑large", ou "chroma/all‑minilm‑l6‑v2‑f32"
        url="http://localhost:11434/api/embeddings",)

    client = chromadb.PersistentClient(path="bdd/rag") # robia/isa88 robia2(filtered robia)
    chroma_collection = client.get_or_create_collection("rag",embedding_function=embedding_model,configuration={
            "hnsw": {
                "space": "cosine",
            }
        })
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = GUI_RAG(db=chroma_collection, embeding_model=embm)
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec())