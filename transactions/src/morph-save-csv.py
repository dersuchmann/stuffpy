import csv
import json
import yaml
from pathlib import Path
import os
from typing import List, Dict, Any
from typedefs import Root, RootT, Account, AccountT, AccountI, Transaction, TransactionT, TransactionI, RootMonth, RootMonthYes, RootMonthYesPath, RootMonthNo
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

def read_ledger_folder(folderpath: Path) -> list[Account]:
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
    
    return accounts


def locate_and_check_leaves(accounts: list[Account], month: int, yaml_data: dict[str, Any] | list[Any] | str, current_path: list[str] | None=None, months: dict[str, RootMonth] | None=None, errors: list[str] | None=None):
    if current_path is None:
        current_path = [str(month)]
    if months is None:
        months = {}
    if errors is None:
        errors = []

    if isinstance(yaml_data, dict):
        for key, value in yaml_data.items():
            locate_and_check_leaves(accounts, month, value, current_path + [key], months, errors)
    elif isinstance(yaml_data, list):
        for item in yaml_data:
            locate_and_check_leaves(accounts, month, item, current_path, months, errors)
    elif isinstance(yaml_data, str):
        hash_expression = fr'[0-9A-Fa-f]{{4}}_[0-9A-Fa-f]{{4}}'
        verify_separator = fr'=|\||\.\.'
        nonempty_verify_column = fr'(?:.(?!{verify_separator}))*.'
        empty_verify_column = fr'(?={verify_separator})'
        first_verify_column = fr'=({empty_verify_column}|{nonempty_verify_column})'
        other_verify_column = fr'\|({empty_verify_column}|{nonempty_verify_column})'
        verify_expression = fr'(?:{first_verify_column})?(?:{other_verify_column})?(?:{other_verify_column})?'
        split_expression = fr'(?:\.\.(.*))?'
        match = re.match(fr'^({hash_expression}){verify_expression}{split_expression}', yaml_data)
        if match:
            hash, amount, date, account, split = [match.group(i+1) for i in range(5)]
            amount = None if amount is None or amount == "" else re.match(r'^(-?\d+)\.(\d\d)$', amount)
            amount = None if amount is None or not amount else int(amount.group(1) + amount.group(2))
            date   = None if date   is None or date   == "" else date
            split  = None if split  is None or split  == "" else re.match(r'^(-?\d+)\.(\d\d)$', split )
            split  = None if split  is None or not split  else int(split .group(1) + split .group(2))
            if amount is not None or date is not None or account is not None:
                maybe_transaction = [(a, t) for a in accounts for t in a.transactions if t.h == hash]
                if len(maybe_transaction) == 0:
                    errors.append(f"{hash}: cannot check because it is missing in ledgers")
                else: # TODO what if multiple results, i.e. hash collision?
                    a, t = maybe_transaction[0]
                    if amount is not None and amount != t.amount:
                        errors.append(f"{hash}: amount is {t.amount} in ledger and {amount} in check")
                    if date is not None and date != t.date:
                        errors.append(f"{hash}: date is {t.date} in ledger and {date} in check")
                    if account is not None and account != f"{a.i.bank}_{a.i.name}":
                        errors.append(f"{hash}: in ledger of '{a.i.bank}_{a.i.name}' but '{account}' in check")
            if split is not None:
                if hash not in months:
                    # first split, add RootMonthYes
                    months[hash] = RootMonthYes(is_split="yes", paths=[RootMonthYesPath(amount=split, path=current_path)])
                else:
                    if isinstance(months[hash], RootMonthYes):
                        # subsequent split, append to RootMonthYes
                        months[hash].paths.append(RootMonthYesPath(amount=split, path=current_path))
                    else: # if isinstance(months[hash], RootMonthNo):
                        # error!
                        errors.append(f"{hash}: first encountered as split but later as non-split")
            else:
                if hash not in months:
                    # non-split, add RootMonthNo
                    months[hash] = RootMonthNo(is_split="no", path=current_path)
                else:
                    # error!
                    errors.append(f"{hash}: first encountered as non-split but later encountered a second time")
        else:
            print(f"invalid: {yaml_data}")
        
    return months, errors


def read_months(accounts: list[Account], folderpath: Path):
    months: dict[str, RootMonth] = {}
    splits_result: dict[str, int] = {}
    errors: list[str] = []
    for yaml_file in folderpath.glob('*.yaml'):
        print(yaml_file.name)
        match = re.fullmatch(r'(\d{4})\.yaml', yaml_file.name)
        if match:
            month = int(match.group(1))
            with open(yaml_file, 'r') as f:
                yaml_data = yaml.safe_load(f)
                locate_and_check_leaves(accounts, month, yaml_data, months=months, errors=errors)

    for hash in months.keys():
        if months[hash].is_split == "yes":
            maybe_transaction = [(a, t) for a in accounts for t in a.transactions if t.h == hash]
            if len(maybe_transaction) == 0:
                pass # This error has already been reported
            else: # TODO what if multiple results, i.e. hash collision?
                a, t = maybe_transaction[0]
                sum_of_splits = sum(p.amount for p in months[hash].paths)
                if sum_of_splits != t.amount:
                    errors.append(f"{hash}: amount is {t.amount} in ledger and splits add up to {sum_of_splits}")

    from_categories = set(months.keys())
    from_ledgers = set(t.h for account in accounts for t in account.transactions)
    missing_in_ledgers = from_categories - from_ledgers
    missing_in_categories = from_ledgers - from_categories
    if missing_in_ledgers != set():
        errors.append(f"missing in ledgers: {missing_in_ledgers}")
    if missing_in_categories != set():
        errors.append(f"missing in categories: {missing_in_categories}")

    return months, errors

def read_input(input: Path):
    # input is discarded for now because we have not implemented yet 
    # how to handle the case that OP_DIR is not SOURCE_DIR
    accounts = read_ledger_folder(SOURCE_DIR / "ledgers")
    months, errors = read_months(accounts, SOURCE_DIR / "scopes" / "lovis" / "months")
    
    root = Root(
        t=RootT.SUCHMANN_TRANSACTIONS_ROOT,
        accounts=accounts,
        months=months,
        errors=errors,
    )
    return root

def save_json_file(filepath: Path, root: Root):
    with open(filepath, 'w') as f:
        json.dump(root.to_json_data(), f, indent=2)

input = OP_DIR
output = COMPILED_DIR / 'data.json'

root = read_input(input)
save_json_file(output, root)
