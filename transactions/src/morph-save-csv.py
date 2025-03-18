import csv
import json
from pathlib import Path
import os
from typing import List, Dict, Any
from typedefs import Root, RootT, Account, AccountT, Transaction, TransactionT
import re

# Get environment variables
BASE_DIR = Path(os.environ['STUFF_BASE_DIR'])
SOURCE_DIR = Path(os.environ['STUFF_SOURCE_DIR'])
REPO_DIR = Path(os.environ['STUFF_REPO_DIR'])
COMPILED_DIR = Path(os.environ['STUFF_COMPILED_DIR'])
OP_DIR = Path(os.environ['STUFF_OP_DIR'])

def decode_transaction(csv_transaction: Dict[str, str]) -> Transaction:
    date: str = csv_transaction['Date']
    payee: str = csv_transaction['Payee']
    memo: str = csv_transaction['Memo']
    amount_str: str = csv_transaction['Amount']
    if not re.match(r'^-?\d+[\.,]\d{2}$', amount_str):
        raise ValueError(f"Invalid amount format: {amount_str}")
    amount: int = int(amount_str.replace('.', '').replace(',', ''))
    
    transaction = Transaction(
        t=TransactionT.SUCHMANN_TRANSACTIONS_TRANSACTION,
        date=date,
        payee=payee,
        memo=memo,
        amount=amount,
    )
    return transaction

def decode_account(bank: str, name: str, csv_transactions: Any) -> Account:
    transactions = [decode_transaction(ct) for ct in csv_transactions]
    account = Account(
        t=AccountT.SUCHMANN_TRANSACTIONS_ACCOUNT,
        bank=bank,
        name=name,
        transactions=transactions,
    )
    return account

def read_csv_folder(folderpath: Path) -> Root:
    accounts: list[Account] = []
    account_names: dict[str, list[str]] = {}
    csv_files = sorted([f for f in folderpath.iterdir() if re.match(r'.*\.csv$', f.name, re.IGNORECASE)])
    pattern = re.compile(r'^(\w+)_(\w+)_(.*)$')
    for csv_file in csv_files:
        match = pattern.match(csv_file.stem)
        if not match:
            print(f"Skipped due to incorrect file name: {csv_file.name}")
        else:
            bank = match.group(1)
            name = match.group(2)
            csv_transactions: list[dict[str, Any]] = []
            if csv_file.exists():
                with open(csv_file, 'rb') as f:
                    content = f.read()
                    if content.startswith(b'\xef\xbb\xbf'):
                        content = content[3:]
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(content.decode('utf-8').splitlines()[0])
                    csv_items = csv.DictReader(content.decode('utf-8').splitlines(), dialect=dialect)
                    csv_items.fieldnames = [field.strip() for field in csv_items.fieldnames]
                    csv_items = [{k: v.strip() for k, v in row.items()} for row in csv_items]
                    for csv_transaction in csv_items:
                        csv_transactions.append(csv_transaction)
            if not bank in account_names.keys():
                account_names[bank] = [name]
                accounts.append(decode_account(bank, name, csv_transactions))
            elif not name in account_names[bank]:
                account_names[bank].append(name)
                accounts.append(decode_account(bank, name, csv_transactions))
            else:
                account = next(acc for acc in accounts if acc.bank == bank and acc.name == name)
                # If there is no match, a StopIteration exception will be raised
                account.transactions[0:0] = [decode_transaction(ct) for ct in csv_transactions] # correctly add multiple entries to the existing list at the front
    
    root = Root(
        t=RootT.SUCHMANN_TRANSACTIONS_ROOT,
        accounts=accounts,
    )
    return root

def save_json_file(filepath: Path, root: Root):
    with open(filepath, 'w') as f:
        json.dump(root.to_json_data(), f, indent=2)

input = OP_DIR
output = COMPILED_DIR / 'data.json'

root = read_csv_folder(input)
save_json_file(output, root)
