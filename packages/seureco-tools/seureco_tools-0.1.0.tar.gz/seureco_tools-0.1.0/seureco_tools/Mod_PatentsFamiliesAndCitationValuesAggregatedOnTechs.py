# -*- coding: utf-8 -*-
"""
Created on Sun Nov  9 20:32:24 2025

@author: JPatrick
"""
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option("display.expand_frame_repr", False)
pd.set_option('display.float_format', lambda x: f"{x:.6f}")

import pandas as pd
from io import StringIO

# %%
 
# NOMBRE DE FAMILLES DE BREVETS AGREGEES SUR LES COMBINAISONS DE TECHNOS : GREEN x JTAG x DIGITAL
"""
Pour recréer les données ci-besoin, à partir d'une fenêtre ''GIT Bash' :
FICHIER UTILISE POUR PRODUIRE CES DONNEES : "DetailedTech_Fractional_FamilyCounts_From2000_Onwards_FilterIs_GT0_Internatnl_Or_GT1_Natnl.csv"
    cd /g/OneDrive/SEURECO/rd_by_techs/data_in/CSV
    cat DetailedTech_Fractional_FamilyCounts_From2000_Onwards_FilterIs_GT0_Internatnl_Or_GT1_Natnl.csv 
     | awk -F, 'NR==1 {print "Grn_Jtg_Dig,fr_nr_families"; next} NR>1 {key = $4 $5 $6 ; sum[key] += $NF} END {for (k in sum) printf "%s,%0.15f\n", k, sum[k]}' 
     | sort
NB : La commande finale "sort" place l'entête 'Grn_Jtg_Dig,fr_nr_families' APRES les données
     Il faut donc déplacer cette ligne en tête si besoin, pour insertion dans un dataframe.
"""
data = """
Grn_Jtg_Dig,fr_nr_families
000,3539755.013333817943931
001,60210.000242752699705
010,1662384.921908361371607
011,138512.204467134113656
100,580003.003521036938764
101,5525.000036603907574
110,109161.910907869954826
111,8994.833000262246060
"""

Patents_Families_8Values_Aggregated_On_Techs_GJD = pd.read_csv(StringIO(data), dtype={'Grn_Jtg_Dig': str})
# print(Patents_Families_8Values_Aggregated_On_Techs_GJD)

# %%

# NOMBRE DE CITATIONS ENTRE BREVETS, AGREGEES SUR LES COMBINAISONS DE TECHNOS : GREEN x JTAG x DIGITAL "CITANTES x CITEES"
"""
Pour recréer les données ci-besoin, à partir d'une fenêtre ''GIT Bash' :
FICHIER UTILISE POUR PRODUIRE CES DONNEES : "Aggregated_Fractional_Citations_6_yearlyCohorts_Of_CitingFam_backward_2012-2023_ALL_lines.csv"
    cd /g/OneDrive/SEURECO/rd_by_techs/data_in/CSV
    cat Aggregated_Fractional_Citations_6_yearlyCohorts_Of_CitingFam_backward_2012-2023_ALL_lines.csv 
    | awk -F, 'NR==1 {print "Grn_Jtg_Dig_Citing,Grn_Jtag_Dig_Cited,fr_nr_citations"; next} NR>1 {key = $8 $9 $10 "," $3 $4 $5; sum[key] += $11} END {for (k in sum) printf "%s,%0.3f\n", k, sum[k]}' 
    | sort
NB : La commande finale "sort" place l'entête 'Grn_Jtg_Dig_Citing,Grn_Jtag_Dig_Cited,fr_nr_citations' APRES les données
     Il faut donc déplacer cette ligne en tête si besoin, pour insertion dans un dataframe.
"""

data = """
Grn_Jtg_Dig_Citing,Grn_Jtag_Dig_Cited,fr_nr_citations
000,000,1586007.021411266410723
000,001,17714.116384031851339
000,010,147041.417039582767757
000,011,15309.103676638032994
000,100,130992.467693627622793
000,101,1615.109685886095349
000,110,13452.369303213858075
000,111,2031.288246093178032
001,000,18517.848853532355861
001,001,18226.572961100664543
001,010,7277.891403823259679
001,011,9635.278286740398471
001,100,1059.708552558497104
001,101,696.238868173339824
001,110,430.027827986547777
001,111,619.687340613638867
010,000,116699.009047621104401
010,001,4787.578874013443965
010,010,778204.277458888711408
010,011,80485.015122295866604
010,100,9596.765797339226992
010,101,535.964783783726261
010,110,35163.500994081761746
010,111,5543.837211338752240
011,000,12621.117992068646345
011,001,6296.122957929187578
011,010,92371.498430521256523
011,011,73902.215174858880346
011,100,932.292332492777291
011,101,377.442821341034346
011,110,3030.404664384268017
011,111,3031.760536321265135
100,000,122793.511791054246714
100,001,1038.828128244508207
100,010,10462.809034866348156
100,011,997.652381465162307
100,100,275350.986457637103740
100,101,1616.322730295936481
100,110,15706.638658143499924
100,111,1500.696326836097796
101,000,1378.378463950027481
101,001,636.908721183103921
101,010,555.676966997325962
101,011,469.670394432565502
101,100,1640.239143593149947
101,101,491.353335560449864
101,110,534.760138140393678
101,111,400.427254537075328
110,000,9585.654739145144049
110,001,233.793405184509311
110,010,33287.770679979774286
110,011,2500.419965762020638
110,100,9111.444332093025878
110,101,345.760355495474698
110,110,26203.209811263426673
110,111,1836.465773370780198
111,000,1006.376592619183043
111,001,271.754099885198400
111,010,3341.507259284666816
111,011,1637.218598346712724
111,100,868.117724194542120
111,101,234.467754548929861
111,110,1394.254770960447786
111,111,909.748362904783676
"""

Patents_Citations_64Values_Aggregated_On_Techs_GJD_Citing_x_GJD_Cited = pd.read_csv(StringIO(data), dtype={'Grn_Jtg_Dig_Citing': str, 'Grn_Jtag_Dig_Cited': str})
# print(Patents_Citations_64Values_Aggregated_On_Techs_GJD_Citing_x_GJD_Cited)
