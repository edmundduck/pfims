import anvil.server

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def upper_dict_keys(rows, key_list=None):
    """
    Change the key(s) in a dict to be upper case.

    If key_list is None, then all keys in a dict will be changed to upper case, otherwise only change those found in key_list.

    Parameters:
        key_list (list): List of key requiring to be upper case.

    Returns:
        result (list of dict): List of dict containing keys in upper case.
    """
    DL = {}
    if rows is not None and len(rows) > 0:
        for k in rows[0].keys():
            if k.upper() in key_list or not key_list:
                DL[k.upper()] = [row[k] for row in rows]
            else:
                DL[k] = [row[k] for row in rows]  
    result = to_list_of_dict(DL)
    return result

def to_list_of_dict(DL):
    """
    Convert the structure of dict of list (DL) to list of dict (LD).

    Parameters:
        DL (dict of list): Dict of list.

    Returns:
        LD (list of dict): List of dict.
    """
    if DL is not None:
        LD = [dict(zip(DL, col)) for col in zip(*DL.values())]
    else:
        LD = []
    return LD

def to_dict_of_list(LD):
    """
    Convert the structure of list of dict (LD) to dict of list (DL).

    Parameters:
        LD (list of dict): List of dict.

    Returns:
        DL (dict of list): Dict of list.
    """
    if LD is not None and len(LD) > 0:
        if isinstance(LD[0], dict):
            DL = {k: [dic[k] for dic in LD] for k in LD[0]}
        else:
        # psycopg2 is not available in client side.
        # elif isinstance(LD[0], psycopg2.extras.DictRow):
            DL = {k: [dic[k] for dic in LD] for k in LD[0].keys()}
    else:
        DL = {}
    return DL

def get_account_currency_symbol(acct_id):
    """
    Return either the currency symbol or abbreviation of a given account ID.

    Currency abbreviation will only be returned if symbol cannot be found or empty.

    Parameters:
        acct_id (int): Account ID.

    Returns:
        result (string): Currency symbol or abbreviation of the given account ID.
    """
    from ..Entities.Account import Account
    from ..Utils.ClientCache import ClientCache
    from ..Utils.Constants import CacheKey
    cache = ClientCache(CacheKey.DICT_ACCOUNT_SYMBOL)

    if any((cache.is_empty(), cache.is_expired())):
        DL = {}
        for acct in anvil.server.call('generate_accounts_list'):
            # Has dependency on how data columns are retrieved in DB
            # TODO - 'symbol' is hardcoded
            DL[acct[Account.field_id()]] = acct['symbol'] if acct['symbol'] else acct[Account.field_base_currency()] if acct[Account.field_base_currency()] else ""
        cache.set_cache(DL)
        return DL.get(acct_id)
    else:
        return cache.get_cache().get(acct_id)
