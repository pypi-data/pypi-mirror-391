# -*- coding: utf-8 -*-
"""
Created on Thu Nov  6 00:47:19 2025

@author: JPatrick


CitationsProcessor.py

A simple, beginner-friendly processor for large patent citation flows.

EN (short):
- Load a large CSV (millions of rows) with RAM-friendly dtypes.
- Apply atomic transformations: drop columns, rename columns, filter anomalies,
  filter sectors/countries with controlled scope, replace codes, and group duplicates.
- All user messages are in English. Docstrings are bilingual (EN + FR).
- No print() inside: a logger (default SimplePrinter) receives human-readable reports.

FR (court) :
- Charge un gros CSV (millions de lignes) avec des types économes en mémoire.
- Transformations atomiques : suppression de colonnes, renommages, filtrage d’anomalies,
  filtrage secteurs/pays avec scope contrôlé, transcodage de codes, et regroupement de doublons.
- Aucun print() dans la classe : un logger (SimplePrinter par défaut) reçoit des rapports lisibles.
- Docstrings bilingues (EN + FR). Les messages affichés à l’utilisateur sont en anglais uniquement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd
import os

# =======================================================================
# Constantes de schéma par défaut (lisibles et faciles à adapter)
# =======================================================================

DEFAULT_COLUMNS = [
    "time_cohort_citing_fam",
    "Cited_Inv_Country",
    "Cited_nace2_code",
    "Cited_has_Green",
    "Cited_has_JTag",
    "Cited_has_WIPO_Digtl",
    "Citing_Inv_Country",
    "Citing_nace2_code",
    "Citing_has_Green",
    "Citing_has_JTag",
    "Citing_has_WIPO_Digtl",
    "fr_nr_citations",
]

# Noms de colonnes standards (pour éviter la magie dans le code)

# --- Input columns (as expected from CSV) ---
COL_CITED_COUNTRY = "Cited_Inv_Country"
COL_CITED_SECTOR  = "Cited_nace2_code"
COL_CITED_GRN     = "Cited_has_Green"
COL_CITED_JTG     = "Cited_has_JTag"
COL_CITED_DIG     = "Cited_has_WIPO_Digtl"

COL_CITING_COUNTRY = "Citing_Inv_Country"
COL_CITING_SECTOR  = "Citing_nace2_code"
COL_CITING_GRN     = "Citing_has_Green"
COL_CITING_JTG     = "Citing_has_JTag"
COL_CITING_DIG     = "Citing_has_WIPO_Digtl"

COL_CITATIONS = "fr_nr_citations"

# --- Additionnal columns used by "SPLIT BY TECHNOS" ---
COL_CITED_TEC   = "CitedTEC"
COL_CITING_TEC  = "CitingTEC"
COL_SPLIT_CIT   = "SplitCitations"
COL_COMBOS      = "Combos"
COL_PAIRKEY     = "PairKey"

# =======================================================================
# Utilitaires : "DECORATEURS" HABILLAGE DES ERREURS DE PARAMETRES D'ENTREE
# =======================================================================

def safe_call_with_hint(example_syntax: str):
    """
    EN: Wrapper that catches missing required keyword errors
    and provides a helpful syntax reminder for the user.

    FR: Wrapper qui intercepte les erreurs d'arguments manquants
    et propose un rappel de la syntaxe correcte.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TypeError as e:
                msg = str(e)
                # FR: Si manque un argument obligatoire keyword-only
                if "missing 1 required keyword-only argument" in msg:
                    raise TypeError(
                        f"Missing required argument.\n\n"
                        f"✅ Correct usage:\n{example_syntax}\n"
                    ) from None
                raise
        return wrapper
    return decorator

