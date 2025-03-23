# Code generated by jtd-codegen for Python v0.3.1

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union, get_args, get_origin


@dataclass
class RootMonth:
    is_split: 'str'

    @classmethod
    def from_json_data(cls, data: Any) -> 'RootMonth':
        variants: Dict[str, Type[RootMonth]] = {
            "no": RootMonthNo,
            "yes": RootMonthYes,
        }

        return variants[data["is_split"]].from_json_data(data)

    def to_json_data(self) -> Any:
        pass

@dataclass
class RootMonthNo(RootMonth):
    path: 'List[str]'

    @classmethod
    def from_json_data(cls, data: Any) -> 'RootMonthNo':
        return cls(
            "no",
            _from_json_data(List[str], data.get("path")),
        )

    def to_json_data(self) -> Any:
        data = { "is_split": "no" }
        data["path"] = _to_json_data(self.path)
        return data

@dataclass
class RootMonthYesPath:
    amount: 'int'
    path: 'List[str]'

    @classmethod
    def from_json_data(cls, data: Any) -> 'RootMonthYesPath':
        return cls(
            _from_json_data(int, data.get("amount")),
            _from_json_data(List[str], data.get("path")),
        )

    def to_json_data(self) -> Any:
        data: Dict[str, Any] = {}
        data["amount"] = _to_json_data(self.amount)
        data["path"] = _to_json_data(self.path)
        return data

@dataclass
class RootMonthYes(RootMonth):
    paths: 'List[RootMonthYesPath]'

    @classmethod
    def from_json_data(cls, data: Any) -> 'RootMonthYes':
        return cls(
            "yes",
            _from_json_data(List[RootMonthYesPath], data.get("paths")),
        )

    def to_json_data(self) -> Any:
        data = { "is_split": "yes" }
        data["paths"] = _to_json_data(self.paths)
        return data

class RootT(Enum):
    SUCHMANN_TRANSACTIONS_ROOT = "suchmann.transactions.root"
    @classmethod
    def from_json_data(cls, data: Any) -> 'RootT':
        return cls(data)

    def to_json_data(self) -> Any:
        return self.value

@dataclass
class Root:
    accounts: 'List[Account]'
    errors: 'List[str]'
    months: 'Dict[str, RootMonth]'
    t: 'RootT'

    @classmethod
    def from_json_data(cls, data: Any) -> 'Root':
        return cls(
            _from_json_data(List[Account], data.get("accounts")),
            _from_json_data(List[str], data.get("errors")),
            _from_json_data(Dict[str, RootMonth], data.get("months")),
            _from_json_data(RootT, data.get("t")),
        )

    def to_json_data(self) -> Any:
        data: Dict[str, Any] = {}
        data["accounts"] = _to_json_data(self.accounts)
        data["errors"] = _to_json_data(self.errors)
        data["months"] = _to_json_data(self.months)
        data["t"] = _to_json_data(self.t)
        return data

class AccountT(Enum):
    SUCHMANN_TRANSACTIONS_ACCOUNT = "suchmann.transactions.account"
    @classmethod
    def from_json_data(cls, data: Any) -> 'AccountT':
        return cls(data)

    def to_json_data(self) -> Any:
        return self.value

@dataclass
class Account:
    h: 'str'
    i: 'AccountI'
    t: 'AccountT'
    transactions: 'List[Transaction]'

    @classmethod
    def from_json_data(cls, data: Any) -> 'Account':
        return cls(
            _from_json_data(str, data.get("h")),
            _from_json_data(AccountI, data.get("i")),
            _from_json_data(AccountT, data.get("t")),
            _from_json_data(List[Transaction], data.get("transactions")),
        )

    def to_json_data(self) -> Any:
        data: Dict[str, Any] = {}
        data["h"] = _to_json_data(self.h)
        data["i"] = _to_json_data(self.i)
        data["t"] = _to_json_data(self.t)
        data["transactions"] = _to_json_data(self.transactions)
        return data

@dataclass
class AccountI:
    bank: 'str'
    name: 'str'

    @classmethod
    def from_json_data(cls, data: Any) -> 'AccountI':
        return cls(
            _from_json_data(str, data.get("bank")),
            _from_json_data(str, data.get("name")),
        )

    def to_json_data(self) -> Any:
        data: Dict[str, Any] = {}
        data["bank"] = _to_json_data(self.bank)
        data["name"] = _to_json_data(self.name)
        return data

@dataclass
class Node:
    t: 'NodeTypes'

    @classmethod
    def from_json_data(cls, data: Any) -> 'Node':
        return cls(
            _from_json_data(NodeTypes, data.get("t")),
        )

    def to_json_data(self) -> Any:
        data: Dict[str, Any] = {}
        data["t"] = _to_json_data(self.t)
        return data

