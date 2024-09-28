import anvil.server
from datetime import date, datetime, timezone

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def get_first_element(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if not isinstance(result, (list, tuple)):
            return result
        else:
            if len(result) == 0:
                raise IndexError("Cannot retrieve from empty list.")
            return result[0]
    return wrapper

def convert_mapping_rules_list(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if not isinstance(result, (list, tuple)):
            raise TypeError("Cannot convert unless the result is either list or tuple.")
        else:
            if len(result) == 0:
                return []
            return [[x.get('col'), x.get('col_code'), x.get('eaction'), x.get('etarget')] for x in result]
    return wrapper

def get_mockup_selected_start_date():
    return date(2023, 1, 1)

def get_mockup_selected_end_date():
    return date(2023, 4, 30)

def get_mockup_selected_symbol():
    return ["STOCK1"]

def get_mockup_selected_labels():
    return [2]

def get_mockup_selected_broker():
    return {
        "broker_id": "UT000001",
        "name": "Unit Test Broker",
        "ccy": "GBP"
    }

def get_new_mockup_broker():
    return {
        "name": "New Unit Test Broker",
        "ccy": "EUR"
    }

def get_mockup_setting():
    return {
        "userid": 365825345,
        "default_broker": "BR000001",
        "default_interval": "SDR",
        "default_datefrom": date(2020, 1, 1),
        "default_dateto": date(2023, 12, 31),
        "logging_level": 5
    }

def get_new_mockup_setting():
    return {
        "userid": 365825345,
        "default_broker": "BR000001",
        "default_interval": "L6M",
        "default_datefrom": date(2020, 6, 30),
        "default_dateto": date(2024, 1, 1),
        "logging_level": 10
    }

def get_mockup_broker():
    return {
        "userid": 365825345,
        "broker_id": "UT000001",
        "name": "Unit Test Broker",
        "ccy": "GBP"
    }

def get_mockup_account():
    return [
        {
            "userid": 365825345,
            "id": 1,
            "name": "Account Test",
            "ccy": "GBP",
            "valid_from": datetime.strptime("2023-07-01", "%Y-%m-%d").date(),
            "valid_to": datetime.strptime("2023-07-02", "%Y-%m-%d").date(),
            "status": True
        }
    ]

def get_new_mockup_account():
    return [
        {
            "userid": 365825345,
            "id": None,
            "name": "NEW ACCT for Test",
            "ccy": "GBP",
            "valid_from": None,
            "valid_to": None,
            "status": True
        }
    ]

def get_mockup_label():
    return {
        "userid": 365825345,
        "id": 1,
        "name": "Label Unit Test",
        "status": True,
        "keywords": None
    }

def get_new_mockup_label():
    return {
        "userid": 365825345,
        "id": None,
        "name": "Unit Test Label New",
        "status": True,
        "keywords": None
    }

def get_mockup_filetype():
    return 'E'

def get_mockup_mapping_groups():
    return [
        {
            "userid": 365825345,
            "id": 1,
            "name": "Unit Test Mapping Group",
            "filetype": "E",
            "lastsave": datetime(2023, 2, 2, 0, 0, tzinfo=timezone.utc),
            "description": "For unit test",
            "rule": None
        }
    ]

def get_mockup_mapping_rules():
    return [
        {
            "gid": 1,
            "col": "K",
            "col_code": "AMT",
            "eaction": None,
            "etarget": None,
            "rule": "Unit Test Map column K to Amount."
        },
        {
            "gid": 1,
            "col": "L",
            "col_code": "AMT",
            "eaction": "L",
            "etarget": '1',
            "rule": "Unit Test Map column L to Amount. Extra action(s): Apply label XXX."
        },
        {
            "gid": 1,
            "col": "M",
            "col_code": "DTE",
            "eaction": None,
            "etarget": None,
            "rule": "Unit Test Map column M to Date."
        },
        {
            "gid": 1,
            "col": "N",
            "col_code": "RMK",
            "eaction": None,
            "etarget": None,
            "rule": "Unit Test Map column N to Remarks."
        }
    ]

def get_new_mockup_mapping_rules():
    return [
        {
            "gid": 1,
            "col": "K",
            "col_code": "AMT",
            "eaction": None,
            "etarget": None,
            "rule": "Unit Test Map column K to Amount."
        },
        {
            "gid": 1,
            "col": "L",
            "col_code": "STD",
            "eaction": "L",
            "etarget": '1',
            "rule": "Unit Test Map column L to Statement Detail. Extra action(s): Apply label XXX."
        },
        {
            "gid": 1,
            "col": "M",
            "col_code": "DTE",
            "eaction": "A",
            "etarget": "1",
            "rule": "Unit Test Map column M to Date. Extra action(s): Apply account XXX."
        },
        {
            "gid": 1,
            "col": "P",
            "col_code": "RMK",
            "eaction": None,
            "etarget": None,
            "rule": "Unit Test Map column N to Remarks."
        }
    ]

def get_mockup_mapping_extra_actions():
    return [
        {
            "col": "L",
            "col_code": "AMT",
            "eaction": "L",
            "etarget": '1'
        }
    ]

def get_mockup_mapping_matrix():
    return [
        {
            # "gid": 1,
            "DTE": None,
            "ACC": None,
            "AMT": None,
            "RMK": None,
            "STD": None,
            "LBL": "L"
        }
    ]

def get_mockup_mapping_matrix_mogstr():
    return [list(matrix.values()) for matrix in get_mockup_mapping_matrix()]

def get_new_mockup_mapping_groups():
    return [
        {
            "userid": 365825345,
            "name": "New Unit Test Mapping Group",
            "filetype": "E",
            "lastsave": datetime(2023, 1, 30, 0, 0, tzinfo=timezone.utc),
            "description": "Newly created for unit test",
            "rule": None
        }
    ]

def get_new_mockup_transaction_group():
    return [
        {
            "userid": 365825345,
            "tab_id": None,
            "tab_name": "Unit Test NEW Exp Grp",
            "submitted": False,
            "tab_create": datetime(2023, 12, 29, 0, 0, tzinfo=timezone.utc),
            "tab_lastsave": datetime(2023, 12, 30, 0, 0, tzinfo=timezone.utc),
            "tab_submitted": None
        }
    ]

def get_mockup_transaction_group():
    return [
        {
            "userid": 365825345,
            "tab_id": 1,
            "tab_name": "Unit Test Expense Group",
            "submitted": False,
            "tab_create": datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
            "tab_lastsave": None,
            "tab_submitted": None
        }
    ]

def get_mockup_transactions():
    return [
        {
            "iid": 1,
            "tab_id": 1,
            "DTE": date(2023, 1, 1),
            "ACC": 1,
            "AMT": 100,
            "LBL": [1],
            "RMK": "Unit test trx 1",
            "STD": None
        },
        {
            "iid": 2,
            "tab_id": 2,
            "DTE": date(2023, 2, 28),
            "ACC": 2,
            "AMT": 200,
            "LBL": [2],
            "RMK": "Unit test trx 2",
            "STD": None
        }
    ]

def get_mockup_labels_summed_total():
    return [
        {
            "LBL": 1,
            "AMT": 100.0
        },
        {
            "LBL": 2,
            "AMT": 200.0
        }
    ]

def get_mockup_accounts_balance():
    return [
        {
            "ACC": 1,
            "AMT": 100.0
        },
        {
            "ACC": 2,
            "AMT": 200.0
        }
    ]

def get_mockup_stock_journal_group():
    return [
        {
            "template_id": 1,
            "template_name": "Unit Test Template",
            "broker_id": "UT000001",
            "submitted": False,
            "template_create": datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
            "template_lastsave": datetime(2023, 5, 2, 0, 0, tzinfo=timezone.utc),
            "template_submitted": None,
            "userid": 365825345
        }
    ]

def get_mockup_stock_journals():
    return [
        {
            "iid": 1,
            "template_id": 1,
            "sell_date": date(2023, 3, 15),
            "buy_date": date(2023, 1, 28),
            "symbol": "STOCK1",
            "qty": 100,
            "sales": 35000.0,
            "cost": 28000.0,
            "fee": 0.0,
            "sell_price": 350.0,
            "buy_price": 280.0,
            "pnl": 7000.0
        },
        {
            "iid": 2,
            "template_id": 1,
            "sell_date": date(2023, 3, 19),
            "buy_date": date(2023, 2, 20),
            "symbol": "STOCK2",
            "qty": 400,
            "sales": 8000.0,
            "cost": 12000.0,
            "fee": 0.0,
            "sell_price": 20.0,
            "buy_price": 30.0,
            "pnl": -4000.0
        },
        {
            "iid": 4,
            "template_id": 1,
            "sell_date": date(2023, 1, 30),
            "buy_date": date(2023, 1, 29),
            "symbol": "STOCK1",
            "qty": 250,
            "sales": 67000.0,
            "cost": 73750.0,
            "fee": 0.0,
            "sell_price": 268.0,
            "buy_price": 295.0,
            "pnl": -6750.0
        }
    ]

