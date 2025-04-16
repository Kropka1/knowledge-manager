from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QMessageBox
)
from PyQt6.QtGui import QIcon
from models.category import Category
from utils.tree_utils import build_category_tree


class TreeViewWindow(QMainWindow):
    def __init__(self, category_id, parent=None):
        super().__init__(parent)
        self.category_id = category_id
        self.category = Category.get_by_id(category_id)

        self.setWindowTitle(f"Tree View: {self.category.name}")
        self.setGeometry(200, 200, 600, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.setup_ui()
        self.load_full_tree()

    def setup_ui(self):
        self.title_label = QLabel(f"Full tree structure for: {self.category.name}")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(self.title_label)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Category", "Description"])
        self.tree_widget.setColumnWidth(0, 300)
        self.layout.addWidget(self.tree_widget)

        self.close_btn = QPushButton("Close")
        self.close_btn.setIcon(QIcon.fromTheme("window-close"))
        self.close_btn.clicked.connect(self.close)
        self.layout.addWidget(self.close_btn)

        self.export_btn = QPushButton("Экспорт")
        self.export_btn.setIcon(QIcon.fromTheme("document-save"))
        self.export_btn.clicked.connect(self.export_tree)
        self.layout.addWidget(self.export_btn)

    def export_tree(self):
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Tree As",
            f"{self.category.name}_tree.txt",
            "Text Files (*.txt)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Knowledge Tree: {self.category.name}\n")
                    f.write("=" * 50 + "\n\n")
                    self._write_tree_to_file(f, self.category_id)
                QMessageBox.information(self, "Success", "Tree exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")

    def _write_tree_to_file(self, file, category_id, level=0):
        category = Category.get_by_id(category_id)
        indent = "    " * level
        file.write(f"{indent}└── {category.name}\n")
        if category.description:
            file.write(f"{indent}    Description: {category.description}\n")

        for child in Category.get_children(category_id):
            self._write_tree_to_file(file, child.id, level + 1)

    def load_full_tree(self):
        self.tree_widget.clear()

        root_item = QTreeWidgetItem(self.tree_widget)
        root_item.setText(0, self.category.name)
        root_item.setText(1, self.category.description or "")

        self._add_children_to_tree(root_item, self.category_id)

        self.tree_widget.expandAll()

    def _add_children_to_tree(self, parent_item, category_id):
        children = Category.get_children(category_id)
        for child in children:
            child_item = QTreeWidgetItem(parent_item)
            child_item.setText(0, child.name)
            child_item.setText(1, child.description or "")
            self._add_children_to_tree(child_item, child.id)