class NodeTypes(Enum):
    SUCHMANN_TRANSACTIONS_ACCOUNT = "suchmann.transactions.account"
    SUCHMANN_TRANSACTIONS_TRANSACTION = "suchmann.transactions.transaction"
    @classmethod
    def from_json_data(cls, data: Any) -> 'NodeTypes':
        return cls(data)

    def to_json_data(self) -> Any:
        return self.value

class TransactionT(Enum):
    SUCHMANN_TRANSACTIONS_TRANSACTION = "suchmann.transactions.transaction"
    @classmethod
    def from_json_data(cls, data: Any) -> 'TransactionT':
        return cls(data)

    def to_json_data(self) -> Any:
        return self.value

@dataclass
class Transaction:
    amount: 'int'
    date: 'str'
    h: 'str'
    i: 'TransactionI'
    memo: 'str'
    payee: 'str'
    t: 'TransactionT'

    @classmethod
    def from_json_data(cls, data: Any) -> 'Transaction':
        return cls(
            _from_json_data(int, data.get("amount")),
            _from_json_data(str, data.get("date")),
            _from_json_data(str, data.get("h")),
            _from_json_data(TransactionI, data.get("i")),
            _from_json_data(str, data.get("memo")),
            _from_json_data(str, data.get("payee")),
            _from_json_data(TransactionT, data.get("t")),
        )

    def to_json_data(self) -> Any:
        data: Dict[str, Any] = {}
        data["amount"] = _to_json_data(self.amount)
        data["date"] = _to_json_data(self.date)
        data["h"] = _to_json_data(self.h)
        data["i"] = _to_json_data(self.i)
        data["memo"] = _to_json_data(self.memo)
        data["payee"] = _to_json_data(self.payee)
        data["t"] = _to_json_data(self.t)
        return data

@dataclass
class TransactionI:
    filename: 'str'
    index: 'int'

    @classmethod
    def from_json_data(cls, data: Any) -> 'TransactionI':
        return cls(
            _from_json_data(str, data.get("filename")),
            _from_json_data(int, data.get("index")),
        )

    def to_json_data(self) -> Any:
        data: Dict[str, Any] = {}
        data["filename"] = _to_json_data(self.filename)
        data["index"] = _to_json_data(self.index)
        return data

def _from_json_data(cls: Any, data: Any) -> Any:
    if data is None or cls in [bool, int, float, str, object] or cls is Any:
        return data
    if cls is datetime:
        return _parse_rfc3339(data)
    if get_origin(cls) is Union:
        return _from_json_data(get_args(cls)[0], data)
    if get_origin(cls) is list:
        return [_from_json_data(get_args(cls)[0], d) for d in data]
    if get_origin(cls) is dict:
        return { k: _from_json_data(get_args(cls)[1], v) for k, v in data.items() }
    return cls.from_json_data(data)

def _to_json_data(data: Any) -> Any:
    if data is None or type(data) in [bool, int, float, str, object]:
        return data
    if type(data) is datetime:
        return data.isoformat()
    if type(data) is list:
        return [_to_json_data(d) for d in data]
    if type(data) is dict:
        return { k: _to_json_data(v) for k, v in data.items() }
    return data.to_json_data()

def _parse_rfc3339(s: str) -> datetime:
    datetime_re = '^(\d{4})-(\d{2})-(\d{2})[tT](\d{2}):(\d{2}):(\d{2})(\.\d+)?([zZ]|((\+|-)(\d{2}):(\d{2})))$'
    match = re.match(datetime_re, s)
    if not match:
        raise ValueError('Invalid RFC3339 date/time', s)

    (year, month, day, hour, minute, second, frac_seconds, offset,
     *tz) = match.groups()

    frac_seconds_parsed = None
    if frac_seconds:
        frac_seconds_parsed = int(float(frac_seconds) * 1_000_000)
    else:
        frac_seconds_parsed = 0

    tzinfo = None
    if offset == 'Z':
        tzinfo = timezone.utc
    else:
        hours = int(tz[2])
        minutes = int(tz[3])
        sign = 1 if tz[1] == '+' else -1

        if minutes not in range(60):
            raise ValueError('minute offset must be in 0..59')

        tzinfo = timezone(timedelta(minutes=sign * (60 * hours + minutes)))

    second_parsed = int(second)
    if second_parsed == 60:
        second_parsed = 59

    return datetime(int(year), int(month), int(day), int(hour), int(minute),
                    second_parsed, frac_seconds_parsed, tzinfo)            
