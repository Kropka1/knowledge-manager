from models.category import Category
from typing import List, Dict, Optional


def build_category_tree(parent_id: Optional[int] = None, level: int = 0, max_level: Optional[int] = None) -> List[Dict]:
    if max_level is not None and level >= max_level:
        return []

    categories = Category.get_children(parent_id)
    result = []

    for category in categories:
        category_data = {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'parent_id': category.parent_id,
            'level': level,
            'children': build_category_tree(category.id, level + 1, max_level)
        }
        result.append(category_data)

    return result


def get_category_path(category_id: int, include_self: bool = True) -> List[Category]:
    path = []
    current = Category.get_by_id(category_id)

    if not current:
        return path

    if include_self:
        path.append(current)

    while current.parent_id is not None:
        current = Category.get_by_id(current.parent_id)
        if current:
            path.insert(0, current)

    return path


def get_all_descendants(category_id: int) -> List[Category]:
    descendants = []
    children = Category.get_children(category_id)

    for child in children:
        descendants.append(child)
        descendants.extend(get_all_descendants(child.id))

    return descendants


def print_tree_to_console(category_id: Optional[int] = None, indent: int = 0) -> None:
    categories = Category.get_children(category_id)

    for category in categories:
        print(' ' * indent + f"├── {category.name} (ID: {category.id})")
        if category.description:
            print(' ' * (indent + 4) + f"Description: {category.description}")
        print_tree_to_console(category.id, indent + 4)


def calculate_tree_depth(category_id: int) -> int:
    children = Category.get_children(category_id)
    if not children:
        return 1
    return 1 + max(calculate_tree_depth(child.id) for child in children)


def count_tree_nodes(category_id: int) -> int:
    count = 1
    for child in Category.get_children(category_id):
        count += count_tree_nodes(child.id)
    return count


def find_category_by_name(name: str, parent_id: Optional[int] = None) -> Optional[Category]:
    categories = Category.get_children(parent_id)
    for category in categories:
        if category.name.lower() == name.lower():
            return category
        # Search in children
        found = find_category_by_name(name, category.id)
        if found:
            return found
    return None


def is_ancestor(category_id: int, potential_ancestor_id: int) -> bool:
    if category_id == potential_ancestor_id:
        return True

    category = Category.get_by_id(category_id)
    if not category or not category.parent_id:
        return False

    if category.parent_id == potential_ancestor_id:
        return True

    return is_ancestor(category.parent_id, potential_ancestor_id)


def get_tree_statistics(category_id: int) -> Dict:
    stats = {
        'node_count': 0,
        'depth': 0,
        'leaf_count': 0,
        'branch_count': 0
    }

    def _collect_stats(current_id, current_depth):
        children = Category.get_children(current_id)

        stats['node_count'] += 1
        stats['depth'] = max(stats['depth'], current_depth)

        if not children:
            stats['leaf_count'] += 1
        elif len(children) > 1:
            stats['branch_count'] += 1

        for child in children:
            _collect_stats(child.id, current_depth + 1)

    _collect_stats(category_id, 1)
    return stats


def export_tree_to_text(category_id: int, file_path: str) -> bool:
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            root = Category.get_by_id(category_id)
            f.write(f"KNOWLEDGE TREE: {root.name}\n")
            f.write("=" * 60 + "\n\n")

            if root.description:
                f.write(f"Root Description: {root.description}\n\n")

            f.write("TREE STRUCTURE:\n")
            _write_branch(f, category_id)

            stats = get_tree_statistics(category_id)
            f.write(f"\nSTATISTICS:\n")
            f.write(f"- Total nodes: {stats['node_count']}\n")
            f.write(f"- Tree depth: {stats['depth']}\n")
            f.write(f"- Leaf nodes: {stats['leaf_count']}\n")
            f.write(f"- Branch nodes: {stats['branch_count']}\n")

        return True
    except Exception:
        return False


def _write_branch(file, category_id: int, level: int = 0):
    category = Category.get_by_id(category_id)
    indent = "    " * level

    file.write(f"{indent}└── {category.name} (ID: {category.id})\n")
    if category.description:
        file.write(f"{indent}    Description: {category.description}\n")

    for child in Category.get_children(category_id):
        _write_branch(file, child.id, level + 1)