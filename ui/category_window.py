# ui/category_window.py
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QInputDialog, QMessageBox, QHBoxLayout, QDialog
)
from models.category import Category
from ui.category_dialog import CategoryDialog


class CategoryWindow(QMainWindow):
    def __init__(self, category_id, parent_window):
        super().__init__()
        self.category_id = category_id
        self.parent_window = parent_window
        self.category = Category.get_by_id(category_id)

        self.setWindowTitle(f"Учет знаний - {self.category.name}")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.setup_ui()
        self.load_subcategories()

    def setup_ui(self):

        # Заголовок с информацией о категории
        self.title_label = QLabel(f"Категория: {self.category.name}")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(self.title_label)

        self.desc_label = QLabel(f"Описание: {self.category.description or ''}")
        self.layout.addWidget(self.desc_label)

        # Дерево подкатегорий
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Подкатегория", "Описание"])
        self.tree.setColumnWidth(0, 300)
        self.layout.addWidget(self.tree)

        # Кнопки
        self.buttons_layout = QHBoxLayout()

        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)
        self.buttons_layout.addWidget(self.back_button)

        self.add_button = QPushButton("Добавить подкатегорию")
        self.add_button.clicked.connect(self.add_subcategory)
        self.buttons_layout.addWidget(self.add_button)

        self.open_button = QPushButton("Открыть")
        self.open_button.clicked.connect(self.open_selected)
        self.buttons_layout.addWidget(self.open_button)

        self.layout.addLayout(self.buttons_layout)

        self.tree.itemDoubleClicked.connect(self.open_selected)

        btn_layout = QHBoxLayout()

        self.back_btn = QPushButton("Назад")
        self.add_btn = QPushButton("Добавить")
        self.edit_btn = QPushButton("Редактировать")
        self.delete_btn = QPushButton("Удалить")

        self.back_btn.clicked.connect(self.go_back)
        self.add_btn.clicked.connect(self.add_subcategory)
        self.edit_btn.clicked.connect(self.edit_subcategory)
        self.delete_btn.clicked.connect(self.delete_subcategory)

        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        self.buttons_layout.addLayout(btn_layout)
        self.delete_btn.setIcon(QIcon.fromTheme("edit-delete"))
        self.edit_btn.setIcon(QIcon.fromTheme("document-edit"))

    def load_subcategories(self):
        self.tree.clear()
        subcategories = Category.get_children(self.category_id)

        for category in subcategories:
            item = QTreeWidgetItem(self.tree)
            item.setText(0, category.name)
            item.setText(1, category.description or "")
            item.setData(0, 100, category.id)

    # Заменяем метод add_subcategory
    def add_subcategory(self):
        dialog = CategoryDialog(self, "Добавить подкатегорию")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data["name"]:
                QMessageBox.warning(self, "Ошибка", "Название подкатегории обязательно")
                return

            Category.create(data["name"], data["description"], self.category_id)
            self.load_subcategories()

    def edit_subcategory(self):
        selected = self.tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите подкатегорию для редактирования")
            return

        category_id = selected.data(0, 100)
        category = Category.get_by_id(category_id)

        dialog = CategoryDialog(
            self,
            f"Редактирование: {category.name}",
            category.name,
            category.description,
            is_edit=True
        )

        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data["name"]:
                QMessageBox.warning(self, "Ошибка", "Название подкатегории обязательно")
                return

            Category.update(category_id, data["name"], data["description"])
            self.load_subcategories()

        elif result == 2:  # Код для удаления
            Category.delete(category_id)
            self.load_subcategories()

    def delete_subcategory(self):
        selected = self.tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите подкатегорию для удаления")
            return

        category_id = selected.data(0, 100)
        category = Category.get_by_id(category_id)

        confirm = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить подкатегорию '{category.name}'? Все вложенные подкатегории также будут удалены!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            if Category.delete(category_id):
                self.load_subcategories()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить подкатегорию")

    def open_selected(self):
        selected = self.tree.currentItem()
        if not selected:
            return

        category_id = selected.data(0, 100)
        self.new_window = CategoryWindow(category_id, self.parent_window)
        self.new_window.show()
        self.hide()

    def go_back(self):
        self.parent_window.show_main_window()
        self.close()
