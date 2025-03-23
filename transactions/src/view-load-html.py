import json
from pathlib import Path
import os
import solara
import solara.lab
from typing import List, Dict
from typedefs import Root, RootT, Account, AccountT, Transaction, TransactionT, RootForeignMonth

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

months = [2412, 2501, 2502, 2503]

def get_filter_prefix(month: int):
    filter_year = f"20{str(month)[:2]}"
    filter_month = f"{str(month)[2:]}"
    filter_prefix = f"{filter_year}/{filter_month}/"
    return filter_prefix


@solara.component
def RegisterCard(account: Account, foreign_months: list[RootForeignMonth], the_months: dict[str, list[str]]):
    
    # Reactive variables
    month_index = solara.reactive(1)
    
    with solara.Card(title="Register", style="background-color: #ffeeee;") as register_card:
        running_sums = []
        current_sum = 0
        sorted_transactions = sorted(account.transactions, key=lambda t: t.date, reverse=True)
        for transaction in reversed(sorted_transactions):
            current_sum += transaction.amount
            running_sums.append(current_sum)
        running_sums.reverse()
        with solara.Column(style="background-color: transparent; position: relative;"):
            with solara.Column(style="visibility: hidden;"):
                with solara.lab.Tabs(background_color="transparent"):
                    with solara.lab.Tab(""):
                        solara.Column(style="background-color: transparent; height: 500px;")
            with solara.Column(style="background-color: transparent; position: absolute; inset: 0;"):
                with solara.lab.Tabs(lazy=True, background_color="transparent"):
                    for month in months:
                        with solara.lab.Tab(str(month)):
                            filter_prefix = get_filter_prefix(month)
                            with solara.Column(style="background-color: transparent; height: 500px; overflow: auto; row-gap: 0px;"):
                                for j, (transaction, running_sum) in enumerate(zip(sorted_transactions, running_sums)):
                                    maybe_fm = [fm for fm in foreign_months if fm.assign == transaction.h]
                                    actual_month = maybe_fm[0].to if len(maybe_fm) > 0 else None
                                    if not (
                                        transaction.date.startswith(filter_prefix)
                                        #(transaction.date.startswith(filter_prefix) and (actual_month is None or actual_month == month)) or 
                                        #(actual_month == month)
                                    ):
                                        continue
                                    with solara.Row(style="align-items: center; background-color: transparent; column-gap: 0px;") as row:
                                        #solara.HTML(tag="span", unsafe_innerHTML=f"<button onclick='javascript:alert(\"{transaction.h}\")'>{transaction.h[0:4]}<br>{transaction.h[5:9]}</button>")
                                        solara.Markdown(f"&nbsp;{running_sum / 100:9.2f}", style="font-family: monospace; white-space: pre;")
                                        solara.Markdown(f"<br>{transaction.h}<br>&nbsp;{f"##{str(actual_month)}##" if actual_month is not None else ""}", style="color: #999; font-family: monospace; white-space: pre;")
                                        solara.Markdown(f"{transaction.date}  {transaction.payee}<br>{transaction.amount / 100:10.2f}  {transaction.memo if transaction.memo != "" else "(no memo)"}<br><strong>{"<br>".join(" > ".join(category_path) for category_path in the_months.get(transaction.h) or []) or "UNCATEGORIZED"}</strong>", style="font-family: monospace; white-space: pre;")
                        


@solara.component
def Page(): 
    solara.Title(f"{str(OP_DIR).removeprefix(str(BASE_DIR.parent))}")
    
    # Reactive variables
    root: solara.Reactive[Root] = solara.use_reactive(nonreactive_root)
    
    # Closure creators
    # (none yet)
    
    # UI
    with solara.Column(align="center", style="width: 800px; overflow: auto; margin: 0 auto !important;"):
        
        # actual content
        with solara.Column(gap="0px", style="width: 800px; overflow: auto;") as col:
            
            solara.Markdown("Running checks...")
            from_categories = set(root.value.months.keys())
            from_ledgers = set(t.h for account in root.value.accounts for t in account.transactions)
            missing_in_ledgers = from_categories - from_ledgers
            missing_in_categories = from_ledgers - from_categories
            if missing_in_ledgers != set():
                solara.Markdown(f"missing in ledgers: {missing_in_ledgers}")
            if missing_in_categories != set():
                solara.Markdown(f"missing in categories: {missing_in_categories}")
            solara.Markdown("<br>".join(root.value.errors) or "no errors found")
                

            for i, account in enumerate(root.value.accounts):
                solara.Markdown(f"# {account.i.bank}_{account.i.name}", style="text-align: center; margin-bottom: 30px; font-size: 120%;")

                with solara.Card(title="Balance", style="background-color: #ffeeee; overflow: auto; row-gap: 0px;") as balance_card:
                    current_balance = sum(transaction.amount for transaction in account.transactions)
                    solara.Markdown(f"Current Balance: {current_balance / 100:.2f}", style="font-family: monospace; white-space: pre;")
                    running_sum = 0
                    for month in months:
                        filter_prefix = get_filter_prefix(month)
                        month_diff  = sum(transaction.amount for transaction in account.transactions if transaction.date.startswith(filter_prefix))
                        month_plus  = sum(transaction.amount for transaction in account.transactions if transaction.date.startswith(filter_prefix) and transaction.amount > 0)
                        month_minus = sum(transaction.amount for transaction in account.transactions if transaction.date.startswith(filter_prefix) and transaction.amount < 0)
                        running_sum += month_diff
                        solara.Markdown(f"{month}: + {month_diff / 100:8.2f} = {running_sum / 100:8.2f} |  -{-month_minus / 100:8.2f}  +{month_plus / 100:8.2f}", style="font-family: monospace; white-space: pre;")

                RegisterCard(account, root.value.foreign_months, root.value.months)

                solara.Markdown("&nbsp;")



# The following line is required only when running the code in a Jupyter notebook:
#Page()
