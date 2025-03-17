import json
from pathlib import Path
import os
import solara
from typing import List, Dict
from typedefs import Root, RootT, Taskset, TasksetT, Task, TaskT

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
    active_taskset_index: solara.Reactive[int | None] = solara.use_reactive(None)

    # Closure creators
    def begin_current_task(i: int):
        def closure():
            active_taskset_index.value = i
        return closure
    
    def mark_current_task_as_completed(i: int):
        def closure():
            tasks = [*root.value.tasksets[i].tasks[1:]]
            completed_tasks = [*root.value.tasksets[i].completed_tasks] + [root.value.tasksets[i].tasks[0]]
            taskset = Taskset(t=TasksetT.SUCHMANN_TASKSETS_TASKSET, name=root.value.tasksets[i].name, tasks=tasks, completed_tasks=completed_tasks)
            tasksets = [*root.value.tasksets[:i]] + [taskset] + [*root.value.tasksets[i+1:]]
            root.value = Root(t=RootT.SUCHMANN_TASKSETS_ROOT, tasksets=tasksets)
            active_taskset_index.value = None
        return closure
    
    def delete_taskset(i: int):
        def closure():
            tasksets = [*root.value.tasksets[:i]] + [*root.value.tasksets[i+1:]]
            root.value = Root(t=RootT.SUCHMANN_TASKSETS_ROOT, tasksets=tasksets)
        return closure

    # UI
    with solara.Column(align="center", style="width: 800px; margin: 0 auto !important;"):
        
        # actual content
        with solara.Column(gap="30px", style="width: 800px;") as col:
            
            solara.Markdown("# All Tasks", style="text-align: center; font-size: 120%;")
            for i, taskset in enumerate(root.value.tasksets):
                with solara.Card(title=taskset.name, subtitle=f"{len(taskset.completed_tasks)}/{len(taskset.tasks) + len(taskset.completed_tasks)} completed", style=active_taskset_index.value == i and "background-color: lightgreen;" or "background-color: #ffeeee;") as card:
                    if len(taskset.tasks) == 0:
                        current_task = Task(t=TaskT.SUCHMANN_TASKSETS_TASK, name="No tasks left")
                    else:
                        current_task = taskset.tasks[0]
                    with solara.Details(summary="View all tasks...", expand=False):
                        markdown = ""
                        for j, task in enumerate(taskset.completed_tasks):
                            markdown += f"- ✓ {task.name}\n"
                        for j, task in enumerate(taskset.tasks):
                            markdown += f"- ☐ **{task.name}**\n" if j == 0 else f"- ☐ {task.name}\n"
                        solara.Markdown(markdown)
                    solara.Markdown("Next task:")
                    with solara.Card(style="margin: 0px !important;"):
                        solara.Markdown(f"# {current_task.name}", style="margin-top: -20px;")
                    with solara.CardActions():
                        solara.Button(active_taskset_index.value == i and "Running..." or "Begin", text=True, disabled=len(taskset.tasks) == 0 or (active_taskset_index.value is not None), on_click=begin_current_task(i))
                        if active_taskset_index.value != i:
                            pass
                        else:
                            solara.Button("Mark as completed", text=True, disabled=len(taskset.tasks) == 0, on_click=mark_current_task_as_completed(i))
                        #solara.Button("Delete", text=True, on_click=delete_taskset(i))
            solara.Markdown("&nbsp;")



# The following line is required only when running the code in a Jupyter notebook:
#Page()
