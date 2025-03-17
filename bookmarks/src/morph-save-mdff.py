import mistune
from mistune import Markdown
from mistune.renderers.markdown import MarkdownRenderer
from mistune.core import BlockState
import json
from pathlib import Path
import os
from typing import Any
from typedefs import Root, RootT, Category, CategoryT, Bookmark, BookmarkT

# Get environment variables
BASE_DIR = Path(os.environ['STUFF_BASE_DIR'])
SOURCE_DIR = Path(os.environ['STUFF_SOURCE_DIR'])
REPO_DIR = Path(os.environ['STUFF_REPO_DIR'])
COMPILED_DIR = Path(os.environ['STUFF_COMPILED_DIR'])
OP_DIR = Path(os.environ['STUFF_OP_DIR'])

renderer = MarkdownRenderer()

def convert_ast(ast: list[dict[str, Any]]) -> Root:
    def process_node(node: dict[str, Any]) -> list[Any]:
        node_type = node.get('type')
        
        if node_type == 'heading':
            heading_text: str = renderer(node['children'], state=BlockState())
            date, scope, name = heading_text.strip().split(sep = ",", maxsplit = 2)
            return [Category(
                t = CategoryT.SUCHMANN_BOOKMARKS_CATEGORY,
                date = date,
                scope = scope,
                name = name,
                items = [],
            )]
        elif node_type == 'link':
            return [Bookmark(
                t = BookmarkT.SUCHMANN_BOOKMARKS_BOOKMARK,
                title = renderer(node['children'], state=BlockState()),
                url = node['attrs']['url'],
            )]
        elif node_type == 'paragraph':
            return [item for child in node['children'] for item in process_node(child)]
        
        return []

    categories: list[Category] = []
    current_category: Category | None = None
    
    for node in ast:
        processed = process_node(node)
        for item in processed:
            if isinstance(item, Category):
                if current_category:
                    categories.append(current_category)
                current_category = item
            elif isinstance(item, Bookmark) and current_category:
                current_category.items.append(item)
    
    if current_category:
        categories.append(current_category)
    
    root = Root(
        t=RootT.SUCHMANN_BOOKMARKS_ROOT,
        categories=categories,
    )
    return root

def read_markdown_file(filepath: Path) -> Root:
    """Read a markdown file and return both raw content and AST representation"""
    if filepath.exists():
        markdown: Markdown = mistune.create_markdown(renderer='ast')
        with open(filepath, 'r') as f:
            content: str = f.read()
            ast: Any = markdown(content)
            root = convert_ast(ast)
            return root
    return Root(
        t = RootT.SUCHMANN_BOOKMARKS_ROOT,
        categories = [],
    )

def write_json_file(filepath: Path, root: Root):
    with open(filepath, 'w') as f:
        json.dump(root.to_json_data(), f, indent=2)

input: Path = OP_DIR / 'data.md'
output: Path = COMPILED_DIR / 'data.json'

root = read_markdown_file(input)
write_json_file(output, root)




def convert_ast_2(ast: list[dict[str, Any]]) -> dict[str, Any]:
    def process_node_2(node: dict[str, Any]) -> list[dict[str, Any]]:
        node_type = node.get('type')
        
        if node_type == 'heading':
            return [{
                'type': 'heading',
                'children': renderer(node['children'], state=BlockState()),
                'content': []
            }]
        elif node_type == 'link':
            return [{
                'type': 'link',
                'children': renderer(node['children'], state=BlockState()),
                'url': node['attrs']['url']
            }]
        elif node_type == 'paragraph':
            return [item for child in node['children'] for item in process_node_2(child)]
        
        return []

    sections: list[dict[str, Any]] = []
    current_heading = None
    
    for node in ast:
        processed = process_node_2(node)
        for item in processed:
            if item['type'] == 'heading':
                if current_heading:
                    sections.append(current_heading)
                current_heading = item
            elif item['type'] == 'link' and current_heading:
                current_heading['content'].append(item)
    
    if current_heading:
        sections.append(current_heading)
    
    result = { 'type': 'document', 'sections': sections }
    return result

