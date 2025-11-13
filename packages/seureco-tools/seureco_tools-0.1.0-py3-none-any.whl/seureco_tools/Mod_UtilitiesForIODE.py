# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 21:26:20 2025

@author: JPatrick


Module permettant de définir et de regrouper facilement des "dimensions" 
utilisées dans la génération automatisée d'identités ou d'équations.

Chaque dimension (c0, c1, s0, s1, t0, t1) représente une liste de codes 
(caractères) correspondant à une catégorie précise (pays, secteurs, technologies).

Ce module s'appuie sur les dataclasses pour simplifier la création 
d'objets structurés, tout en offrant une validation de base.
"""

from dataclasses import dataclass
from typing import List, Optional

import random

def parse_codes_to_dict(s: str, decimal_only: bool = False) -> dict:
    """
    EN:
    Parse a space-separated string of numeric or alphanumeric tokens and convert
    them into a dictionary. Keys are always the original strings.
    
    If the token is a number:
        - The value stored is the integer part of that number.
    If the token is not a number:
        - The token is ignored if `decimal_only=True`
        - Else, the token is stored with itself as a value
    
    Parameter:
        decimal_only (bool):
            - True → only store tokens that look like decimal numbers (contain a dot)
            - False → store both integers and decimals; non-numeric entries stored as is
    
    FR :
    Analyse une chaîne contenant des valeurs séparées par des espaces, et les
    transforme en dictionnaire. Les clés sont les valeurs exactes de la chaîne.
    
    Si la valeur est un nombre :
        - on stocke la partie entière du nombre (ex: "20.42" → 20)
    Si ce n'est pas un nombre :
        - la valeur est ignorée si `decimal_only=True`
        - sinon la valeur stockée est le token lui-même
    
    Paramètre :
        decimal_only (bool) :
            - True → on NE retient que les nombres décimaux (ayant un point)
            - False → entiers et décimaux acceptés ; valeurs non numériques conservées
    """

    result = {}  # Dictionnaire à remplir

    # On parcourt chaque élément (séparé par les espaces)
    for token in s.split():

        # CAS 1 : filtrage des tokens non décimaux si decimal_only=True
        if decimal_only and "." not in token:
            # On passe au token suivant sans rien ajouter au dict
            continue

        try:
            # On tente de convertir le token en nombre décimal
            # Si c'est un succès → on prend la partie entière
            value = int(float(token))

        except ValueError:
            # Le token n'est PAS un nombre
            if decimal_only:
                # En mode "décimaux uniquement", on ignore les non numériques
                continue
            else:
                # Sinon → on les garde en tant que texte
                value = token

        # On enregistre dans le dictionnaire final
        result[token] = value

    return result


def parse_codes_to_dict_OLD(s: str) -> dict:
    """
    EN:
    Parse a space-separated string of numeric or alphanumeric codes and convert
    them into a dictionary. Keys are the original tokens as strings. If the token
    represents a number (integer or decimal), the value will be the integer part
    of that number. If the token is not a number, the value will be the token
    itself.

    Example:
        "10 20.5 NtAv" →
        {
            "10": 10,
            "20.5": 20,
            "NtAv": "NtAv"
        }

    FR :
    Analyse une chaîne contenant des codes séparés par des espaces, et les
    transforme en dictionnaire. Les clés sont les valeurs exactes présentes dans
    la chaîne. Si la valeur est un nombre (entier ou décimal), la valeur du
    dictionnaire sera sa partie entière. Si la valeur ne peut pas être interprétée
    comme un nombre, alors la clé sera aussi la valeur.

    Exemple :
        "10 20.5 NtAv" →
        {
            "10": 10,
            "20.5": 20,
            "NtAv": "NtAv"
        }
    """

    result = {}  # Dictionnaire dans lequel nous allons stocker nos résultats

    # On découpe la chaîne sur les espaces pour obtenir chaque élément séparément
    for token in s.split():

        try:
            # Essai de convertir le token en nombre décimal (float)
            # Si cela fonctionne, on prend seulement la partie entière avec int()
            value = int(float(token))

        except ValueError:
            # Si on arrive ici, cela signifie que le token n'est PAS un nombre
            # Exemples : "NtAv", "ABC", etc.
            # Dans ce cas, on met le token lui-même comme valeur
            value = token

        # On ajoute dans le dictionnaire la clé (token original) + sa valeur calculée
        result[token] = value

    # On retourne le dictionnaire final à l'appelant
    return result

@dataclass
class Dimensions:
    """
    Conteneur regroupant jusqu'à six dimensions optionnelles :
    
    - c0, c1 : dimensions basées sur les pays (ex. : codes ISO alpha-2)
    - s0, s1 : dimensions basées sur les secteurs d'activité (ex. : codes NACE)
    - t0, t1 : dimensions basées sur les technologies (ex. : Green, Digital, etc.)
    
    Chaque dimension est une liste (Python `list[str]`) ou peut rester `None` 
    si elle n'est pas utilisée dans un contexte donné.
    
    Exemple d'utilisation :
    ----------------------
    >>> dims = Dimensions(c0=["FR", "DE"], s0=["C10T12"])
    >>> dims.c0
    ['FR', 'DE']
    >>> dims.active_dimensions()
    {'c0': ['FR', 'DE'], 's0': ['C10T12']}
    
    L'intérêt de cette classe est d'éviter de transmettre plusieurs paramètres 
    distincts à chaque appel de fonction : un seul objet `Dimensions` suffit.
    """

    C0: Optional[List[str]] = None
    C1: Optional[List[str]] = None
    S0: Optional[List[str]] = None
    S1: Optional[List[str]] = None
    T0: Optional[List[str]] = None
    T1: Optional[List[str]] = None

    def __post_init__(self):
        """
        Méthode spéciale appelée automatiquement juste après l'initialisation.
        
        Elle vérifie que seules les dimensions reconnues sont utilisées.
        Cela permet d'éviter les erreurs de frappe ou l'ajout involontaire 
        d'une dimension qui ne serait pas gérée par le reste du programme.
        
        Si un nom d'attribut incorrect est détecté, une erreur explicite est levée.
        """
        allowed = {"C0", "C1", "S0", "S1", "T0", "T1"}
        for k in vars(self).keys():
            if k not in allowed:
                raise ValueError(f"Dimension inconnue : {k}")

    def active_dimensions(self):
        """
        Retourne uniquement les dimensions définies (non nulles).
        
        Cela facilite le traitement dans les boucles de génération d'équations,
        en n'incluant que les dimensions réellement utilisées.
        
        Retour :
        --------
        dict : un dictionnaire {nom_dimension: liste_de_valeurs}
        
        Exemple :
        >>> dims = Dimensions(c0=["FR"], s1=["C10"])
        >>> dims.active_dimensions()
        {'c0': ['FR'], 's1': ['C10']}
        """
        return {
            k: v for k, v in vars(self).items()
            if v is not None
        }

def create_random_values_in_dict(C0=None, S0=None, T0=None, C1=None, S1=None, T1=None, trace=0):
    """
    Génère un dictionnaire de coefficients aléatoires indexé par les combinaisons
    des dimensions fournies. Toute dimension valant None est ignorée.

    Paramètres :
      - C0, S0, T0, C1, S1, T1 : listes OU None
      - trace :
          0 = aucune sortie console
          1 = affichage compact (sans listes de valeurs)
          2 = affichage complet (y compris listes de valeurs)
    """

    # Préparation des dimensions actives, triées alphabétiquement pour stabilité
    all_dims = [("C0", C0), ("S0", S0), ("T0", T0),
                ("C1", C1), ("S1", S1), ("T1", T1)]

    labels = []
    loops = []

    for name, dim in all_dims:
        if dim is not None:
            labels.append(name)
            loops.append(sorted(dim))

    # --------------------------------------------------------
    # SECTION AFFICHAGE DIMENSIONS (différenciée par trace)
    # --------------------------------------------------------
    if trace >= 1:
        print("\n=== INPUT DIMENSIONS ===")

        if trace == 1:
            # Format dictionnaire compact : cardinalités seulement
            summary = {
                name: (len(dim) if dim is not None else "Empty")
                for name, dim in all_dims
            }
            print("Input dimensions and cardinalities : ", end="")
            print(summary)

        elif trace == 2:
            # Détail complet : cardinalité + liste des valeurs
            print(f"Active dimensions count : {len(loops)}")
            for name, dim in all_dims:
                if dim is None:
                    print(f"- {name} : Empty")
                else:
                    sorted_dim = sorted(dim)
                    print(f"- {name} ({len(sorted_dim)} values) : {', '.join(sorted_dim)}")
        # print("")

    # --------------------------------------------------------
    # Nombre attendu de combinaisons (pour cohérence utilisateur)
    # --------------------------------------------------------
    total_expected = 1
    for dim in loops:
        total_expected *= len(dim)

    if trace >= 1:
        print(f"Total expected combinations : {total_expected}")
        print("")

    # --------------------------------------------------------
    # Génération récursive des clés
    # --------------------------------------------------------
    result = {}

    def rec(prefix, level):
        """
        Fonction récursive (FR) :
        - prefix = liste de segments de clé déjà construits
        - level  = profondeur courante dans la hiérarchie des dimensions
        """
        if level == len(loops):
            key = "_".join(prefix)
            result[key] = random.uniform(0, 100)
            return
        for val in loops[level]:
            rec(prefix + [val], level + 1)

    rec([], 0)

    # --------------------------------------------------------
    # SECTION FIN D'AFFICHAGE (inchangée par rapport à la version précédente)
    # --------------------------------------------------------
    if trace >= 1:
        print("=== OUTPUT SUMMARY ===")
        print(f"Generated items : {len(result)}")

        if len(result) > 0:
            sorted_keys = sorted(result.keys())
            # VARIANTE d'affichage n°1 : Key format order : ['C0', 'S0', 'T0', 'C1', 'S1', 'T1']          
            # print(f"Key format order   : {labels}")
            # VARIANTE d'affichage n°1 : Key format order : '{C0}_{S0}_{T0}_{C1}_{S1}_{T1}'
            # Explication de la façon de faire pour aide à la maintenance :
            # '_{'.join(labels) → transforme ['C0','S0',...] en C0}_{S0}_{...
            # '{{{}}}'.format(...) → entoure correctement avec { et } dans une f-string
            key_format = "_".join(f"{{{name}}}" for name in labels)
            print(f"Key format  : '{key_format}'")
            # --
            print(f"- First key : '{sorted_keys[0]}'")
            print(f"- Last key  : '{sorted_keys[-1]}'")
        print("====================================\n")

    return result

def create_random_values_in_dict_OLD(C0=None, S0=None, T0=None, C1=None, S1=None, T1=None):
    """
    Construit un dictionnaire dont les clés représentent toutes les combinaisons
    possibles des dimensions transmises, et dont les valeurs sont des nombres
    aléatoires compris entre 0 et 100.

    ➜ Toute dimension None est ignorée :
       - Exclue des boucles d’itération
       - Non incluse dans la clé générée

    Les valeurs de chaque dimension sont triées par ordre alphabétique,
    afin de garantir un ordre stable et reproductible des clés.
    """

    # ------------------------------------------------------------------
    # Constitution de la liste des dimensions actives (non-Nulles)
    # en respectant l'ordre logique C0, S0, T0, C1, S1, T1
    # Chaque dimension est triée alphabétiquement pour un ordre cohérent
    # ------------------------------------------------------------------
    loops = []   # listes de valeurs (après tri)
    labels = []  # noms des dimensions actives

    if C0 is not None: loops.append(sorted(C0)); labels.append("C0")
    if S0 is not None: loops.append(sorted(S0)); labels.append("S0")
    if T0 is not None: loops.append(sorted(T0)); labels.append("T0")
    if C1 is not None: loops.append(sorted(C1)); labels.append("C1")
    if S1 is not None: loops.append(sorted(S1)); labels.append("S1")
    if T1 is not None: loops.append(sorted(T1)); labels.append("T1")

    # ------------------------------------------------------------------
    # Affichage des dimensions retenues : nom + taille
    # ------------------------------------------------------------------
    print("\n=== INFORMATIONS DIMENSIONS ===")
    print(f"Nombre de dimensions actives : {len(loops)}")
    for name, dim in zip(labels, loops):
        print(f" - {name} : {len(dim)} valeurs")

    # ------------------------------------------------------------------
    # Calcul du nombre total de combinaisons pour information
    # (= produit des tailles)
    # ------------------------------------------------------------------
    total_expected = 1
    for dim in loops:
        total_expected *= len(dim)

    print(f"\nNombre total de combinaisons attendues : {total_expected}")

    # ------------------------------------------------------------------
    # Dictionnaire résultat
    # ------------------------------------------------------------------
    result = {}

    # ------------------------------------------------------------------
    # Fonction récursive générant toutes les combinaisons
    # ------------------------------------------------------------------
    def rec(prefix, level):
        """
        Fonction récursive :
        - prefix : liste des éléments déjà fixés dans la clé
        - level  : dimension en cours
        """
        if level == len(loops):
            key = "_".join(prefix)
            result[key] = random.uniform(0, 100)
            return

        for val in loops[level]:
            rec(prefix + [val], level + 1)

    # Lancement
    rec([], 0)

    # ------------------------------------------------------------------
    # Synthèse de génération
    # ------------------------------------------------------------------
    print("\n=== GÉNÉRATION DES CLÉS ===")
    print(f"Nombre d'éléments générés : {len(result)}")

    # Exemple de format de clé
    if len(result) > 0:
        # Clés triées pour cohérence d’affichage
        sorted_keys = sorted(result.keys())
        print(f"Format clé : segments séparés par '_' dans l'ordre {labels}")
        print(f" - Première clé : {sorted_keys[0]}")
        print(f" - Dernière clé  : {sorted_keys[-1]}")

    print("====================================\n")

    return result
