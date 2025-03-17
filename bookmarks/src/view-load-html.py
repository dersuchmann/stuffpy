import json
from pathlib import Path
import os
import solara
from typing import List, Dict
from typedefs import Root, RootT, Category, CategoryT, Bookmark, BookmarkT

# Get environment variables
BASE_DIR = Path(os.environ['STUFF_BASE_DIR'])
SOURCE_DIR = Path(os.environ['STUFF_SOURCE_DIR'])
REPO_DIR = Path(os.environ['STUFF_REPO_DIR'])
COMPILED_DIR = Path(os.environ['STUFF_COMPILED_DIR'])
OP_DIR = Path(os.environ['STUFF_OP_DIR'])

def read_json_file(filepath: Path) -> Root:
    with open(filepath, 'r') as f:
        return Root.from_json_data(json.load(f))
input: Path = COMPILED_DIR / 'data.json'
nonreactive_root: Root = read_json_file(input)


@solara.component
def Page(): 
    
    # Reactive variables
    root: solara.Reactive[Root] = solara.use_reactive(nonreactive_root)
    
    # Closure creators
    # (none yet)
    
    # UI
    with solara.Column(align="center", style="width: 800px; margin: 0 auto !important;"):
        
        # actual content
        with solara.Column(gap="0px", style="width: 800px;") as col:
            
            for i, category in enumerate(root.value.categories):
            
                solara.Markdown(f"# {category.date} | {category.scope} | {category.name}", style="text-align: center; margin-bottom: 30px; font-size: 120%;")
                for j, bookmark in enumerate(category.items):
                    with solara.Card(title=bookmark.title, style="background-color: #ffeeee;") as card:
                        solara.HTML(tag="a", attributes={ 'href': bookmark.url }, unsafe_innerHTML=bookmark.url)
            solara.Markdown("&nbsp;")



# The following line is required only when running the code in a Jupyter notebook:
#Page()
