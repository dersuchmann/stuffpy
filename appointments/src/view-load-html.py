import json
from pathlib import Path
import os
import solara
from typing import List, Dict
from typedefs import Root, RootT, Category, CategoryT, Appointment, AppointmentT

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
    solara.Title(f"{str(OP_DIR).removeprefix(str(BASE_DIR.parent))}")
    
    # Reactive variables
    root: solara.Reactive[Root] = solara.use_reactive(nonreactive_root)
    clipboard: solara.Reactive[tuple[int, int]] = solara.use_reactive(None)
    
    # Closure creators
    def cut(i: int, j: int):
        def closure():
            clipboard.value = (i, j)
        return closure
    
    def paste(i: int, j: int, before: bool):
        def closure():
            old_i, old_j = clipboard.value
            
            new_i = i
            new_j = j + (1 if not before else 0)

            # Get the appointment to move
            appointment_to_move = root.value.categories[old_i].items[old_j]
            
            if old_i == new_i:
                # Remove and insert in the same category
                old_and_new_category = root.value.categories[old_i]
                if old_j < new_j:
                    old_items = (
                        [*old_and_new_category.items[:old_j]] + 
                        [*old_and_new_category.items[old_j + 1:new_j]] + 
                        [appointment_to_move] + 
                        [*old_and_new_category.items[new_j:]]
                    )
                else:
                    old_items = (
                        [*old_and_new_category.items[:new_j]] + 
                        [appointment_to_move] + 
                        [*old_and_new_category.items[new_j:old_j]] + 
                        [*old_and_new_category.items[old_j + 1:]]
                    )
                old_and_new_category = Category(t=CategoryT.SUCHMANN_APPOINTMENTS_CATEGORY, name=old_and_new_category.name, items=old_items)
                # Update root with both changes
                categories = [*root.value.categories]
                categories[old_i] = old_and_new_category
            else:
                # Remove from old location
                old_category = root.value.categories[old_i]
                old_items = [*old_category.items[:old_j]] + [*old_category.items[old_j + 1:]]
                old_category = Category(t=CategoryT.SUCHMANN_APPOINTMENTS_CATEGORY, name=old_category.name, items=old_items)
                # Insert into new location
                new_category = root.value.categories[new_i]
                new_items = [*new_category.items[:new_j]] + [appointment_to_move] + [*new_category.items[new_j:]]
                new_category = Category(t=CategoryT.SUCHMANN_APPOINTMENTS_CATEGORY, name=new_category.name, items=new_items)
                # Update root with both changes
                categories = [*root.value.categories]
                categories[old_i] = old_category
                categories[new_i] = new_category
            root.value = Root(t=RootT.SUCHMANN_APPOINTMENTS_ROOT, categories=categories)

            clipboard.value = None
        return closure
    
    # UI
    with solara.Column(align="center", style="width: 800px; margin: 0 auto !important;"):
        
        # actual content
        with solara.Column(gap="30px", style="width: 800px;") as col:
            
            for i, category in enumerate(root.value.categories):
            
                solara.Markdown(f"# {category.name}", style="text-align: center; font-size: 120%;")
                for j, appointment in enumerate(category.items):
                    with solara.Card(title=appointment.title, style=(clipboard.value == (i, j) and "opacity: 0.4;" or "") + "background-color: #ffeeee;") as card:
                        solara.Markdown(f"{appointment.tag} | {appointment.date} | starts {appointment.start} | ends {appointment.end}")
                        with solara.CardActions():
                            solara.Button("✂",   text=True, disabled=clipboard.value == (i, j), on_click=cut(i, j))
                            solara.Button("📋 before", text=True, disabled=clipboard.value is None or clipboard.value == (i, j), on_click=paste(i, j, True))
                            solara.Button("📋 after",  text=True, disabled=clipboard.value is None or clipboard.value == (i, j), on_click=paste(i, j, False))
                solara.Markdown("&nbsp;")



# The following line is required only when running the code in a Jupyter notebook:
#Page()