def require_keyword_args(example_syntax: str):
    """
    EN:
    Decorator ensuring that a method can only be called with keyword arguments
    (besides the implicit 'self'). If a positional argument is used, a helpful
    TypeError is raised with an example of the proper syntax.

    FR:
    Décorateur imposant l'utilisation obligatoire des arguments nommés
    (à l'exception implicite de 'self'). Si un argument positionnel est utilisé,
    une exception TypeError est levée avec un exemple de syntaxe correcte.

    Parameters
    ----------
    example_syntax : str
        A valid example call to show in case of misuse / Un exemple
        d'appel correct à afficher en cas de mauvaise utilisation.

    Returns
    -------
    function
        Wrapped function enforcing keyword-only usage / Fonction décorée
        imposant l'utilisation des arguments nommés.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # FR: Si plus d'un argument positionnel → cela signifie que l'appelant
            # a utilisé au moins un argument positionnel interdit (hors self)
            if len(args) > 1:
                raise TypeError(
                    f"Keyword-only arguments are required for '{func.__name__}'.\n\n"
                    f"✅ Correct usage:\n"
                    f"{example_syntax}\n\n"
                    f"💡 Tip: Always specify argument names explicitly.\n"
                )
            return func(*args, **kwargs)
        return wrapper

    return decorator

# =========================
# ANSI COLOR DEFINITIONS
# =========================

ANSI = {
    # Styles
    "reset": "\033[0m",
    "bold": "\033[1m",
    "underline": "\033[4m",
    "blink": "\033[5m",
    # Foreground (text) colors
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_black": "\033[90m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
    # Background colors
    "bg_black": "\033[40m",
    "bg_red": "\033[41m",
    "bg_green": "\033[42m",
    "bg_yellow": "\033[43m",
    "bg_blue": "\033[44m",
    "bg_magenta": "\033[45m",
    "bg_cyan": "\033[46m",
    "bg_white": "\033[47m",
    "bg_bright_black": "\033[100m",
    "bg_bright_red": "\033[101m",
    "bg_bright_green": "\033[102m",
    "bg_bright_yellow": "\033[103m",
    "bg_bright_blue": "\033[104m",
    "bg_bright_magenta": "\033[105m",
    "bg_bright_cyan": "\033[106m",
    "bg_bright_white": "\033[107m",
}

# =========================
# LOGGER CLASSES
# =========================

class SimplePrinter:
    """
    EN: Minimal logger used by default. Only provides .info(msg).
    FR: Logger minimal par défaut. Fournit uniquement .info(msg).
    """
    def info(self, msg: str) -> None:
        print()
        print(msg)

@dataclass
class OpReport:
    """
    EN: Small structured report returned by each operation.
    FR: Petit rapport structuré retourné par chaque opération.
    """
    name: str
    details: Dict[str, Any]

    def __str__(self) -> str:
        # Define colors for the service name: red on black
        fg = ANSI["bright_red"]
        bg = ANSI["bg_black"]
        style = ANSI["bold"]
        reset = ANSI["reset"]

        # Format details list
        items = ", ".join(f"{k}={v}" for k, v in self.details.items())

        # Colored service name between brackets
        return f"[{bg}{fg}{style}{self.name}{reset}] {items}"



@dataclass
class OpReport_old1:
    """
    EN: Small structured report returned by each operation.
    FR: Petit rapport structuré retourné par chaque opération.
    """
    name: str
    details: Dict[str, Any]

    def __str__(self) -> str:
        # EN user-facing message (concise)
        items = ", ".join(f"{k}={v}" for k, v in self.details.items())
        return f"[{self.name}] {items}"


# =======================================================================
# La classe principale
# =======================================================================

class CitationsProcessor:
    """
    EN
    ---
    A clear, beginner-friendly processor for patent citation flows.

    Key ideas:
    - Atomic methods (each step does one thing)
    - Memory-friendly dtypes (string / Int8 / float32) with a simple policy switch
    - No prints inside: all user-facing messages go to a configurable logger
    - English-only user messages; FR+EN docstrings; FR comments for maintainers

    FR
    ---
    Un processeur lisible et simple pour les flux de citations de brevets.

    Principes :
    - Méthodes atomiques (une seule responsabilité par méthode)
    - Types économes en mémoire (string / Int8 / float32) via une politique simple
    - Aucun print dans la classe : les messages vont à un logger configurable
    - Messages utilisateur en anglais ; docstrings FR+EN ; commentaires FR pédagogiques
    """

    # -------------------------------------------------------------------
    # Construction
    # -------------------------------------------------------------------
    def __init__(self, logger: Optional[Any] = None) -> None:
        """
        EN:
        Initialize the processor.
        - logger: any object exposing .info(str). If None, uses SimplePrinter().

        FR :
        Initialise le processeur.
        - logger : objet ayant une méthode .info(str). Si None, utilise SimplePrinter().
        """
        self.df: Optional[pd.DataFrame] = None
        self.logger = logger if logger is not None else SimplePrinter()
        self._last_loaded_path: Optional[str] = None

    # -------------------------------------------------------------------
    # Méthodes internes (utilitaires)
    # -------------------------------------------------------------------
    def _log(self, report: OpReport) -> None:
        """EN: Send the report to the logger. FR : Envoie le rapport au logger."""
        if self.logger is not None:
            self.logger.info(str(report))

    def _check_loaded(self) -> None:
        """
        EN: Ensure data is loaded before running any transformation.
        FR : Vérifie que des données sont chargées avant toute transformation.
        """
        if self.df is None:
            raise RuntimeError("No data loaded. Please call load_csv() first.")

    def _validate_scope(self, scope: str) -> Tuple[bool, bool, bool]:
        """
        EN:
        Validate scope and return a triple (apply_cited, apply_citing, is_both).
        'both' means: consider both sides for a special rule (see methods).

        FR :
        Valide le scope et renvoie un triplet (appliquer_cited, appliquer_citing, est_both).
        'both' signifie : considérer les deux côtés pour une règle spéciale (voir méthodes).
        """
        s = (scope or "").strip().lower()
        if s not in {"cited", "citing", "both"}:
            raise ValueError("scope must be 'cited', 'citing', or 'both'.")
        return (s in {"cited", "both"},  # apply on cited side?
                s in {"citing", "both"}, # apply on citing side?
                s == "both")             # both special rule?

    def _build_dtypes(self, hint: str) -> Dict[str, str]:
        """
        EN:
        Return a dtype mapping depending on the memory policy.
        - 'compact': string for codes, Int8 for flags, float32 for weights.
        - 'default': let pandas infer dtypes.

        FR :
        Renvoie une table de dtypes selon la politique mémoire.
        - 'compact' : string pour codes, Int8 pour indicateurs, float32 pour poids.
        - 'default' : laisse pandas déduire les types.
        """
        if (hint or "").lower() == "compact":
            return {
                "time_cohort_citing_fam": "string",
                COL_CITED_COUNTRY: "string",
                COL_CITED_SECTOR: "string",
                "Cited_has_Green": "Int8",
                "Cited_has_JTag": "Int8",
                "Cited_has_WIPO_Digtl": "Int8",
                COL_CITING_COUNTRY: "string",
                COL_CITING_SECTOR: "string",
                "Citing_has_Green": "Int8",
                "Citing_has_JTag": "Int8",
                "Citing_has_WIPO_Digtl": "Int8",
                COL_CITATIONS: "float32",
            }
        # default policy: no explicit dtypes
        return {}

    # -------------------------------------------------------------------
    # 1) Chargement
    # -------------------------------------------------------------------
    def load_csv(
        self,
        inputfile: str,
        nrows: Optional[int] = None,
        sample_frac: Optional[float] = None,
        dtype_hint: str = "compact",
        use_pyarrow: bool = True,
    ) -> OpReport:
        """
        EN:
        Load the CSV into memory using RAM-friendly dtypes.
        - path: CSV file path
        - nrows: load only the first N rows (deterministic sampling)
        - sample_frac: if provided, sample that fraction AFTER loading (0 < f <= 1)
        - dtype_hint: "compact" to minimize RAM, "default" to let pandas infer
        - use_pyarrow: try engine='pyarrow' (faster); fallback to engine='c' if unavailable

        Returns:
            OpReport with rows, cols, nrows_param, sample_frac.

        FR :
        Charge le CSV en mémoire avec des dtypes économes.
        - path : chemin du fichier CSV
        - nrows : charge uniquement les N premières lignes (échantillon déterministe)
        - sample_frac : si fourni, échantillonne APRÈS lecture (0 < f <= 1)
        - dtype_hint : "compact" pour minimiser la RAM, "default" pour laisser pandas choisir
        - use_pyarrow : tente engine='pyarrow' (rapide) ; sinon bascule sur engine='c'

        Retour :
            OpReport avec rows, cols, nrows_param, sample_frac.
        """
        # -- Préparation des dtypes
        dtypes = self._build_dtypes(dtype_hint)

        # -- Sélection du moteur de lecture
        engine = "pyarrow" if use_pyarrow else "c"

        # -- Lecture avec fallback propre si pyarrow indisponible
        try:
            df = pd.read_csv(
                inputfile,
                header=0,
                dtype=dtypes if dtypes else None,
                engine=engine,
                nrows=nrows,
            )
        except Exception:
            df = pd.read_csv(
                inputfile,
                header=0,
                dtype=dtypes if dtypes else None,
                engine="c",
                nrows=nrows,
            )

        # -- Homogénéiser quelques colonnes (codes en string)
        for col in (COL_CITED_COUNTRY, COL_CITED_SECTOR, COL_CITING_COUNTRY, COL_CITING_SECTOR):
            if col in df.columns:
                df[col] = df[col].astype("string")

        # -- Échantillonnage optionnel (après lecture)
        if sample_frac is not None:
            if not (0 < sample_frac <= 1):
                raise ValueError("sample_frac must be in (0, 1].")
            df = df.sample(frac=sample_frac, random_state=42).reset_index(drop=True)

        self.df = df

        report = OpReport("load_csv", {
            "rows": len(df),
            "cols": len(df.columns),
            "nrows_param": -1 if nrows is None else nrows,
            "sample_frac": 1.0 if sample_frac is None else sample_frac,
        })
        self._log(report)
        # -- Sauvegarde de l'emplacement du fichier d'entrée
        # pour réutilisation éventuelle au moment de l'enregistrement par .save_as()
        self._last_loaded_path = os.path.abspath(inputfile)
        return report

    # -------------------------------------------------------------------
    # 2) Suppression de colonnes (libérer de la RAM)
    # -------------------------------------------------------------------
    def drop_columns(self, cols: Iterable[str]) -> OpReport:
        """
        EN:
        Drop one or several columns if present.
    
        Accepted inputs:
        - a list of column names      (["A", "B"])
        - a set of column names       ({"A", "B"})
        - a single column name string ("A") -> automatically converted to ["A"]
    
        Parameters:
        -----------
        cols : list / set / str
            Column(s) to drop. Any non-existing column name is ignored.
    
        Behavior:
        ---------
        - Strings are automatically converted into a one-element list.
        - No error is raised when a column does not exist.
        - Report indicates how many columns were requested, dropped, and remain.
    
        Returns:
        --------
        OpReport
            name="drop_columns"
            details={"requested", "dropped", "remaining_cols"}
    
        FR:
        Supprime une ou plusieurs colonnes si elles existent.
    
        Entrées acceptées :
        - liste de noms de colonnes      (["A", "B"])
        - ensemble de noms de colonnes   ({"A", "B"})
        - nom de colonne seul en string  ("A") -> converti automatiquement en ["A"]
    
        Comportement :
        - Conversion automatique d'une string en liste à un élément.
        - Pas d'erreur si une colonne n'existe pas.
        - Le rapport indique le nombre demandé, supprimé et restant.
        """

        self._check_loaded()
        
        # ✅ Ajout robuste pour accepter string OU iterable
        # FR : Si 'cols' est une chaîne, on la convertit automatiquement en liste
        if isinstance(cols, str):
            magenta = "\033[35m"
            reset = "\033[0m"
            self._log(OpReport(
                "warning",
                {"detail": f"{magenta}Received a string for 'cols', converting to [string]{reset}"}
            ))
            cols = [cols]
        
        cols = list(cols)
        existing = [c for c in cols if c in self.df.columns]
        before = len(self.df.columns)
        self.df.drop(columns=existing, inplace=True)
        after = len(self.df.columns)

        report = OpReport("drop_columns", {
            "requested": len(cols),
            "dropped": before - after,
            "remaining_cols": after
        })
        self._log(report)
        return report

    # -------------------------------------------------------------------
    # 3) Renommages
    # -------------------------------------------------------------------
    def rename_columns_by_position(self, new_names: List[str]) -> OpReport:
        """
        EN:
        Rename all columns positionally (len must match). Safer when the source file is stable.

        FR :
        Renomme toutes les colonnes par position (longueur identique).
        Plus sûr quand le fichier source est stable.
        """
        self._check_loaded()
        if len(new_names) != len(self.df.columns):
            raise ValueError("new_names length must match the number of DataFrame columns.")
        old = list(self.df.columns)
        self.df.columns = list(new_names)

        report = OpReport("rename_columns_by_position", {
            "cols": len(new_names),
            "old_first3": old[:3],
            "new_first3": new_names[:3],
        })
        self._log(report)
        return report

    def rename_columns(self, mapping: Dict[str, str]) -> OpReport:
        """
        EN:
        Rename specific columns by name using a dict mapping.

        FR :
        Renomme des colonnes spécifiques par nom via un dict.
        """
        self._check_loaded()
        self.df.rename(columns=mapping, inplace=True)

        report = OpReport("rename_columns", {
            "renamed": len(mapping),
            "sample_keys": list(mapping.keys())[:3],
        })
        self._log(report)
        return report

    # -------------------------------------------------------------------
    # 4) Filtrage anomalies (NaN / vides) --- TESTÉ / VALIDÉ OK : 06/11/2025
    # RESTE SEULEMENT SYNTAXE A REDIGER DANS LIGNES "@" CI-DESSOUS ET TESTER AVEC required_cols != None
    # -------------------------------------------------------------------
    @safe_call_with_hint('cp.filter_anomalies(required_cols=[.../...])')
    @require_keyword_args('cp.filter_anomalies(required_cols=[.../...])')
    def filter_anomalies(self, required_cols: Optional[List[str]] = None) -> OpReport:
        """
        EN:
        Remove rows with NaN/empty values on required columns.
        Accepted inputs:
        - list of column names      (["A", "B"])
        - set of column names       ({"A", "B"})
        - a single column name str  ("A") -> automatically converted to ["A"]
    
        If required_cols is None, all columns except the weight column
        ('fr_nr_citations') are considered required.
    
        FR :
        Supprime les lignes avec NaN/vides sur les colonnes requises.
        Entrées acceptées :
        - liste de noms de colonnes      (["A", "B"])
        - ensemble de noms de colonnes   ({"A", "B"})
        - nom de colonne seul en string  ("A") -> converti automatiquement en ["A"]
    
        Si required_cols est None, toutes les colonnes sauf la colonne de poids
        ('fr_nr_citations') sont considérées comme requises.
        """
        self._check_loaded()
        df = self.df
        n0 = len(df)
    
        # ✅ Auto-conversion d'une string en liste avec warning magenta
        if isinstance(required_cols, str):
            magenta = "\033[35m"
            reset = "\033[0m"
            self._log(OpReport(
                "warning",
                {"detail": f"{magenta}Received a string for 'required_cols', converting to [string]{reset}"}
            ))
            required_cols = [required_cols]
    
        if required_cols is None:
            required_cols = [c for c in df.columns if c != COL_CITATIONS]
    
        keep_mask = pd.Series(True, index=df.index)
        per_col_issues: Dict[str, int] = {}
    
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in DataFrame.")
    
            is_bad = df[col].isna()
            if pd.api.types.is_string_dtype(df[col].dtype):
                is_bad = is_bad | (df[col].str.len() == 0)
    
            cnt = int(is_bad.sum())
            per_col_issues[f"nan_or_empty_{col}"] = cnt
            keep_mask = keep_mask & (~is_bad)
    
        self.df = df[keep_mask].reset_index(drop=True)
        n1 = len(self.df)
    
        details = {
            **per_col_issues,
            "rows_before": n0,
            "rows_after": n1,
            "rows_removed": n0 - n1
        }
        report = OpReport("filter_anomalies", details)
        self._log(report)
        return report
    
    # -------------------------------------------------------------------
    # 5) Filtrage SECTEURS --- TESTÉ / VALIDÉ OK : 06/11/2025
    # -------------------------------------------------------------------
    @safe_call_with_hint('cp.filter_sectors(action="delete-if-cited", sectors=["NtAv"])')
    @require_keyword_args('cp.filter_sectors(action="delete-if-cited", sectors=["NtAv"])')
    def filter_sectors(
        self,
        *,
        action: str,
        sectors: Iterable[str] | str,
    ) -> OpReport:
        """
        EN:
        Filter DataFrame rows according to a list of sectors codes and an explicit action.
    
        Actions
        -------
        - "delete-if-cited":
            Drop rows when Cited_nace2_code ∈ sectors.
        - "delete-if-citing":
            Drop rows when Citing_nace2_code ∈ sectors.
        - "delete-if-cited-or-citing":
            Drop rows when Cited_nace2_code OR Citing_nace2_code ∈ sectors.
        - "delete-if-cited-and-citing":
            Drop rows only when Cited == Citing AND code ∈ sectors.
        - "delete-if-not-cited-or-citing":
            Keep only rows where at least one side (cited or citing)
            is in sectors. (Inclusion filter, not exclusion)
    
        FR:
        Filtre les lignes du DataFrame selon une liste de codes secteurs
        et une action explicite.
    
        Actions
        -------
        - "delete-if-cited":
            Supprime les lignes dont Cited_nace2_code ∈ sectors.
        - "delete-if-citing":
            Supprime les lignes dont Citing_nace2_code OU Citing_nace2_code ∈ sectors.
        - "delete-if-cited-or-citing":
            Supprime les lignes dont Cited_nace2_code ∈ sectors.
        - "delete-if-cited-and-citing":
            Supprime uniquement si Cited == Citing ET code ∈ sectors.
        - "delete-if-not-cited-or-citing":
            Conserve uniquement les lignes ayant au moins un côté
            (cited ou citing) ∈ sectors. (Filtrage par inclusion)
    
        Security notes
        --------------
        - No default value for action → explicit intent required.
        - Empty sectors set:
            * delete-if-*: no-op
            * delete-if-not-*: forbidden to prevent full drop
        - Keyword-only arguments required (decorator) to avoid misuse.
        """
    
        import pandas as pd
    
        self._check_loaded()
    
        # --- Validation de la valeur de action (FR pour le dev)
        allowed_actions = {
            "delete-if-cited",
            "delete-if-citing",
            "delete-if-cited-or-citing",
            "delete-if-cited-and-citing",
            "delete-if-not-cited-or-citing",
        }
        if action not in allowed_actions:
            raise ValueError(
                f"Invalid action: '{action}'. Must be one of: {sorted(allowed_actions)}"
            )
    
        # --- Normalisation de sectors en set[str] non vides
        if isinstance(sectors, (str, int)):
            sectors = [sectors]
        if not hasattr(sectors, "__iter__"):
            raise TypeError("'sectors' must be string or iterable")
    
        banned = set()
        for item in sectors:
            if item is None:
                raise ValueError("sectors contains None")
            s = str(item).strip()
            if not s:
                raise ValueError("sectors contains an empty string")
            banned.add(s)
    
        # --- Colonnes indispensables : on contrôle proprement
        C0 = COL_CITED_SECTOR
        C1 = COL_CITING_SECTOR
        for col in (C0, C1):
            if col not in self.df.columns:
                raise ValueError(f"Missing column '{col}' in DataFrame")
    
        # --- Règle de sécurité pour liste vide (FR pour dev)
        if not banned:
            if action == "delete-if-not-cited-or-citing":
                raise ValueError(
                    "sectors must not be empty when using delete-if-not-cited-or-citing"
                )
            # no-op dans les 3 autres cas
            report = OpReport("filter_countries", {
                "action": action,
                "rows_before": len(self.df),
                "rows_after": len(self.df),
                "removed": 0,
                "mode": "ban-list (empty → no change)",
            })
            self._log(report)
            return report
    
        n0 = len(self.df)
        drop_mask = pd.Series(False, index=self.df.index)
    
        # --- Logique métier : masques selon l'action (FR pour dev)
        if action == "delete-if-cited":
            drop_mask = self.df[C0].isin(banned)
    
        elif action == "delete-if-citing":
            drop_mask = self.df[C1].isin(banned)
    
        elif action == "delete-if-cited-or-citing":
            drop_mask = self.df[C0].isin(banned) | self.df[C1].isin(banned)
    
        elif action == "delete-if-cited-and-citing":
            same = self.df[C0] == self.df[C1]
            drop_mask = same & self.df[C0].isin(banned)
    
        elif action == "delete-if-not-cited-or-citing":
            keep_mask = self.df[C0].isin(banned) | self.df[C1].isin(banned)
            drop_mask = ~keep_mask
    
        removed = int(drop_mask.sum())
        self.df = self.df[~drop_mask].reset_index(drop=True)
        n1 = len(self.df)
    
        interpretation = (
            "keep-list (inclusion)" if action == "delete-if-not-cited-or-citing"
            else "ban-list (exclusion)"
        )
    
        # --- Messages console/log (EN uniquement)
        report = OpReport("filter_sectors", {
            "action": action,
            "rows_before": n0,
            "rows_after": n1,
            "removed": removed,
            "mode": interpretation,
            "sectors_count": len(banned),
        })
        self._log(report)
        return report
    
    # -------------------------------------------------------------------
    # 6) Filtrage PAYS --- TESTÉ / VALIDÉ OK : 06/11/2025
    # -------------------------------------------------------------------
    @safe_call_with_hint('cp.filter_countries(action="delete-if-cited", countries=["FR","DE"])')
    @require_keyword_args('cp.filter_countries(action="delete-if-cited", countries=["FR","DE"])')
    def filter_countries(
        self,
        *,
        action: str,
        countries: Iterable[str] | str,
    ) -> OpReport:
        """
        EN:
        Filter DataFrame rows according to a list of country codes and an explicit action.
    
        Actions
        -------
        - "delete-if-cited":
            Drop rows when Cited_Inv_Country ∈ countries.
        - "delete-if-citing":
            Drop rows when Citing_Inv_Country ∈ countries.
        - "delete-if-cited-or-citing":
            Drop rows when Cited_Inv_Country OR Citing_Inv_Country ∈ countries.
        - "delete-if-cited-and-citing":
            Drop rows only when Cited == Citing AND code ∈ countries.
        - "delete-if-not-cited-or-citing":
            Keep only rows where at least one side (cited or citing)
            is in countries. (Inclusion filter, not exclusion)
    
        FR:
        Filtre les lignes du DataFrame selon une liste de codes pays
        et une action explicite.
    
        Actions
        -------
        - "delete-if-cited":
            Supprime les lignes dont Cited_Inv_Country ∈ countries.
        - "delete-if-citing":
            Supprime les lignes dont Citing_Inv_Country OU Citing_Inv_Country ∈ countries.
        - "delete-if-cited-or-citing":
            Supprime les lignes dont Cited_Inv_Country ∈ countries.
        - "delete-if-cited-and-citing":
            Supprime uniquement si Cited == Citing ET code ∈ countries.
        - "delete-if-not-cited-or-citing":
            Conserve uniquement les lignes ayant au moins un côté
            (cited ou citing) ∈ countries. (Filtrage par inclusion)
    
        Security notes
        --------------
        - No default value for action → explicit intent required.
        - Empty countries set:
            * delete-if-*: no-op
            * delete-if-not-*: forbidden to prevent full drop
        - Keyword-only arguments required (decorator) to avoid misuse.
        """
    
        import pandas as pd
    
        self._check_loaded()
    
        # --- Validation de la valeur de action (FR pour le dev)
        allowed_actions = {
            "delete-if-cited",
            "delete-if-citing",
            "delete-if-cited-or-citing",
            "delete-if-cited-and-citing",
            "delete-if-not-cited-or-citing",
        }
        if action not in allowed_actions:
            raise ValueError(
                f"Invalid action: '{action}'. Must be one of: {sorted(allowed_actions)}"
            )
    
        # --- Normalisation de countries en set[str] non vides
        if isinstance(countries, (str, int)):
            countries = [countries]
        if not hasattr(countries, "__iter__"):
            raise TypeError("'countries' must be string or iterable")
    
        banned = set()
        for item in countries:
            if item is None:
                raise ValueError("countries contains None")
            s = str(item).strip()
            if not s:
                raise ValueError("countries contains an empty string")
            banned.add(s)
    
        # --- Colonnes indispensables : on contrôle proprement
        C0 = COL_CITED_COUNTRY
        C1 = COL_CITING_COUNTRY
        for col in (C0, C1):
            if col not in self.df.columns:
                raise ValueError(f"Missing column '{col}' in DataFrame")
    
        # --- Règle de sécurité pour liste vide (FR pour dev)
        if not banned:
            if action == "delete-if-not-cited-or-citing":
                raise ValueError(
                    "countries must not be empty when using delete-if-not-cited-or-citing"
                )
            # no-op dans les 3 autres cas
            report = OpReport("filter_countries", {
                "action": action,
                "rows_before": len(self.df),
                "rows_after": len(self.df),
                "removed": 0,
                "mode": "ban-list (empty → no change)",
            })
            self._log(report)
            return report
    
        n0 = len(self.df)
        drop_mask = pd.Series(False, index=self.df.index)
    
        # --- Logique métier : masques selon l'action (FR pour dev)
        if action == "delete-if-cited":
            drop_mask = self.df[C0].isin(banned)
    
        elif action == "delete-if-citing":
            drop_mask = self.df[C1].isin(banned)
    
        elif action == "delete-if-cited-or-citing":
            drop_mask = self.df[C0].isin(banned) | self.df[C1].isin(banned)
    
        elif action == "delete-if-cited-and-citing":
            same = self.df[C0] == self.df[C1]
            drop_mask = same & self.df[C0].isin(banned)
    
        elif action == "delete-if-not-cited-or-citing":
            keep_mask = self.df[C0].isin(banned) | self.df[C1].isin(banned)
            drop_mask = ~keep_mask
    
        removed = int(drop_mask.sum())
        self.df = self.df[~drop_mask].reset_index(drop=True)
        n1 = len(self.df)
    
        interpretation = (
            "keep-list (inclusion)" if action == "delete-if-not-cited-or-citing"
            else "ban-list (exclusion)"
        )
    
        # --- Messages console/log (EN uniquement)
        report = OpReport("filter_countries", {
            "action": action,
            "rows_before": n0,
            "rows_after": n1,
            "removed": removed,
            "mode": interpretation,
            "countries_count": len(banned),
        })
        self._log(report)
        return report
    
    # -------------------------------------------------------------------
    # 7) Remplacement de codes  --- TESTÉ / VALIDÉ OK : 06/11/2025
    # -------------------------------------------------------------------
    def replace_codes(
        self,
        mapping: Dict[str, str],
        target: str,                  # "country" OR "sector" (exclusif)
        scope: str = "both"           # "cited" / "citing" / "both"
    ) -> OpReport:
        """
        EN:
        Replace codes using a mapping dictionary on requested target and scope.
        - target: "country" OR "sector" (exclusive).
        - scope:
            * "cited": apply on cited columns only
            * "citing": apply on citing columns only
            * "both": apply on both sides independently (union of sides)

        Note:
        This method does NOT aggregate duplicates; call group_duplicates() afterwards.

        FR :
        Remplace les codes via un dictionnaire de transcodage sur la cible et le scope demandés.
        - target : "country" OU "sector" (exclusif).
        - scope :
            * "cited"  : applique sur les colonnes côté cited uniquement
            * "citing" : applique sur les colonnes côté citing uniquement
            * "both"   : applique sur les deux côtés indépendamment (union des côtés)

        Remarque :
        Cette méthode NE regroupe PAS les doublons ; appeler group_duplicates() ensuite.
        """
        self._check_loaded()

        t = (target or "").strip().lower()
        if t not in {"country", "sector"}:
            raise ValueError("target must be either 'country' or 'sector' (exclusive).")

        apply_cited, apply_citing, _ = self._validate_scope(scope)
        mapping_str = {str(k): str(v) for k, v in mapping.items()}

        affected_cols: List[str] = []
        changed_total = 0

        # -- Sélection des colonnes selon la cible et le scope
        if t == "country":
            if apply_cited and COL_CITED_COUNTRY in self.df.columns:
                affected_cols.append(COL_CITED_COUNTRY)
            if apply_citing and COL_CITING_COUNTRY in self.df.columns:
                affected_cols.append(COL_CITING_COUNTRY)

        elif t == "sector":
            if apply_cited and COL_CITED_SECTOR in self.df.columns:
                affected_cols.append(COL_CITED_SECTOR)
            if apply_citing and COL_CITING_SECTOR in self.df.columns:
                affected_cols.append(COL_CITING_SECTOR)

        # -- Application simple et lisible (pour débutants)
        for col in affected_cols:
            before = self.df[col].astype("string")
            self.df[col] = before.map(lambda x: mapping_str.get(str(x), x)).astype("string")
            changed_total += int((before != self.df[col]).sum())

        report = OpReport("replace_codes", {
            "scope": scope,
            "target": t,
            "columns_affected": len(affected_cols),
            "values_changed": changed_total
        })
        self._log(report)
        return report

    # -------------------------------------------------------------------
    # 8) Regroupement des doublons (agrégation)
    # -------------------------------------------------------------------
    def group_duplicates(self, weight_column: str) -> OpReport:
        """
        EN:
        Group duplicate rows by summing the given weight column, using *all other columns* as keys.
        Example:
            group_duplicates("fr_nr_citations")
        Implementation:
            group_cols = [every column except 'weight_column']
            df = df.groupby(group_cols, dropna=False, as_index=False)[weight_column].sum()

        FR :
        Regroupe les doublons en sommant la colonne de poids fournie, en utilisant
        *toutes les autres colonnes* comme clés.
        Exemple :
            group_duplicates("fr_nr_citations")
        Implémentation :
            group_cols = [toutes les colonnes sauf 'weight_column']
            df = df.groupby(group_cols, dropna=False, as_index=False)[weight_column].sum()
        """
        self._check_loaded()
        if weight_column not in self.df.columns:
            raise ValueError(f"Weight column '{weight_column}' not found in the DataFrame.")

        n0 = len(self.df)
        group_cols = [c for c in self.df.columns if c != weight_column]

        # -- Agrégation lisible (pas de code "magique")
        grouped = (
            self.df.groupby(group_cols, dropna=False, as_index=False)[weight_column]
                   .sum()
                   .astype({weight_column: "float32"})
        )
        self.df = grouped
        n1 = len(self.df)

        report = OpReport("group_duplicates", {
            "weight_column": weight_column,
            "rows_before": n0,
            "rows_after": n1,
            "reduction": n0 - n1
        })
        self._log(report)
        return report

    # -------------------------------------------------------------------
    # 9) Sauvegarde du DataFrame courant (CSV ou Excel)
    # -------------------------------------------------------------------
    def save_as(
        self,
        filename: str,
        type: str = "csv",
        replace: bool = False,
        suffix: Optional[str] = None,
    ) -> OpReport:
        """
        EN:
        Save the current DataFrame to disk (CSV or Excel).

        Parameters
        ----------
        filename : str
            Target file name, with or without path. If no path is provided,
            the directory of the last loaded file (via load_csv) is used.
        type : {"csv", "excel"}, default "csv"
            Output format.
        replace : bool, default False
            If False and file already exists → abort with error log.
            If True → overwrite existing file.
        suffix : str, optional
            Text to append before the file extension.
            Example: filename="data.csv", suffix="_filtered"
            → "data_filtered.csv".

        FR:
        Sauvegarde le DataFrame courant sur disque (CSV ou Excel).

        Paramètres
        -----------
        filename : str
            Nom du fichier cible, avec ou sans chemin. Si aucun chemin
            n’est précisé, on réutilise celui du dernier fichier chargé
            par load_csv().
        type : {"csv", "excel"}, défaut "csv"
            Format de sortie.
        replace : bool, défaut False
            Si False et que le fichier existe → arrêt avec message d’erreur.
            Si True → écrasement silencieux.
        suffix : str, optionnel
            Chaîne à insérer avant l’extension.
            Exemple : "data.csv" + "_2000_row" → "data_2000_row.csv"
        """
        import os

        self._check_loaded()

        # --- Vérification du format demandé
        fmt = (type or "").strip().lower()
        if fmt not in {"csv", "excel"}:
            raise ValueError("Parameter 'type' must be either 'csv' or 'excel'.")

        # --- Vérification et normalisation du chemin
        path = os.path.abspath(filename)
        dirname, basename = os.path.split(path)
        
        # Si aucun chemin fourni → utiliser celui du dernier load_csv
        if filename == os.path.basename(filename):
            # aucun chemin explicite
            base_dir = getattr(self, "_last_loaded_path", None)
            if base_dir is None:
                raise RuntimeError("No path specified and no previous file loaded.")
            dirname = os.path.dirname(base_dir)
        else:
            dirname = os.path.dirname(os.path.abspath(filename))
        
        # --- Validation du dossier
        if not os.path.isdir(dirname):
            raise ValueError(f"Invalid output directory: '{dirname}'")

        # --- Extraction du nom et extension
        name, ext = os.path.splitext(basename)
        print(name, ext)
        # --- Validation extension / format
        default_ext = ".xlsx" if fmt == "excel" else ".csv"
        if ext and ext.lower() != default_ext:
            raise ValueError(f"Incompatible extension '{ext}' for type='{fmt}'.")

        # --- Ajout du suffixe éventuel
        if suffix:
            name = f"{name}{suffix}"

        # --- Reconstruction du nom complet
        final_path = os.path.join(dirname, name + (ext if ext else default_ext))

        # --- Vérification existence + replace
        if os.path.exists(final_path) and not replace:
            raise RuntimeError(
                f"Target file '{final_path}' already exists. "
                "Use replace=True to overwrite."
            )

        # --- Enregistrement
        try:
            if fmt == "csv":
                self.df.to_csv(final_path, index=False)
            else:
                self.df.to_excel(final_path, index=False)
        except Exception as e:
            raise RuntimeError(f"Failed to save file '{final_path}': {e}")

        # --- Rapport final (succès)
        report = OpReport("save_as", {
            "file": final_path,
            "rows": len(self.df),
            "cols": len(self.df.columns),
            "replace": replace,
            "status": "ok"
        })
        self._log(report)
        return report

    # ============================================================
    # === SERVICE : split_by_technos() ===========================
    # ============================================================
    
    @safe_call_with_hint('cp.split_by_technos(split_rule="split_citations")')
    @require_keyword_args('cp.split_by_technos(split_rule="split_citations")')
    def split_by_technos(
        self,
        *,
        split_rule: str = "split_citations",       # "keep_citations" | "split_citations"
        cols: Iterable[str] | None = None,         # optional explicit column names
        group: bool = False,                       # regroup after split
        add_combo_count_col: bool = True,          # add "Combos" column if group=False
        add_pair_key_col: bool = False,            # add "PairKey" = "{CitedTEC}-{CitingTEC}"
        tol_sum_check: float = 1e-3,               # tolerance for conservation check
    ) -> OpReport:
        """
        EN:
        Split the internal DataFrame into a long format, where each line represents
        a unique combination of technologies (CitedTEC × CitingTEC).
    
        Parameters
        ----------
        split_rule : {"keep_citations", "split_citations"}
            - "split_citations": divide the original citation value equally among
              all generated combinations.
            - "keep_citations": keep the same citation value for each combination.
        cols : Iterable[str], optional
            Custom column names (11 expected). If None, uses default constants.
        group : bool, default=False
            If True, group resulting rows by all identification columns and sum
            SplitCitations.
        add_combo_count_col : bool, default=True
            Add column 'Combos' (number of combinations generated per source row).
            Ignored if group=True.
        add_pair_key_col : bool, default=False
            Add column 'PairKey' = "{CitedTEC}-{CitingTEC}".
        tol_sum_check : float, default=1e-9
            Numerical tolerance for total-sum conservation check.
    
        FR:
        Transforme le DataFrame interne en format "long" : chaque ligne représente
        une paire explicite de technologies (CitedTEC × CitingTEC).
    
        - split_rule="split_citations" : la colonne Citations est divisée par
          le nombre de combinaisons générées (conservation stricte de la somme).
        - split_rule="keep_citations" : la valeur est dupliquée sans division.
    
        La méthode peut regrouper les lignes finales selon les colonnes
        d’identification (paramètre group=True).
    
        Retour :
            OpReport résumant l’opération.
        """
    
        import pandas as pd
        from itertools import product
    
        # --------------------------------------------------------
        # 1) PRE-CHECKS AND VALIDATION
        # --------------------------------------------------------
        self._check_loaded()
    
        # Allowed rules
        allowed_rules = {"keep_citations", "split_citations"}
        if split_rule not in allowed_rules:
            raise ValueError(
                f"Invalid split_rule '{split_rule}'. Must be one of {sorted(allowed_rules)}."
            )
    
        # Resolve column names
        if cols is None:
            cols = [
                COL_CITED_COUNTRY, COL_CITED_SECTOR,
                COL_CITED_GRN, COL_CITED_JTG, COL_CITED_DIG,
                COL_CITING_COUNTRY, COL_CITING_SECTOR,
                COL_CITING_GRN, COL_CITING_JTG, COL_CITING_DIG,
                COL_CITATIONS,
            ]
    
        if not isinstance(cols, (list, tuple)) or len(cols) != 11:
            raise ValueError(
                "Parameter 'cols' must be an iterable of exactly 11 column names."
            )
    
        if len(set(cols)) != 11:
            raise ValueError("Parameter 'cols' contains duplicate names.")
    
        for c in cols:
            if c not in self.df.columns:
                raise ValueError(f"Missing required column '{c}' in DataFrame.")
    
        (
            cited_country, cited_sector,
            cited_grn, cited_jtg, cited_dig,
            citing_country, citing_sector,
            citing_grn, citing_jtg, citing_dig,
            citations_col,
        ) = cols
    
        # Check flags are 0/1 or bool
        flag_cols = [
            cited_grn, cited_jtg, cited_dig,
            citing_grn, citing_jtg, citing_dig,
        ]
        for fc in flag_cols:
            invalid_mask = ~self.df[fc].isin([0, 1, True, False])
            if invalid_mask.any():
                bad_vals = self.df.loc[invalid_mask, fc].unique()[:5]
                raise ValueError(
                    f"Column '{fc}' contains invalid values: {bad_vals}. Only 0/1 or bool allowed."
                )
    
        # --------------------------------------------------------
        # 2) BASIC METRICS BEFORE TRANSFORMATION
        # --------------------------------------------------------
        n0 = len(self.df)
        c0 = len(self.df.columns)
        sum_before = float(self.df[citations_col].sum())
    
        # --------------------------------------------------------
        # 3) MAIN TRANSFORMATION LOOP
        # --------------------------------------------------------
        records = []
        for _, row in self.df.iterrows():
            # --- determine active technologies ---
            cited_techs = [
                t for t, f in zip(["GRN", "JTG", "DIG"], [row[cited_grn], row[cited_jtg], row[cited_dig]]) if f == 1 or f is True
            ]
            citing_techs = [
                t for t, f in zip(["GRN", "JTG", "DIG"], [row[citing_grn], row[citing_jtg], row[citing_dig]]) if f == 1 or f is True
            ]
    
            if not cited_techs:
                cited_techs = ["OTH"]
            if not citing_techs:
                citing_techs = ["OTH"]
    
            combos = list(product(cited_techs, citing_techs))
            n_combos = len(combos)
            base_value = row[citations_col]
    
            if split_rule == "split_citations":
                value = base_value / n_combos
            else:
                value = base_value
    
            for cited_tec, citing_tec in combos:
                record = {
                    COL_CITED_COUNTRY: row[cited_country],
                    COL_CITED_SECTOR: row[cited_sector],
                    COL_CITED_TEC: cited_tec,
                    COL_CITING_COUNTRY: row[citing_country],
                    COL_CITING_SECTOR: row[citing_sector],
                    COL_CITING_TEC: citing_tec,
                    COL_SPLIT_CIT: value,
                }
                if not group and add_combo_count_col:
                    record[COL_COMBOS] = n_combos
                if add_pair_key_col:
                    record[COL_PAIRKEY] = f"{cited_tec}-{citing_tec}"
                records.append(record)
    
        df_long = pd.DataFrame(records)
    
        # --------------------------------------------------------
        # 4) GROUPING (optional)
        # --------------------------------------------------------
        if group:
            group_cols = [
                COL_CITED_COUNTRY, COL_CITED_SECTOR, COL_CITED_TEC,
                COL_CITING_COUNTRY, COL_CITING_SECTOR, COL_CITING_TEC,
            ]
            df_long = (
                df_long.groupby(group_cols, as_index=False)[COL_SPLIT_CIT]
                .sum()
                .reset_index(drop=True)
            )
    
        # --------------------------------------------------------
        # 5) VALIDATION OF CONSERVATION (if split_citations)
        # --------------------------------------------------------
        sum_after = float(df_long[COL_SPLIT_CIT].sum())
        if split_rule == "split_citations":
            diff = abs(sum_after - sum_before)
            if diff > tol_sum_check:
                raise ValueError(
                    f"Sum mismatch after split_citations: diff={diff}, tolerance={tol_sum_check}"
                )
    
        # --------------------------------------------------------
        # 6) FINALIZE AND REPORT
        # --------------------------------------------------------
        self.df = df_long.reset_index(drop=True)
        n1 = len(self.df)
        c1 = len(self.df.columns)
    
        report = OpReport("split_by_technos", {
            "split_rule": split_rule,
            "rows_before": n0,
            "rows_after": n1,
            "cols_before": c0,
            "cols_after": c1,
            "sum_before": sum_before,
            "sum_after": sum_after,
        })
    
        self._log(report)
        return report

    # --------------------/-----------------------------------------------
    # 11) Accès lecture au DataFrame courant
    # -------------------------------------------------------------------
    def get_df(self) -> pd.DataFrame:
        """
        EN:
        Return the current DataFrame (note: callers can still modify it in Python).
        FR :
        Renvoie le DataFrame courant (attention : il reste modifiable par l’appelant).
        """
        self._check_loaded()
        return self.df


