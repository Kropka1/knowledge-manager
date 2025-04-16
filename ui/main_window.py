from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QInputDialog, QMessageBox, QDialog, QHBoxLayout
)
from models.category import Category
from ui.category_window import CategoryWindow
from ui.category_dialog import CategoryDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Учет знаний - Главная")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.setup_ui()
        self.load_categories()

    def setup_ui(self):
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Категория", "Описание"])
        self.tree.setColumnWidth(0, 300)
        self.layout.addWidget(self.tree)

        self.add_button = QPushButton("Добавить категорию")
        self.add_button.clicked.connect(self.add_category)
        self.layout.addWidget(self.add_button)

        self.open_button = QPushButton("Открыть")
        self.open_button.clicked.connect(self.open_selected_category)
        self.layout.addWidget(self.open_button)

        self.tree.itemDoubleClicked.connect(self.open_selected_category)
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("Добавить")
        self.edit_btn = QPushButton("Редактировать")
        self.delete_btn = QPushButton("Удалить")

        self.add_btn.clicked.connect(self.add_category)
        self.edit_btn.clicked.connect(self.edit_category)
        self.delete_btn.clicked.connect(self.delete_category)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        self.layout.addLayout(btn_layout)
        self.delete_btn.setIcon(QIcon.fromTheme("edit-delete"))
        self.edit_btn.setIcon(QIcon.fromTheme("document-edit"))

        self.tree_view_btn = QPushButton("Посмотреть схему")
        self.tree_view_btn.setIcon(QIcon.fromTheme("view-tree"))
        self.tree_view_btn.clicked.connect(self.show_tree_view)

        btn_layout.addWidget(self.tree_view_btn)

    def show_tree_view(self):
        selected = self.tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите категорию")
            return

        category_id = selected.data(0, 100)
        from ui.tree_view_window import TreeViewWindow
        self.tree_window = TreeViewWindow(category_id, self)
        self.tree_window.show()

    def edit_category(self):
        selected = self.tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите категорию для редактирования")
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
                QMessageBox.warning(self, "Ошибка", "Название категории обязательно")
                return

            Category.update(category_id, data["name"], data["description"])
            self.load_categories()

        elif result == 2:  # Код для удаления
            Category.delete(category_id)
            self.load_categories()

    def delete_category(self):
        selected = self.tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите категорию для удаления")
            return

        category_id = selected.data(0, 100)
        category = Category.get_by_id(category_id)

        confirm = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить категорию '{category.name}'? Все подкатегории также будут удалены!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            if Category.delete(category_id):
                self.load_categories()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить категорию")

    def load_categories(self):
        self.tree.clear()
        categories = Category.get_children()

        for category in categories:
            item = QTreeWidgetItem(self.tree)
            item.setText(0, category.name)
            item.setText(1, category.description or "")
            item.setData(0, 100, category.id)

    def add_category(self):
        dialog = CategoryDialog(self, "Добавить категорию")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data["name"]:
                QMessageBox.warning(self, "Ошибка", "Название категории обязательно")
                return

            Category.create(data["name"], data["description"])
            self.load_categories()

    def open_selected_category(self):
        selected = self.tree.currentItem()
        if not selected:
            return

        category_id = selected.data(0, 100)
        self.category_window = CategoryWindow(category_id, self)
        self.category_window.show()
        self.hide()

    def show_main_window(self):
        self.show()
        self.load_categories()
