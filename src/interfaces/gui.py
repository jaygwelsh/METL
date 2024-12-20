# src/interfaces/gui.py

import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QMessageBox,
    QHBoxLayout, QLineEdit, QDialog, QTableWidget, QTableWidgetItem, QMenuBar, QMenu, QAction, QStatusBar
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from core.metadata import MetadataEngine
from utils.auth import authenticate_user
from core.ledger import Ledger
from utils.logger import get_logger

logger = get_logger(__name__)

class LedgerDialog(QDialog):
    def __init__(self, parent, rows):
        super().__init__(parent)
        self.setWindowTitle("Ledger Transactions")
        self.resize(600, 400)

        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Data", "Timestamp"])
        self.table.setRowCount(len(rows))
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)

        for i, r in enumerate(rows):
            id_item = QTableWidgetItem(str(r[0]))
            data_item = QTableWidgetItem(str(r[1]))
            ts_item = QTableWidgetItem(str(r[2]))
            self.table.setItem(i, 0, id_item)
            self.table.setItem(i, 1, data_item)
            self.table.setItem(i, 2, ts_item)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        self.setLayout(layout)

class METLGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.role = "guest"
        # Initialize a ledger if you want GUI logging as well
        self.ledger = Ledger({"db_path": "ledger.db"})
        self.engine = MetadataEngine(ledger=self.ledger)
        self.engine.load_private_key()
        self.engine.load_public_key()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("METL")
        self.resize(600, 300)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        token_input_layout = QHBoxLayout()

        self.token_label = QLabel("Token:", self)
        self.token_input = QLineEdit(self)
        self.token_button = QPushButton("Login", self)
        self.token_button.setIcon(QIcon())  # Remove icons if not available
        self.token_button.clicked.connect(self.login_user)

        token_input_layout.addWidget(self.token_label)
        token_input_layout.addWidget(self.token_input)
        token_input_layout.addWidget(self.token_button)

        main_layout.addLayout(token_input_layout)

        self.label = QLabel("Select a file to embed or verify metadata:", self)
        main_layout.addWidget(self.label)

        self.btn_embed = QPushButton("Embed Metadata")
        self.btn_embed.setIcon(QIcon())
        self.btn_embed.clicked.connect(self.select_file_for_embedding)
        main_layout.addWidget(self.btn_embed)

        self.btn_verify = QPushButton("Verify Metadata")
        self.btn_verify.setIcon(QIcon())
        self.btn_verify.clicked.connect(self.select_file_for_verification)
        main_layout.addWidget(self.btn_verify)

        self.btn_ledger = QPushButton("Show Ledger")
        self.btn_ledger.setIcon(QIcon())
        self.btn_ledger.setEnabled(False)
        self.btn_ledger.clicked.connect(self.show_ledger)
        main_layout.addWidget(self.btn_ledger)

        central_widget.setLayout(main_layout)

        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = QMenu("File", self)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        menu_bar.addMenu(file_menu)

        help_menu = QMenu("Help", self)
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        menu_bar.addMenu(help_menu)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def login_user(self):
        token = self.token_input.text().strip()
        if not token:
            QMessageBox.warning(self, "Warning", "Please enter a token.")
            return
        user_info = authenticate_user(token)
        self.role = user_info.get("role", "guest")
        QMessageBox.information(self, "Login", f"Logged in as {self.role}")
        self.status_bar.showMessage(f"Logged in as {self.role}")

        if self.role == "admin":
            self.btn_ledger.setEnabled(True)
        else:
            self.btn_ledger.setEnabled(False)

    def select_file_for_embedding(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Embed Metadata")
        if file_path:
            self.embed_metadata(file_path)

    def embed_metadata(self, file_path):
        try:
            with open(file_path, "r", errors='ignore') as f:
                content = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unable to read file:\n{e}")
            return

        suggestions = self.engine.suggest_metadata(content)
        signed_meta = self.engine.embed_metadata(file_path, suggestions, self.engine._private_key)
        if signed_meta:
            QMessageBox.information(self, "Success", "Metadata embedded successfully (sidecar).")
            self.status_bar.showMessage("Metadata embedded successfully.")
        else:
            QMessageBox.critical(self, "Error", "Failed to embed metadata.")
            self.status_bar.showMessage("Embedding failed.")

    def select_file_for_verification(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Verify Metadata")
        if file_path:
            self.verify_metadata(file_path)

    def verify_metadata(self, file_path):
        verified = self.engine.verify_metadata(file_path, self.engine._public_key)
        if verified:
            QMessageBox.information(self, "Verification", "Metadata verified successfully.")
            self.status_bar.showMessage("Metadata verified successfully.")
        else:
            QMessageBox.critical(self, "Verification Failed", "Metadata verification failed.")
            self.status_bar.showMessage("Metadata verification failed.")

    def show_ledger(self):
        if self.role != "admin":
            QMessageBox.warning(self, "Access Denied", "You do not have permission to view the ledger.")
            return

        conn = sqlite3.connect('ledger.db')
        c = conn.cursor()
        c.execute("SELECT id, data, timestamp FROM transactions ORDER BY id ASC")
        rows = c.fetchall()
        conn.close()

        if not rows:
            QMessageBox.information(self, "Ledger", "No transactions recorded.")
            return

        dlg = LedgerDialog(self, rows)
        dlg.exec_()
        self.status_bar.showMessage("Ledger viewed.")

    def show_about(self):
        QMessageBox.information(self, "About METL",
                                "METL - Metadata Embedding and Tracking Ledger\n\n"
                                "A tool for embedding, verifying, and managing metadata.\n"
                                "Role-Based Access Control for ledger viewing and actions.\n"
                                "©2024 Your Name or Organization")

def main():
    app = QApplication(sys.argv)
    gui = METLGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
