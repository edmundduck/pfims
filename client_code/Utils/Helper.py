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
        elif isinstance(LD[0], psycopg2.extras.DictRow):
            DL = {k: [dic[k] for dic in LD] for k in LD[0].keys()}
        else:
            raise TypeError(f"Only list of dict or list of DictCursor is supported.")
    else:
        DL = {}
    return DL
