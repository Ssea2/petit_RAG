import sys
import shutil
import os
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                             QVBoxLayout, QWidget, QFileDialog, QMessageBox)

class ImportWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Importateur de Fichiers")
        self.resize(300, 150)

        # Configuration du dossier de destination
        self.dossier_destination = Path("./imports")
        self.dossier_destination.mkdir(exist_ok=True) # Crée le dossier s'il n'existe pas

        # Interface
        self.bouton_import = QPushButton("Importer des fichiers")
        self.bouton_import.clicked.connect(self.importer_fichiers)

        layout = QVBoxLayout()
        layout.addWidget(self.bouton_import)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def importer_fichiers(self):
        # 1. Ouvrir l'explorateur pour choisir des fichiers
        fichiers, _ = QFileDialog.getOpenFileNames(
            self,
            "Sélectionner les fichiers à importer",
            "",
            "Tous les fichiers (*.*)"
        )

        if fichiers:
            try:
                for f in fichiers:
                    chemin_source = Path(f)
                    # 2. Copier chaque fichier vers la destination
                    shutil.copy(chemin_source, self.dossier_destination / chemin_source.name)
                
                QMessageBox.information(self, "Succès", f"{len(fichiers)} fichier(s) importé(s) avec succès !")
            
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'import : {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImportWindow()
    window.show()
    sys.exit(app.exec())