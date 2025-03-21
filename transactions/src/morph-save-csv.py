import csv
import json
from pathlib import Path
import os
from typing import List, Dict, Any
from typedefs import Root, RootT, Account, AccountT, AccountI, Transaction, TransactionT, TransactionI
import re
import fnvhash

def stuff_hash(i: Any):
    temp = hex(fnvhash.fnv1a_32(bytes(repr(i), encoding="utf-8")))[2:].zfill(8)
    return temp[:4] + '_' + temp[4:]


# Get environment variables
BASE_DIR = Path(os.environ['STUFF_BASE_DIR'])
SOURCE_DIR = Path(os.environ['STUFF_SOURCE_DIR'])
REPO_DIR = Path(os.environ['STUFF_REPO_DIR'])
COMPILED_DIR = Path(os.environ['STUFF_COMPILED_DIR'])
OP_DIR = Path(os.environ['STUFF_OP_DIR'])

def decode_transaction(i: TransactionI, csv_transaction: Dict[str, str]) -> Transaction:
    date: str = csv_transaction['Date']
    payee: str = csv_transaction['Payee']
    memo: str = csv_transaction['Memo']
    amount_str: str = csv_transaction['Amount']
    if not re.match(r'^-?\d+[\.,]\d{2}$', amount_str):
        raise ValueError(f"Invalid amount format: {amount_str}")
    amount: int = int(amount_str.replace('.', '').replace(',', ''))
    
    transaction = Transaction(
        t=TransactionT.SUCHMANN_TRANSACTIONS_TRANSACTION,
        i=i,
        h=stuff_hash(i),
        date=date,
        payee=payee,
        memo=memo,
        amount=amount,
    )
    return transaction

def decode_account(i: AccountI, transactions: list[Transaction]) -> Account:
    account = Account(
        t=AccountT.SUCHMANN_TRANSACTIONS_ACCOUNT,
        i=i,
        h=stuff_hash(i),
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
                account_i = AccountI(bank=bank, name=name)
                new_transactions = [
                    decode_transaction(
                        TransactionI(filename=str(csv_file).removeprefix(str(SOURCE_DIR / "ledgers")), index=index),
                        ct,
                    ) for index, ct in enumerate(csv_transactions)
                ]
                accounts.append(decode_account(account_i, new_transactions))
            elif not name in account_names[bank]:
                account_names[bank].append(name)
                account_i = AccountI(bank=bank, name=name)
                new_transactions = [
                    decode_transaction(
                        TransactionI(filename=str(csv_file).removeprefix(str(SOURCE_DIR / "ledgers")), index=index),
                        ct,
                    ) for index, ct in enumerate(csv_transactions)
                ]
                accounts.append(decode_account(account_i, new_transactions))
            else:
                account = next(acc for acc in accounts if acc.i.bank == bank and acc.i.name == name)
                # If there is no match, a StopIteration exception will be raised
                account.transactions[0:0] = [
                    decode_transaction(
                        TransactionI(filename=str(csv_file).removeprefix(str(SOURCE_DIR / "ledgers")), index=index),
                        ct,
                    ) for index, ct in enumerate(csv_transactions)
                ] # correctly add multiple entries to the existing list at the front
    
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
