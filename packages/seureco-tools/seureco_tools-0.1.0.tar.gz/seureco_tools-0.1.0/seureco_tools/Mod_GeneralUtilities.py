# -*- coding: utf-8 -*-
"""
Created on Thu Nov  6 07:57:23 2025

@author: JPatrick
"""

import sys

def convert_2chars_codes_from_str_to_list(s: str) -> set[str]:
    """
    Découpe la chaîne sur un ou plusieurs espaces
    et renvoie une liste triée alphabétiquement
    de tous les éléments (sans aucun filtrage).

    Exemple :
        >>> s = "97 AB  AC   AD AE"
        >>> extract_tokens_sorted(s)
        ['97', 'AB', 'AC', 'AD', 'AE']
    """
    tokens = s.split()          # split() gère les espaces multiples
    return sorted(tokens)       # tri alphabétique

def list_to_set(tokens: list[str]) -> set[str]:
    """
    Convertit une liste de tokens en un set (ensemble Python).

    - Supprime automatiquement les doublons éventuels
    - Ne modifie pas la liste d’origine
    """
    return set(tokens)

def counts(df):
    """Return row count as int (safe when df is None)."""
    return 0 if df is None else len(df)

def report_system_memory():
    """Affiche un bilan mémoire RAM du système."""
    try:
        import psutil
    except ImportError:
        print("[INFO] psutil non installé. Installez-le avec : pip install psutil")
        return

    vm = psutil.virtual_memory()

    print("\n=== Bilan mémoire système (RAM) ===")
    print(f"Total RAM       : {vm.total / 1024**3:,.2f} Go")
    print(f"Utilisée        : {vm.used / 1024**3:,.2f} Go", end="")
    print(f" ({vm.percent:.1f}%)")
    print(f"Disponible      : {vm.available / 1024**3:,.2f} Go")
    print("===================================")

def report_object_memory(obj, show_ram=False, detail=False):
    """
    Affiche un bilan mémoire d'un objet Python.
    - Gestion spécifique DataFrame (infos optionnelles)
    - Fallback sys.getsizeof
    - Option show_ram pour bilan mémoire système
    """
    try:
        import pandas as pd
    except ImportError:
        pd = None
    
    try:
        from pympler import asizeof
        _has_pympler = True
    except ImportError:
        _has_pympler = False

    print("\n===== Bilan mémoire de l'objet =====")

    if pd is not None and isinstance(obj, pd.DataFrame):
        print("Type : pandas.DataFrame")

        # Stats globales
        rows, cols = obj.shape
        print(f"Lignes : {rows:,}")
        print(f"Colonnes : {cols:,}")
        print(f"Liste des colonnes : {list(obj.columns)}")

        if detail:
            print("\nDétail mémoire occupée par colonne (octets) :")
            print(obj.memory_usage(deep=True))

        total = obj.memory_usage(deep=True).sum()
        print(f"Total occupé par cet objet en mémoire : {total / 1024**2:,.3f} Mo")

    else:
        size = sys.getsizeof(obj)
        print(f"Type : {type(obj).__name__}")
        print(f"Taille sys.getsizeof : {size / 1024**2:,.6f} Mo")

        if _has_pympler:
            deep_size = asizeof.asizeof(obj)
            print(f"Taille réelle (pympler) : {deep_size / 1024**2:,.6f} Mo")
        else:
            print("[INFO] pympler non installé. Pour taille réelle : pip install pympler")

    print("====================================")

    if show_ram:
        report_system_memory()

def invert_dict_keys_values(mapping: dict, val_type: str = "list", sep: str = " ") -> dict:
    """
    Convert a dictionary between two structural formats:
    
    - Flat format:
        { element : group }
    - Long format:
        { group : [elements] }

    Auto-detection:
    - If values are lists/tuples → long → flat
    - If values are strings → flat → long
    - If val_type="string" and a value contains `sep`, it is treated as a
      serialized list and automatically split.

    Example
    -------
    Long → Flat:
        { "Europe": ["FR", "DE", "IT"] }
        → { "FR": "Europe", "DE": "Europe", "IT": "Europe" }

    Flat → Long:
        { "FR": "Europe", "DE": "Europe", "IT": "Europe" }
        → { "Europe": ["FR", "DE", "IT"] }

    Parameters
    ----------
    mapping : dict
        Input dictionary in flat or long form.
    val_type : str
        "list" (default) → output values stored as lists
        "string" → output values concatenated using `sep`
    sep : str
        Separator for joining/splitting values when val_type="string".

    Returns
    -------
    dict
        Converted dictionary.

    """

    if not mapping:
        return {}

    value_types = {type(v) for v in mapping.values()}

    # CAS LONG → FLAT
    if value_types.issubset({list, tuple}):
        out = {}
        for alpha_code, numeric_list in mapping.items():
            for numeric_code in numeric_list:
                out[numeric_code] = alpha_code
        return out

    # CAS FLAT → LONG
    if value_types == {str}:
        out = {}
        for numeric_code, alpha_code in mapping.items():

            # Si valeur sérialisée (string contenant sep)
            if sep and sep in alpha_code:
                for sub in alpha_code.split(sep):
                    out.setdefault(sub, []).append(numeric_code)
                continue

            # Cas normal
            out.setdefault(alpha_code, []).append(numeric_code)

        if val_type == "string":
            return {k: sep.join(v_list) for k, v_list in out.items()}
        return out

    # ERREUR → mélange de types
    raise TypeError("Values must be all strings (flat) or all lists/tuples (long).")

dict_tests = {
    'C10T12': ['10', '10.5', '11', '12']
    }

