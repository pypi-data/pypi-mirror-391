# -*- coding: utf-8 -*-
"""
Created on Thu Nov  6 00:53:48 2025

@author: JPatrick
"""

import sys, os
from pprint import pprint

source_filepath = os.path.abspath("G:/OneDrive/SEURECO/_dev/python/pyiode")
if source_filepath not in sys.path:
    sys.path.insert(0, source_filepath)
    
from Cls_CitationsProcessor_v0_3 import CitationsProcessor

from Mod_GeneralUtilities import report_system_memory, report_object_memory, invert_dict_keys_values
from Mod_UtilitiesForIODE import parse_codes_to_dict
from Mod_RdAndCitationsDataForIODE import (
    all_citation_country_list_cohortes_2000_2023,
    nemesis_countries_eu27_and_additionals,
    nemesis_countries_including_rest_of_world,
    parent_child_25s_nace_aggregates_map
)
from Mod_PatentsFamiliesAndCitationValuesAggregatedOnTechs import (
    Patents_Families_8Values_Aggregated_On_Techs_GJD,
    Patents_Citations_64Values_Aggregated_On_Techs_GJD_Citing_x_GJD_Cited
)

import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option("display.expand_frame_repr", False)

dict_numeric_nacecodes_to_aggregate25s = invert_dict_keys_values(parent_child_25s_nace_aggregates_map)

print("Mapping of digital NACE codes to 25S aggregates :")
print("=============================================== :")
print(dict_numeric_nacecodes_to_aggregate25s)

# print(dictionnaire_codes_nace)

# Pour renommer/regrouper les citations de ces 4 pays sous "RW" :
nemesis_country_RoW_mapping_for_citations = {
    'SG': "RW",
    'IL': "RW",
    'TW': "RW",
    'CL': "RW"
}

citing_countries_to_remove = sorted(
    all_citation_country_list_cohortes_2000_2023 # Ensemble des codes pays présents dans cohortes
    - nemesis_countries_eu27_and_additionals # EU27 + "Pays additionnels" SANS "reste du monde"
)
cited_countries_to_remove = sorted(
    all_citation_country_list_cohortes_2000_2023
    - nemesis_countries_including_rest_of_world
)

# %%

dataframe_header_map = {
    "time_cohort_citing_fam": "cohort_citing_fam",
    "Cited_Inv_Country": "CitedCTY",
    "Cited_nace2_code": "CitedNAC",
    "Cited_has_Green": "CitedGRN",
    "Cited_has_JTag": "CitedJTG",
    "Cited_has_WIPO_Digtl": "CitedDIG",
    "Citing_Inv_Country": "CitingCTY",
    "Citing_nace2_code": "CitingNAC",
    "Citing_has_Green": "CitingGRN",
    "Citing_has_JTag": "CitingJTG",
    "Citing_has_WIPO_Digtl": "CitingDIG",
    "fr_nr_citations": "Citations",
}

report_system_memory()

# Répertoire d'accès aux fichiers de citations :
fract_cit_filepath = "G:/OneDrive/SEURECO/fractional_citations (Maastricht)/20251017 Download Zenodo"
# Fichier d'entrée de Fractional_Citations :
input_csv_filename  = f"{fract_cit_filepath}/Fractional_Citations_6_yearlyCohorts_Of_CitingFam_backward_2012-2023.csv"
# Fichier de sortie (SANS le PATH NI l'EXTENSION)
output_filename = os.path.splitext(os.path.basename(input_csv_filename))[0]
output_filename = f"Aggregated_{output_filename}"

nrows=250

# Création du processeur avec utilisation du logger "SimplePrinter" interne par défaut :
cp = CitationsProcessor()

print("Loading DataFrame from CSV...")
report_load = cp.load_csv(
    inputfile=input_csv_filename,
    nrows=nrows,                     # ➜ changer à None pour charger tout
    dtype_hint="compact",            # ➜ pour limiter l’usage RAM
    use_pyarrow=True
)
print("\n✅ DataFrame loaded from CSV !")

