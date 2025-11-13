# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 21:12:25 2025

@author: JPatrick
"""

from pprint import pprint

# %%

def get_unique_prefixes_in_order(d):
    """
    Extract unique prefixes from dictionary keys,
    preserving the original order of appearance,
    but removing only *consecutive* duplicates.

    Example
    -------
    >>> d = {
    ...   "PRODQ_FR_011": "...",
    ...   "PRODQ_FR_012": "...",
    ...   "EXPTOTQ_FR_011": "...",
    ...   "EXPTOTQ_FR_012": "...",
    ...   "PRODQ_DE_011": "..."
    ... }
    >>> prefixes, count = get_unique_prefixes_in_order(d)
    >>> prefixes
    ['PRODQ', 'EXPTOTQ', 'PRODQ']
    >>> count
    3

    Parameters
    ----------
    d : dict
        Any Python dictionary whose keys contain underscores "_".

    Returns
    -------
    tuple[list[str], int]
        A tuple containing:
          - the list of unique prefixes in order (without consecutive duplicates)
          - the total count of such prefixes
    """
    prefixes_in_order = []
    last_prefix = None

    for key in d.keys():
        prefix = key.split("_")[0]
        if prefix != last_prefix:
            prefixes_in_order.append(prefix)
            last_prefix = prefix

    return prefixes_in_order, len(prefixes_in_order)

# %%

def preview_dict(dic, n=1, use_pprint=False):
    """
    Affiche les n premières et n dernières paires clé:valeur d'un dictionnaire.

    Paramètres :
            d : dict
                Dictionnaire à visualiser.
            n : int, optionnel
                Nombre d'éléments à afficher en début et en fin (défaut = 5).
            use_pprint : bool, optionnel
                Si True (défaut), utilise pprint pour un affichage formaté.
    """
    if not isinstance(dic, dict):
        raise TypeError("L'objet fourni n'est pas un dictionnaire.")
    items = list(dic.items())
    total = len(items)
    if total == 0:
        print("(dictionnaire vide)")
        return
    print()
    # print("---------------------------------")
    # print(f">>> {min(n, total)} première(s) entrée(s) :")
    first_part = dict(items[:n])
    # print()
    if use_pprint:
        pprint(first_part)
    else:
        for k, v in first_part.items():
            print(f"> {k}: {v}")
    if total > n:
        print(".../...")
        # print(f">>> {min(n, total)} dernière(s) entrée(s) :")
        last_part = dict(items[-n:])
        # print()
        if use_pprint:
            pprint(last_part)
        else:
            for k, v in last_part.items():
                print(f"> {k}: {v}")           
    print()
    # print("---------------------------------")
    print(f"✅ Total entries into dictionary: {len(dic)}")
    n_unique_prefixes = len({k.split("_")[0] for k in dic})
    unique_prefixes = sorted({k.split("_")[0] for k in dic})
    unique_prefixes_in_dict_order, n_unique_prefixes_in_key_order = get_unique_prefixes_in_order(dic)
    if unique_prefixes != unique_prefixes_in_dict_order:
        print(f"✅ List of the {n_unique_prefixes} unique prefix(es) found into dictionary (in ALPHABETIC order):")
        print(unique_prefixes)
    print(f"✅ List of the {n_unique_prefixes_in_key_order} prefix(es) found into dictionary (in order of apparition into dictionary):")
    print(unique_prefixes_in_dict_order)

