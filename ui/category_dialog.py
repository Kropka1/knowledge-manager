# ui/category_dialog.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QDialogButtonBox, QMessageBox
)


class CategoryDialog(QDialog):
    def __init__(self, parent=None, title="Добавить категорию", name="", description="", is_edit=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Название:"))
        self.name_edit = QLineEdit(name)
        layout.addWidget(self.name_edit)

        layout.addWidget(QLabel("Описание:"))
        self.desc_edit = QTextEdit(description)
        layout.addWidget(self.desc_edit)

        self.button_box = QDialogButtonBox()
        if is_edit:
            self.delete_btn = self.button_box.addButton(
                "Удалить", QDialogButtonBox.ButtonRole.DestructiveRole
            )
            self.delete_btn.clicked.connect(self.confirm_delete)
        self.button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.desc_edit.setAcceptRichText(False)
        self.desc_edit.setPlaceholderText("Введите описание...")
        self.desc_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.desc_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.desc_edit.textChanged.connect(self.adjust_height)

        layout.addWidget(self.button_box)

    def adjust_height(self):
        doc_height = self.desc_edit.document().size().height()
        margin = 10
        self.desc_edit.setFixedHeight(min(int(doc_height) + margin, 300))

    def get_data(self):
        return {
            "name": self.name_edit.text().strip(),
            "description": self.desc_edit.toPlainText().strip()
        }

    def confirm_delete(self):
        confirm = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить эту категорию? Все подкатегории также будут удалены!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.done(2)
