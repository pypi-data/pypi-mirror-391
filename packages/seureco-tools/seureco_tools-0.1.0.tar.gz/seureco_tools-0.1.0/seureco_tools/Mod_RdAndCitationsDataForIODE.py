# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 20:46:06 2025

@author: JPatrick
"""

"""
    LISTE DE VALEURS ENTRANT DANS LA COMPOSITION DES DIFFERENTES "DIMENSIONS"
    UTILISEES POUR GENERER LES VARIABLES, IDENTITES ET EQUATIONS DANS IODE/NEMESIS
    AINSI QUE IODE/TWINRD.
"""

# %%

# A	   Agriculture, forestry, and fishing
# B	   Mining and quarrying
# C10_C12  Food, beverages and tobacco products
# C13_C15  Textiles, apparel and related products
# C16_C18  Wood, paper, printing and related products
# C19	Coke and refined petroleum products
# C20	Chemical industry
# C21	Pharmaceutical industry
# C22	Manufacture of rubber and plastic products
# C23	Manufacture of other non-metallic mineral products
# C24	Metallurgy
# C25	Fabricated metal products, except machinery and equipment
# C261 	Electronic components and boards
# C262	 Computers and peripheral equipment
# C263	 Communication equipment
# C264	 Consumer electronics
# C265	 Instruments for measuring, testing, navigation ; Watches & clocks
# C266	 Irradiation, electromedical and electrotherapeutic equipment
# C267	 Optical and photographic equipment
# C268	 Magnetic and optical media
# C27	 Electrical equipment
# C28	 Machinery and equipment n.e.c.
# C29	 Motor vehicle industry
# C30	 Manufacture of other transport equipment
# C31_ C33	Diverse goods and repair/installation of specialized eqpts
# D	    Electricity, gas, steam, and air conditioning supply
# E36	 Water production and distribution; sanitation, waste management
# E37_E39  Sewerage, waste management, materials recovery and remediation

# %%

# ENSEMBLE DES CODES PAYS PRESENTS DANS FICHIER DE BREVETS "FILTRES-2 PAYS" - PERIODE 2000 -> 2023
"""
FICHIER : "DetailedTech_Fractional_FamilyCounts_From2000_Onwards_FilterIs_GT0_Internatnl_Or_GT1_Natnl.csv""
"""
all_filtered_patents_country_list_2000_2023 = {
        "AB","AC","AD","AE","AF","AG","AI","AL","AM","AN","AO","AP","AQ","AR","AS","AT","AU","AW","AX","AZ",
        "BA","BB","BC","BD","BE","BF","BG","BH","BI","BJ","BL","BM","BN","BO","BQ","BR","BS","BT","BU","BV",
        "BW","BX","BY","BZ","CA","CC","CD","CF","CG","CH","CI","CK","CL","CM","CN","CO","CR","CS","CT","CU",
        "CV","CW","CY","CZ","DD","DE","DJ","DK","DM","DO","DR","DZ","EA","EC","EE","EG","EH","EM","EN","EP",
        "ER","ES","ET","FE","FI","FJ","FK","FL","FM","FN","FO","FR","FX","GA","GB","GC","GD","GE","GF","GG",
        "GH","GI","GL","GM","GN","GP","GQ","GR","GS","GT","GU","GY","HA","HD","HK","HL","HN","HR","HT","HU",
        "HW","IB","ID","IE","IL","IM","IN","IO","IQ","IR","IS","IT","JE","JM","JO","JP","JT","KA","KE","KG",
        "KH","KI","KM","KN","KP","KR","KT","KW","KY","KZ","LA","LB","LC","LE","LI","LK","LN","LR","LS","LT",
        "LU","LV","LY","MA","MB","MC","MD","ME","MG","MH","MI","MK","ML","MM","MN","MO","MP","MQ","MR","MS",
        "MT","MU","MV","MW","MX","MY","MZ","NA","NC","NE","NF","NG","NI","NJ","NL","NO","NP","NR","NU","NV",
        "NY","NZ","OA","OH","OM","ON","OR","PA","PE","PF","PG","PH","PI","PK","PL","PM","PN","PO","PR","PS",
        "PT","PW","PY","QA","QC","RE","RF","RJ","RO","RS","RU","RW","RZ","SA","SB","SC","SD","SE","SG","SH",
        "SI","SJ","SK","SL","SM","SN","SO","SP","SR","SS","ST","SU","SV","SW","SX","SY","SZ","TC","TD","TF",
        "TG","TH","TJ","TK","TL","TM","TN","TO","TP","TR","TT","TV","TW","TX","TY","TZ","UA","UC","UD","UG",
        "UI","UK","UL","UM","US","UT","UW","UX","UY","UZ","VA","VC","VE","VG","VI","VN","VU","WA","WF","WI",
        "WO","WS","WU","XK","XN","XP","YE","YS","YU","ZA","ZJ","ZM","ZW","ZZ"
}


# ENSEMBLE DES CODES PAYS PRESENTS DANS FICHIER "COHORTES" CITATIONS BREVETS (FORWARD) - PERIODE 2000 -> 2023
"""
FICHIER : "Fractional_Citations_6_yearlyCohorts_Of_CitingFam_backward.csv"
"""
all_citation_country_list_cohortes_2000_2023 = {
        "AB","AC","AD","AE","AF","AG","AI","AL","AM","AN","AO","AP","AQ","AR","AS","AT","AU","AW","AX","AZ",
        "BA","BB","BC","BD","BE","BF","BG","BH","BI","BJ","BL","BM","BN","BO","BQ","BR","BS","BT","BU","BV",
        "BW","BX","BY","BZ","CA","CC","CD","CF","CG","CH","CI","CK","CL","CM","CN","CO","CR","CS","CT","CU",
        "CV","CW","CY","CZ","DD","DE","DJ","DK","DM","DO","DR","DZ","EA","EC","EE","EG","EH","EM","EN","EP",
        "ER","ES","ET","EV","FE","FI","FJ","FK","FL","FM","FN","FO","FR","FX","GA","GB","GC","GD","GE","GF",
        "GG","GH","GI","GL","GM","GN","GP","GQ","GR","GS","GT","GU","GY","HA","HD","HI","HK","HL","HN","HR",
        "HT","HU","HW","IB","ID","IE","IL","IM","IN","IO","IQ","IR","IS","IT","JE","JM","JO","JP","JT","KA",
        "KE","KG","KH","KI","KM","KN","KP","KR","KS","KT","KW","KY","KZ","LA","LB","LC","LE","LI","LK","LN",
        "LR","LS","LT","LU","LV","LY","MA","MB","MC","MD","ME","MG","MH","MI","MK","ML","MM","MN","MO","MP",
        "MQ","MR","MS","MT","MU","MV","MW","MX","MY","MZ","NA","NC","NE","NF","NG","NH","NI","NJ","NL","NO",
        "NP","NR","NU","NV","NY","NZ","OA","OH","OM","ON","OR","PA","PE","PF","PG","PH","PI","PK","PL","PM",
        "PN","PO","PR","PS","PT","PW","PY","QA","QC","RE","RF","RI","RJ","RO","RS","RU","RW","RZ","SA","SB",
        "SC","SD","SE","SG","SH","SI","SJ","SK","SL","SM","SN","SO","SP","SR","SS","ST","SU","SV","SW","SX",
        "SY","SZ","TC","TD","TF","TG","TH","TJ","TK","TL","TM","TN","TO","TP","TR","TT","TV","TW","TX","TY",
        "TZ","UA","UC","UD","UG","UK","UL","UM","UR","US","UT","UW","UX","UY","UZ","VA","VC","VE","VG","VI",
        "VN","VU","WA","WF","WI","WO","WS","WU","XK","XN","XP","XX","YE","YS","YU","ZA","ZJ","ZM","ZW","ZZ",
        "97"
}

# LES 45 PAYS OBJETS DES TRAVAUX REALISES AU 1ER SEMESTRE 2025 POUR COMPLETER/ESTIMER R&D INCOMPLETE OU INCONNUE
# ATTENTION PAYS "UK" DANS CETTE ETUDE (ET DANS NEMESIS EN GENERAL)
# CORRESPOND AU CODE "GB" DANS FICHIERS DE "BREVETS" ET COHORTES DE "CITATIONS"
countries_with_known_rd_45c = {
    "AT", "AU", "BE", "BG", "BR", "CA", "CH", "CL", "CN", "CY", "CZ", "DE", "DK", "EE", "ES",
    "FI", "FR", "GR", "HR", "HU", "IE", "IL", "IN", "IS", "IT", "JP", "KR", "LT", "LU", "LV",
    "MT", "MX", "NL", "NO", "PL", "PT", "RO", "RU", "SE", "SG", "SI", "SK", "TW", "UK", "US"
}
eu27_countries = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES",
                  "FI", "FR", "GR", "HR", "HU", "IE", "IT", "LT", "LU",
                  "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"}

additional_countries_for_both_nemesis_and_twinrd = {"CH", "NO", "UK"}

# ================================================================================
# SPECIFIQUE "TWINRD" :
twinrd_RoW = {"AU", "BR", "CA", "CN", "IN", "JP", "KR", "MX", "RU", "RW", "US"} # NOTA : "IS" est dans ce "RW" (définit dans Nemesis)
twinrd_countries = eu27_countries | additional_countries_for_both_nemesis_and_twinrd | twinrd_RoW
all_twinrd_countries = twinrd_countries | twinrd_RoW

# ================================================================================
# SPECIFIQUE "NEW-NEMESIS" :
additional_countries_only_for_nemesis = {"IS"}
# NOTA : "IS" (ISLANDE) ne fait pas partie de EU27 et n'est pas présent dans les fichiers FIGARO
nemesis_countries_eu27_and_additionals = eu27_countries | additional_countries_for_both_nemesis_and_twinrd | additional_countries_only_for_nemesis
# NOTA : nemesis_countries nous intéresse en notion "CITING" dans le traitement des CITATIONS de BREVETS
nemesis_rest_of_world = {"AU", "BR", "CA", "CN", "IN", "JP", "KR", "MX", "RU", "RW", "US"} # NOTA : "IS" n'est PAS dans ce "RW" (définit dans Nemesis)
# ================================================================================

# ================================================================================

nemesis_countries_including_rest_of_world = nemesis_countries_eu27_and_additionals | nemesis_rest_of_world
# NOTA : all_countries nous intéresse en notion "CITED" (emprunt de connaissances) dans le traitement des CITATIONS de BREVETS
new_nemesis_RoW_for_citation = countries_with_known_rd_45c - nemesis_countries_including_rest_of_world

nemesis_countries_expect_eu27_countries = nemesis_countries_including_rest_of_world - eu27_countries

# %%

# BELOW theses codes are NEMESIS CODES, NOT NACE2 codes

nemesis_sectors_without_split = {
    '02', '03', '04', '05', '06', '07', '08', '09', '11', '12', '13', '14', '15',
    '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '29', '29B'
}

nemesis_subsectors = {
    '011', '012', '013',
    '101', '102',
    '271', '272', '273', '274',
    '281', '282', '283', '284',
    '301', '302', '303', '304', '305'
}

new_nemesis_sectors = nemesis_subsectors | nemesis_sectors_without_split

final_demand_categories = ['P3S13', 'P3S14', 'P3S15', 'P51G', 'P5M']

sectors_parent_child_map = {
        "01": ["011", "012", "013"],
        "10": ["101", "102"],              
        "27": ["271", "272", "273", "274"],  
        "28": ["281", "282", "283", "284"],       
        "30": ["301", "302", "303", "304", "305"]
}

# LIST APPLICABLE INTO "TECHS" PART OF PROJECT :

nemesis_sectors_without_split_for_techs = {
    '02', '03', '04', '05', '06', '07', '08', '09', '11', '12', '13', '14', '15',
    '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '29', '29B'
}

sectors_parent_child_map = {
        "01": ["011", "012", "013"],
        "10": ["101", "102"],              
        "26": ["261", "262", "263", "264", "265", "266", "267", "268"],  
        "27": ["271", "272", "273", "274"],  
        "28": ["281", "282", "283", "284"],       
        "30": ["301", "302", "303", "304", "305"]
}

parent_child_nemesis_nace_codes_map = {
    "01": ["011", "012", "013"],
    "02": ["02"],
    "03": ["03"],
    "04": ["04"],
    "05": ["05"],
    "06": ["06"],
    "07": ["07"],
    "08": ["08"],
    "09": ["09"],
    "10": ["101", "102"],
    "11": ["11"],
    "12": ["12"],
    "13": ["13"],
    "14": ["14"],
    "15": ["15"],
    "16": ["16"],
    "17": ["17"],
    "18": ["18"],
    "19": ["19"],
    "20": ["20"],
    "21": ["21"],
    "22": ["22"],
    "23": ["23"],
    "24": ["24"],
    "25": ["25"],
    "26": ["26"],
    "27": ["271", "272", "273", "274"],
    "28": ["281", "282", "283", "284"],
    "29": ["29"],
    "29B": ["29B"],
    "30": ["301", "302", "303", "304", "305"]
}

parent_child_25s_nace_aggregates_map = {
    'C10T12': ['10', '10.5', '11', '12'], 
    'C13T15': ['13', '14', '15'], 
    'C16T18': ['16', '17', '18.1'], 
    'C19': ['19'], 
    'C20': ['20.1', '20.2', '20.3', '20.4', '20.42', '20.5', '20.51', '20.6'], 
    'C21': ['21'], 
    'C22': ['22', '22.1', '22.2'], 
    'C23': ['23', '23.1', '23.3', '23.42', '23.5'],
    'C24': ['24', '24.46'], 
    'C25': ['25.1', '25.2', '25.3', '25.4', '25.5', '25.6', '25.7', '25.9', '25.94'],
    'C261': ['26.1', '26.11'], 
    'C262': ['26.2'],
    'C263': ['26.3'], 
    'C264': ['26.4'], 
    'C265': ['26.5', '26.51', '26.52'],
    'C266': ['26.6'], 
    'C267': ['26.7'], 
    'C268': ['26.8'],
    'C27': ['27.1', '27.12', '27.2', '27.3', '27.33', '27.4', '27.5', '27.9'],
    'C28': ['28.1', '28.11', '28.14', '28.21', '28.22', '28.23', '28.25', '28.29', '28.3', '28.4', '28.9', '28.92', '28.94', '28.95', '28.99'], 
    'C29': ['29.1', '29.3'],
    'C30': ['30'], 
    'C31T33': ['31', '32', '32.5', '32.9'],
    'F42T43': ['42.2', '42.91', '43'],
    'J62T63': ['62'], 'NtAv': ['NtAv']
}

# ENSEMBLE DES CODES NACE PRESENTS DANS FICHIER DE BREVETS "FILTRES-2 PAYS" - PERIODE 2000 -> 2023
"""
FICHIER : "DetailedTech_Fractional_FamilyCounts_From2000_Onwards_FilterIs_GT0_Internatnl_Or_GT1_Natnl.csv""
"""
filetred_patents_80_nace_codes = {
    "10","10.5","11","12","13","14","15","16","17","18.1","19","20.1","20.2","20.3","20.4",
    "20.42","20.5","20.51","20.6","21","22","22.1","22.2","23","23.1","23.3","23.42","23.5","24","24.46",
    "25.1","25.2","25.3","25.4","25.5","25.6","25.7","25.9","25.94","26.1","26.11","26.2","26.3","26.4","26.5",
    "26.51","26.52","26.6","26.7","26.8","27.1","27.12","27.2","27.3","27.33","27.4","27.5","27.9","28.1","28.11",
    "28.14","28.21","28.22","28.23","28.25","28.29","28.3","28.4","28.9","28.92","28.94","28.95","28.99","29.1","29.3",
    "30","31","32","32.5","32.9","42.2","42.91","43","62","NtAv"
}

# %%

technos_families = {"DIG", "GRN", "JTG", "OTH"}

# Mapping techno enfant → agrégat parent (CHild -> PaRent)
techs_ch_pr_map = {
    # Les agrégats sont leurs propres parents
    "AGR_GRN": "AGR_GRN",
    "AGR_JTG": "AGR_JTG",
    "AGR_DIG": "AGR_DIG",
    # Green
    "GRN_EM1": "AGR_GRN",
    "GRN_EM2": "AGR_GRN",
    "GRN_EM3": "AGR_GRN",
    "GRN_EM4": "AGR_GRN",
    "GRN_EM5": "AGR_GRN",
    "GRN_Y02A": "AGR_GRN",
    "GRN_Y02B": "AGR_GRN",
    "GRN_Y02C": "AGR_GRN",
    "GRN_Y02D": "AGR_GRN",
    "GRN_Y02E": "AGR_GRN",
    "GRN_Y02P": "AGR_GRN",
    "GRN_Y02T": "AGR_GRN",
    "GRN_Y02W": "AGR_GRN",
    "GRN_Y04S": "AGR_GRN",
    # JTag
    "JTG_01": "AGR_JTG",
    "JTG_02": "AGR_JTG",
    "JTG_03": "AGR_JTG",
    "JTG_04": "AGR_JTG",
    "JTG_05": "AGR_JTG",
    "JTG_06": "AGR_JTG",
    "JTG_07": "AGR_JTG",
    "JTG_08": "AGR_JTG",
    "JTG_09": "AGR_JTG",
    "JTG_10": "AGR_JTG",
    "JTG_11": "AGR_JTG",
    "JTG_12": "AGR_JTG",
    "JTG_13": "AGR_JTG",
    # Digital / WIPO
    "DIG_AIML": "AGR_DIG",
    "DIG_VRAR": "AGR_DIG",
    "DIG_AUTS": "AGR_DIG",
    "DIG_BIGD": "AGR_DIG",
    "DIG_BLCH": "AGR_DIG",
    "DIG_CLOUD": "AGR_DIG",
    "DIG_IOT": "AGR_DIG",
    "DIG_QUAN": "AGR_DIG",
    "DIG_ROBO": "AGR_DIG",
    "DIG_SMCT": "AGR_DIG",
    # Cas particuliers
    "TECH_OTH": "TECH_OTH",
    "TECH_ALL": "TECH_ALL"
}

# %%

"""
   CI-DESSOUS : DONNEES DE TEST
"""

c0 = {"AT", "DE", "FR"}

s0 = {"C10T12", "C13T15", "C16T18"}

t0 = technos_families



