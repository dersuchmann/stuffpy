import json
from pathlib import Path
import os
import solara
from typing import List, Dict
from typedefs import Root, RootT, Account, AccountT, Transaction, TransactionT

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
    
    # Closure creators
    # (none yet)
    
    # UI
    with solara.Column(align="center", style="width: 800px; margin: 0 auto !important;"):
        
        # actual content
        with solara.Column(gap="0px", style="width: 800px;") as col:
            
            for i, account in enumerate(root.value.accounts):
                solara.Markdown(f"# {account.bank}_{account.name}", style="text-align: center; margin-bottom: 30px; font-size: 120%;")
                with solara.Card(title="Transactions", style="background-color: #ffeeee;") as card:
                    for j, transaction in enumerate(account.transactions):
                            solara.Markdown(f"{transaction.date} | {transaction.amount / 100:.2f} | {transaction.payee} | {transaction.memo}")
                solara.Markdown("&nbsp;")



# The following line is required only when running the code in a Jupyter notebook:
#Page()
