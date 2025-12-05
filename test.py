from PySide6.QtWidgets import QApplication, QTextBrowser, QLabel

app = QApplication([])

browser = QLabel()
browser.setText("""
<p>Texte principal</p>
<p><a href="https://www.openai.com">OpenAI</a></p>
<p><a href="https://www.python.org">Python</a></p>
""")
browser.setOpenExternalLinks(True)
browser.show()

app.exec()
