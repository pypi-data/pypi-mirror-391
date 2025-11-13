# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 21:38:09 2025

@author: JPatrick
"""

# Configuration de l'accès fichier externe utiles au fonctionnement du présent module

# ------------------------------------------------------------
import sys, os
source_filepath = os.path.abspath("G:/OneDrive/SEURECO/_dev/python/pyiode")
if source_filepath not in sys.path:
    sys.path.insert(0, source_filepath)

output_filepath = f"{source_filepath}/output"  # Chemin de stockage des fichiers produits
# Création du dossier si besoin (optionnel)
# ------------------------------------------------------------

from pprint import pprint
from Cls_IdentityGenerator_v0_4 import IdentityGenerator

from Mod_RdAndCitationsDataForIODE import (
    eu27_countries,
    nemesis_subsectors,
    technos_families,
    c0, s0, t0
)

from Mod_UtilitiesForGUI import preview_dict

from Mod_UtilitiesForIODE import Dimensions, create_random_values_in_dict

# %%

def select_valid_coefs(coefs_dict, key):
    """
    Retourne coefs_dict[key] si >= max_value, sinon None.
    Si la clé n'existe pas : retourne None.
    """
    max_value = 0
    if not isinstance(key, str):
        return None
    value = coefs_dict.get(key)
    if value is None:
        return None
    return value if value >= max_value else None

# %%

c1=c0 ; s1=s0 ; t1=t0

# dims_test = Dimensions(
#     C0=eu27_countries,
#     S0=nemesis_subsectors,
#     T0=technos_families,
#     C1=eu27_countries,
#     S1=nemesis_subsectors,
#     T1=technos_families
# )

dims_test = Dimensions(
    C0=c0,
    S0=s0,
    T0=t0,
    C1=c1,
    S1=s1,
    T1=t1
)

maastricht_coefs_cst = create_random_values_in_dict(**dims_test.active_dimensions(), trace=2)

# preview_dict(maastricht_coefs_cst, n=1)

# %%

o = IdentityGenerator()

o.set_dimensions(**dims_test.active_dimensions())

o.set_debug(0)                      # Options disponibles : 0 | 1 | 2
# CI-DESSOUS: P1 = "Motif" de création du nom des IDENTITÉS IODE à créer
#             P2 = "Motif" de la façon de construire la fonction (somme de termes) de chacune des identités IODE
#             à travers la "déclinaison" des termes sur {C1}_{S1}_{T1
o.set_aggregate_mode("unique")      # Options disponibles : "unique" | "duplicates" | "count"
o.set_aggregate_skip_rules(None)
o.set_user_functions({"parent": lambda s: s[:2]})
o.get_dimensions()

o.set_weight_filter(
        max_terms=None,
        weight_fn=select_valid_coefs,
        weight_dict=maastricht_coefs_cst,
        key="{C0}_{S0}_{T0}_{C1}_{S1}_{T1}")

o.set_formula(variable="KNOW_{C0}_{S0}_{T0}", formula="{weight}*SRDUSE_{C1}_{S1}_{T1}")

identities = o.run(output="dict")

preview_dict(identities, n=1)

# print()
# identities = o.run(output="df")
# pprint(identities.head(3))

# identities = o.run(output="dict")
# preview_dict(identities, n=3)

# o.set_formula("KNOW_{C0}_{parent(S0)}_{S0}_{T0}", "{weight}*SRDUSE_{C1}_{S1}_{T1}")

# o.set_weight_filter(
#         weight_fn=get_maastricht_val,
#         weight_dict=select_valid_coefs,
#         key="{C0}_{S0}_{T0}_{C1}_{S1}_{T1}")

# print()
# #identities = o.run(output="df")

# identities = o.run(output="df")
# pprint(identities.head(3))

# #identities = o.run(output="csv", filepath=f"{output_filepath}/test.csv")
# identities = o.run(output="excel", filepath=f"{output_filepath}/test.xlsx")

# preview_dict(identities, n=1)

# # o.help()
# # o.help("aggregate_mode")
# # o.help("run")

print("\nTraitement terminé !")