# =======================================================================
# Enchaînement des traitements sur les CITATIONS chargées depuis le CSV :
cp.drop_columns(cols={"time_cohort_citing_fam"})
# --- Suppression des lignes dont les codes pays ne sont pas renseignés dans le fichier CSV (valeurs nulles) ---
cp.filter_anomalies(required_cols=None)
# --- Suppression des lignes dont le code NACE est "NtAv" (non disponible) ---
cp.filter_sectors(action="delete-if-cited-or-citing", sectors="NtAv")
# --- Suppression de toutes les lignes où le pays cité ou citant est "UK" ---
#     (afin de libérer le code "UK" pour un éventuel remappage ultérieur)
cp.filter_countries(action="delete-if-cited-or-citing", countries="UK")
# --- Remplacement du code pays "GB" par "UK" dans toutes les colonnes concernées ---
cp.replace_codes(mapping={"GB": "UK"}, target="country", scope="both")
# --- Remappage des codes pays cités selon le dictionnaire Nemesis "Rest of the World" ---
cp.replace_codes(mapping=nemesis_country_RoW_mapping_for_citations, target="country", scope="cited")
# --- Suppression des lignes correspondant aux pays à retirer côté "citant" (Nemesis + ROW) ---
cp.filter_countries(action="delete-if-citing", countries=citing_countries_to_remove)
# --- Suppression des lignes correspondant aux pays à retirer côté "cité" (Nemesis + ROW) ---
cp.filter_countries(action="delete-if-cited", countries=cited_countries_to_remove)
# --- Remappage des codes NACE pour passer des codes "Maastricht" vers codes "25S" ---
#     (exemple : {'10', '10.5', '11', '12'} => 'C10T12')
cp.replace_codes(mapping=dict_numeric_nacecodes_to_aggregate25s, target="sector", scope="both")
# --- Regroupement des doublons : agrège les lignes identiques en sommant la colonne "fr_nr_citations" ---
cp.group_duplicates("fr_nr_citations")
# =======================================================================

# --- Récupération du dataframe final et export vers CSV ---
if nrows==None:
    suffix="_ALL_lines"
else:
    suffix=f"_{nrows}_lines"

df = cp.save_as(output_filename, type="csv", replace=True, suffix=suffix)
    
if True:
    # --- Renommage des colonnes pour des noms plus courts ---
    cp.rename_columns(dataframe_header_map)
    # --- Affichage partiel du dataframe (11 premières colonnes) ---
    print(cp.get_df().iloc[:, :11])
    # df = cp.get_df()
    # report_object_memory(df, detail=True)
    """
    cat Grouped_Fractional_Citations_6_yearlyCohorts_Of_CitingFam_backward_2018-2023.csv | awk -F, 'NR>1 {key = $8 $9 $10 " use-> " $3 $4 $5; sum[key] += $11} END {for (k in sum) printf "%s : %10d\n", k, int(sum[k])}' | sort |grep -E "(100|010|001) :" | sort -k3
    
    """
    inputfile = f"{fract_cit_filepath}/{output_filename}{suffix}.csv"
    print("Loading DataFrame from NEW CSV...")
    report_load = cp.load_csv(
        inputfile=inputfile,
        nrows=nrows,      # ➜ change à None pour charger tout
        dtype_hint="compact",
        use_pyarrow=True
    )
    print("✅ DataFrame load from NEW CSV !")

cp.split_by_technos(
    split_rule="split_citations",
    add_combo_count_col=False,
    tol_sum_check=10,
    group=True
    )

if nrows==None:
    suffix="_Split_ALL_lines"
else:
    suffix=f"_Split_{nrows}_lines"

df = cp.save_as(output_filename, type="csv", replace=True, suffix=suffix)

cp.rename_columns(dataframe_header_map)
# --- Affichage partiel du dataframe (11 premières colonnes) ---

print()

print(cp.get_df().iloc[:, :11])



