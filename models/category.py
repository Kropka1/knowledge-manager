# models/category.py
from db.database import get_connection


class Category:
    def __init__(self, id=None, name="", description="", parent_id=None):
        self.id = id
        self.name = name
        self.description = description
        self.parent_id = parent_id

    @staticmethod
    def create(name, description, parent_id=None):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO categories (name, description, parent_id) VALUES (?, ?, ?)",
                (name, description, parent_id)
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_by_id(category_id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description, parent_id FROM categories WHERE id = ?", (category_id,))
            row = cursor.fetchone()
            if row:
                return Category(*row)
            return None

    @staticmethod
    def update(category_id, name, description):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE categories SET name = ?, description = ? WHERE id = ?",
                (name, description, category_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(category_id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE id = ? OR parent_id = ?",
                           (category_id, category_id))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def get_children(parent_id=None):
        with get_connection() as conn:
            cursor = conn.cursor()

            if parent_id is None:
                cursor.execute("""
                    SELECT id, name, description, parent_id 
                    FROM categories 
                    WHERE parent_id IS NULL
                """)
            else:
                cursor.execute("""
                    SELECT id, name, description, parent_id 
                    FROM categories 
                    WHERE parent_id = ?
                """, (parent_id,))

            rows = cursor.fetchall()
            return [Category(*row) for row in rows]

    @staticmethod
    def get_all():
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description, parent_id FROM categories")
            return [Category(*row) for row in cursor.fetchall()]


if __name__ == "__main__":
    print(Category.get_all())
