# -*- coding: utf-8 -*-
"""
Created on Wed Nov  5 09:42:31 2025

@author: JPatrick
"""

from __future__ import annotations

import re
from itertools import product
from typing import Callable, Dict, Iterable, List, Optional, Tuple

# pandas is optional until user asks for df/csv/excel
try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None


class IdentityGenerator:
    """
    FR
    ===
    Générateur d'identités IODE/LEC — Implémentation lisible et pédagogique.
    - Docstrings bilingues FR+EN
    - Messages utilisateurs (logs/erreurs) en anglais
    - Agrégation standard : toute dimension présente dans `formula` mais
      absente du gabarit `variable` est agrégée.
    - Skip rules et filtre pondéré {weight} optionnels
    - Debug contrôlé et limité aux 5 premières variables (cf. set_debug)
    - Mode d’agrégation post-transformation configurable :
      "unique" (défaut), "duplicates", "count"

    EN
    ===
    IODE/LEC identity generator — Readable, beginner-friendly implementation.
    - Bilingual docstrings (FR+EN)
    - User-facing messages in English
    - Standard aggregation: any dimension present in `formula` but absent
      from `variable` name pattern is aggregated.
    - Optional skip rules and {weight} filter
    - Debug policy limited to the first 5 variables (see set_debug)
    - Post-transformation aggregation mode:
      "unique" (default), "duplicates", "count"
    """

    _DIM_KEYS = ("C0", "S0", "T0", "C1", "S1", "T1")

    def __init__(self) -> None:
        """
        FR
        --
        Initialise une instance réutilisable. Les dimensions, fonctions,
        filtre de poids, skip rules et patterns sont configurés via les
        setters dédiés.

        EN
        --
        Initializes a reusable instance. Dimensions, user functions,
        weight filter, skip rules and patterns are configured via
        the dedicated setters.
        """
        # Persistent config
        self._dimensions: Dict[str, Optional[List[str]]] = {
            "C0": None, "S0": None, "T0": None,
            "C1": None, "S1": None, "T1": None,
        }
        self._user_functions: Dict[str, Callable[[str], str]] = {}

        self._weight_fn: Optional[Callable[[Dict[str, float], str], Optional[float]]] = None
        self._weight_dict: Optional[Dict[str, float]] = None
        self._weight_key: Optional[str] = None

        # Skip rules among {"C","S","T","CS","CT","ST","CST"}
        self._skip_rules: List[str] = []

        # Debug
        self._debug_level: int = 0  # 0=OFF, 1=INFO, 2=DETAIL
        self._message_lang: str = "en"
        self._debug_max_vars: int = 5  # limit debug prints to first N variables

        # Per-batch
        self._variable_pattern: Optional[str] = None
        self._formula_pattern: Optional[str] = None

        # Post-transformation aggregation mode
        self._aggregate_mode: str = "unique"  # "unique" | "duplicates" | "count"

    # -------------------------
    # Public API
    # -------------------------

    def set_message_language(self, lang: str = "en") -> None:
        """
        FR
        --
        Définit la langue des messages runtime (logs/erreurs). Par défaut: "en".

        EN
        --
        Sets runtime message language (logs/errors). Default: "en".
        """
        self._message_lang = lang or "en"

    def set_dimensions(self, **dims: Optional[Iterable[str]]) -> None:
        """
        FR
        --
        Déclare ou met à jour des dimensions parmi C0, S0, T0, C1, S1, T1.
        - Sous-ensemble possible ; le reste demeure inchangé
        - Passer None efface explicitement la dimension
        - Aucune validation ici : elle aura lieu dans `run()`

        EN
        --
        Declares or updates dimensions among C0, S0, T0, C1, S1, T1.
        - You may pass a subset; others remain unchanged
        - Pass None to explicitly clear a dimension
        - No validation here; it happens in `run()`
        """
        for k, v in dims.items():
            if k not in self._dimensions:
                raise ValueError(f"Unknown dimension '{k}'. Allowed: {list(self._dimensions)}")
            self._dimensions[k] = None if v is None else list(v)

    def get_dimensions(self) -> Dict[str, int]:
        """
        FR
        --
        Retourne {dimension: nombre_de_valeurs} pour les dimensions définies.

        EN
        --
        Returns {dimension: number_of_values} for defined dimensions.
        """
        return {k: len(v) for k, v in self._dimensions.items() if v is not None}

    def set_user_functions(self, fns: Dict[str, Callable[[str], str]]) -> None:
        """
        FR
        --
        Déclare/complète des fonctions custom utilisables en gabarit
        sous la forme `{fname(PX)}`, par ex. `{parent(S0)}`.

        EN
        --
        Declares/extends custom functions usable in patterns as `{fname(PX)}`,
        e.g. `{parent(S0)}`.
        """
        self._user_functions.update(fns or {})

    def set_weight_filter(
        self,
        max_terms: Optional[int] = None,
        weight_fn: Optional[Callable[[Dict[str, float], str], Optional[float]]] = None,
        weight_dict: Optional[Dict[str, float]] = None,
        key: Optional[str] = None,
    ) -> "IdentityGenerator":
        """
        EN
        ===
        Configure weighted filtering for term generation.
        - max_terms: keep at most N terms with the highest valid weights.
        - weight_fn: function returning a numeric weight or None.
        - weight_dict: coefficient lookup table used by weight_fn.
        - key: template used to build lookup keys (e.g. "{C0}_{S0}_...").
        Notes:
        - Invalid weights (None or 0) are always excluded.
        - Skip-rules remain applied first.
    
        FR
        ===
        Configure le filtrage pondéré pour la génération des termes.
        - max_terms : conserve au plus N termes avec les poids les plus élevés.
        - weight_fn : fonction renvoyant un poids numérique ou None.
        - weight_dict : dictionnaire de coefficients pour weight_fn.
        - key : modèle de clé (ex. "{C0}_{S0}_...").
        Remarques :
        - Poids invalides (None ou 0) exclus systématiquement.
        - Les skip-rules restent appliquées en premier.
        """
        self._weight_fn = weight_fn
        self._weight_dict = weight_dict
        self._weight_key = key
        self._weight_max_terms = max_terms
        return self

    def set_weight_filter_PREVIOUS(self,
                          weight_fn: Callable[[Dict[str, float], str], Optional[float]],
                          weight_dict: Dict[str, float],
                          key: str) -> None:
        """
        FR
        --
        Configure le filtre pondéré {weight}. Appel futur:
        weight_fn(weight_dict, resolved_key) -> Optional[float].
        - None ou 0 → terme ignoré
        - valeur non nulle → insérée dans {weight}
        Validation intelligente: si le gabarit `key` ne peut produire aucune
        clé correspondant à `weight_dict`, lève une erreur explicite (avec
        suggestions de gabarits).

        EN
        --
        Configures the weighted filter for {weight}. Future call:
        weight_fn(weight_dict, resolved_key) -> Optional[float].
        - None or 0 → skip term
        - non-zero value → inserted into {weight}
        Smart validation: if `key` template cannot produce any key that
        matches `weight_dict`, raises a clear error (with template suggestions).
        """
        if not isinstance(key, str):
            raise ValueError("Weight key must be a string template such as '{C0}_{S0}_{C1}_{S1}'.")
        self._weight_fn = weight_fn
        self._weight_dict = weight_dict
        self._weight_key = key

        # Early validation if dimensions are already set
        tok_dims = re.findall(r"\{(C0|S0|T0|C1|S1|T1)\}", key)
        all_dims_ready = all(self._dimensions.get(d) for d in tok_dims)
        if all_dims_ready:
            self._validate_weight_filter_config(phase="set_filter")

    def disable_weight_filter(self) -> None:
        """FR/EN — Désactive le filtre pondéré / Disables the weighted filter."""
        self._weight_fn = None
        self._weight_dict = None
        self._weight_key = None

    def set_aggregate_skip_rules(self, *rules: Optional[str]) -> None:
        """
        FR
        --
        Définit les règles d'exclusion d'agrégation parmi
        {"C","S","T","CS","CT","ST","CST"}.
        - 1 à 7 valeurs, ou (None) seul pour reset.

        EN
        --
        Sets pre-aggregation exclusion rules among
        {"C","S","T","CS","CT","ST","CST"}.
        - 1 to 7 values, or (None) alone to reset.
        """
        allowed = {"C", "S", "T", "CS", "CT", "ST", "CST"}
        if len(rules) == 1 and rules[0] is None:
            self._skip_rules = []
            return
        clean = []
        for r in rules:
            if r not in allowed:
                raise ValueError(f"Unknown skip rule '{r}'. Allowed: {sorted(allowed)}")
            clean.append(r)
        self._skip_rules = clean

    def set_aggregate_mode(self, mode: str) -> None:
        """
        FR
        --
        Définit le comportement d'agrégation post-transformation.
        Modes :
          - "unique"     : suppression des termes strictement identiques (default)
          - "duplicates" : conserve tous les termes bruts
          - "count"      : regroupe et ajoute un multiplicateur ("3 * TERME")

        EN
        --
        Defines post-transformation aggregation behavior.
        Modes:
          - "unique"     : remove exact duplicate terms (default)
          - "duplicates" : keep all generated raw terms
          - "count"      : group duplicates and add multiplicity ("3 * TERM")
        """
        allowed = {"unique", "duplicates", "count"}
        if mode not in allowed:
            raise ValueError(f"Unknown aggregate_mode '{mode}'. Allowed: {sorted(allowed)}")
        self._aggregate_mode = mode

    def set_debug(self, level: int = 1) -> None:
        """
        FR
        --
        Définit la verbosité debug :
        0=OFF ; 1=INFO (hors skip) ; 2=DETAIL (inclut skip)
        Les messages détaillés sont affichés pour les **5 premières variables**.

        EN
        --
        Sets debug verbosity:
        0=OFF; 1=INFO (no skip traces); 2=DETAIL (includes skip).
        Detailed messages are limited to the **first 5 variables**.
        """
        if level not in (0, 1, 2):
            raise ValueError("debug level must be 0, 1 or 2")
        self._debug_level = level

    def set_formula(self, variable: str, formula: str) -> None:
        """
        FR
        --
        Enregistre les gabarits `variable` et `formula`.

        EN
        --
        Registers `variable` and `formula` patterns.
        """
        self._variable_pattern = variable
        self._formula_pattern = formula

    def run(self, output: str = "dict", filepath: Optional[str] = None):
        """
        FR
        --
        Exécute la génération.
        - Retourne par défaut un dict {variable_name: expression}
        - output="df"   → pandas.DataFrame (2 colonnes)
        - output="csv"  → écrit un CSV (filepath requis)
        - output="excel"→ écrit un XLSX (<= 1_048_576 lignes)

        EN
        --
        Runs generation.
        - Returns a dict by default {variable_name: expression}
        - output="df"   → pandas.DataFrame (2 columns)
        - output="csv"  → writes a CSV (requires filepath)
        - output="excel"→ writes an XLSX (<= 1_048_576 rows)
        """
        # 1) Validate configuration
        variable = self._variable_pattern
        formula = self._formula_pattern
        if not variable or not formula:
            raise ValueError("Both 'variable' and 'formula' patterns must be set via set_formula().")
    
        has_weight = "{weight}" in formula
        if has_weight and not self._weight_fn:
            raise ValueError("Formula uses {weight} but no weight filter is configured. Call set_weight_filter().")
        if (self._weight_fn is not None) and not has_weight:
            raise ValueError("A weight filter is configured but the formula has no {weight} token.")
    
        # Re-check weight filter validity if configured (dimensions may have changed)
        if has_weight:
            tok_dims = re.findall(r"\{(C0|S0|T0|C1|S1|T1)\}", self._weight_key or "")
            all_dims_ready = all(self._dimensions.get(d) for d in tok_dims)
            if all_dims_ready:
                self._validate_weight_filter_config(phase="run")
    
        dims_all = {k: (v or []) for k, v in self._dimensions.items()}  # unify to lists
    
        # 2) Extract placeholders (order-preserving)
        fn_var, simple_var = self._extract_placeholders(variable)
        fn_for, simple_for = self._extract_placeholders(formula)
    
        # tokens like "parent(S0)" used in the variable name → virtual dims for naming
        name_virtual_tokens, name_virtual_lists = self._compute_virtual_tokens_for_name(fn_var, dims_all)
    
        # Dimensions referenced simply in variable (naming granularity)
        dims_in_variable_simple = [tok for tok in simple_var if tok in dims_all]
        dims_in_variable_simple = self._unique_in_order(dims_in_variable_simple)
    
        # Dimensions referenced in formula (including function args in var/formula)
        fn_dims_in_variable = [dim for (_, dim) in fn_var if dim in dims_all]
        fn_dims_in_formula = [dim for (_, dim) in fn_for if dim in dims_all]
        dims_in_formula = self._unique_in_order(
            [tok for tok in simple_for if tok in dims_all] + fn_dims_in_variable + fn_dims_in_formula
        )
    
        # Check every referenced dimension has a provided list
        missing = [d for d in self._unique_in_order(dims_in_variable_simple + dims_in_formula) if not dims_all.get(d)]
        if missing:
            raise ValueError(
                "Missing values for dimension(s): " + ", ".join(missing) +
                ". Provide them via set_dimensions(...)."
            )
    
        # 3) Build name iteration axes (simple dims + virtual tokens)
        dims_for_names: List[str] = list(dims_in_variable_simple) + name_virtual_tokens
        lists_for_names: List[List[Optional[str]]] = []
        for d in dims_for_names:
            if d in name_virtual_lists:
                lists_for_names.append(name_virtual_lists[d])
            else:
                lists_for_names.append(dims_all[d])
        if not lists_for_names:
            lists_for_names = [[None]]  # single no-dim variable
    
        # 4) Determine aggregation axes (standard rule)
        dims_formula_only = [d for d in dims_in_formula if d not in dims_in_variable_simple]
        lists_for_sum: List[List[Optional[str]]] = [dims_all[d] for d in dims_formula_only] or [[None]]
    
        # 5) Debug — initial info
        est_vars = self._prod([len(lst) for lst in lists_for_names]) if lists_for_names else 1
        est_terms_per_var = self._prod([len(lst) for lst in lists_for_sum]) if lists_for_sum else 1
        est_total_terms = est_vars * est_terms_per_var
        self._debug_info_initial(dims_in_variable_simple, dims_formula_only, est_vars, est_terms_per_var, est_total_terms)
    
        # 6) Generation
        results: Dict[str, str] = {}
        shown_debug_vars = 0
        for combo_names in product(*lists_for_names):
            ctx_name: Dict[str, Optional[str]] = {}
            for d, val in zip(dims_for_names, combo_names):
                ctx_name[d] = val
                if d in self._DIM_KEYS:
                    ctx_name[d] = val
    
            variable_name = self._substitute(variable, ctx_name, fn_eval_needed=True)
    
            terms: List[str] = []
            terms_shown_for_debug = 0
    
            # Build a base context that includes the *simple* naming dims for sum loops
            base_ctx_sum: Dict[str, Optional[str]] = {}
            for d in dims_in_variable_simple:
                base_ctx_sum[d] = ctx_name.get(d)
    
            # ---------------------------------------------------------------------
            # ✅ NEW STRATEGY : two-phase weighted selection if weight filter active
            # ---------------------------------------------------------------------
            # Check that all components of the weighted filter are properly configured.
            has_weight_function = self._weight_fn is not None
            has_weight_dict     = self._weight_dict is not None
            has_weight_key      = self._weight_key is not None
            two_phase = has_weight_function and has_weight_dict and has_weight_key
            if two_phase:
                # Phase 1 — collect candidates with valid weights (skip-rules inside)
                candidates = self._collect_weighted_candidates(
                    lists_for_sum,
                    dims_formula_only,
                    base_ctx_sum
                )
    
                # Phase 2 — select top-N by descending weight (stable)
                selected = self._select_top_weighted_candidates(
                    candidates,
                    self._weight_max_terms
                )
                # Phase 3 — generate final terms only for selected contexts
                for cand in selected:
                    ctx_sum = dict(cand["ctx_sum"])  # type: ignore
                    ctx_for_formula = dict(ctx_sum)
                    ctx_for_formula["weight"] = f"{cand['weight']}"
    
                    self._apply_fn_calls_to_context(self._formula_pattern or "", ctx_for_formula)
                    term_expr = self._substitute(formula, ctx_for_formula, fn_eval_needed=True)
                    terms.append(term_expr)
    
                    if (
                        self._debug_level >= 1
                        and shown_debug_vars < self._debug_max_vars
                        and terms_shown_for_debug < 2
                    ):
                        self._print(f"[DEBUG]   + term example: {term_expr}")
                        terms_shown_for_debug += 1
    
            else:
                # -----------------------------------------------------------------
                # Fallback = legacy behaviour (no top-N selection)
                # -----------------------------------------------------------------
                for combo_sum in product(*lists_for_sum):
                    ctx_sum: Dict[str, Optional[str]] = dict(base_ctx_sum)
                    for d, val in zip(dims_formula_only, combo_sum):
                        ctx_sum[d] = val
    
                    skip_reason = self._should_skip(ctx_sum)
                    if skip_reason is not None:
                        if self._debug_level >= 2 and shown_debug_vars < self._debug_max_vars:
                            self._print(
                                f"[SKIP] Rule {skip_reason} triggered "
                                f"(C0={ctx_sum.get('C0')}, S0={ctx_sum.get('S0')}, T0={ctx_sum.get('T0')}; "
                                f"C1={ctx_sum.get('C1')}, S1={ctx_sum.get('S1')}, T1={ctx_sum.get('T1')})"
                            )
                        continue
    
                    ctx_for_key = dict(ctx_sum)
                    if self._weight_fn and self._weight_dict is not None and self._weight_key:
                        key_resolved = self._substitute(self._weight_key, ctx_for_key, fn_eval_needed=False)
                        weight_val = self._weight_fn(self._weight_dict, key_resolved)
                        if weight_val is None or weight_val == 0:
                            continue
                        ctx_for_formula = dict(ctx_sum)
                        ctx_for_formula["weight"] = f"{weight_val}"
                    else:
                        ctx_for_formula = dict(ctx_sum)
    
                    self._apply_fn_calls_to_context(self._formula_pattern or "", ctx_for_formula)
                    term_expr = self._substitute(formula, ctx_for_formula, fn_eval_needed=True)
                    terms.append(term_expr)
    
                    if (
                        self._debug_level >= 1
                        and shown_debug_vars < self._debug_max_vars
                        and terms_shown_for_debug < 2
                    ):
                        self._print(f"[DEBUG]   + term example: {term_expr}")
                        terms_shown_for_debug += 1
    
            # --------------------------
            # 6.bis) Post-aggregation: apply aggregate_mode
            # --------------------------
            if self._aggregate_mode == "unique":
                terms = list(dict.fromkeys(terms))
    
            elif self._aggregate_mode == "count":
                from collections import Counter
                counter = Counter(terms)
                seen = {}
                for t in terms:
                    if t not in seen:
                        seen[t] = counter[t]
                new_terms = []
                for term, count in seen.items():
                    if count == 1:
                        new_terms.append(term)
                    else:
                        new_terms.append(f"{term} (x {count})")
                terms = new_terms
    
            if terms:
                results[variable_name] = " + ".join(terms)
                if self._debug_level >= 1 and shown_debug_vars < self._debug_max_vars:
                    self._print(f"[DEBUG] → variable_name = {variable_name}")
                    self._print(f"[DEBUG]   → {len(terms)} term(s) kept")
                    shown_debug_vars += 1
    
        # 7) Output formatting
        if output == "dict":
            print("\nData returned into a [dictionary] format")
            return results
    
        if output == "df":
            if pd is None:
                raise RuntimeError("pandas is required for output='df'. Please install pandas.")
            df = pd.DataFrame(
                [{"variable": k, "expression": v} for k, v in results.items()],
                columns=["variable", "expression"]
            )
            print("\nData returned into a [dataframe] format")
            return df
    
        if output in ("csv", "excel"):
            if filepath is None:
                raise ValueError("When output is 'csv' or 'excel', you must provide a 'filepath'.")
            if pd is None:
                raise RuntimeError("pandas is required for CSV/Excel export. Please install pandas.")
    
            df = pd.DataFrame(
                [{"variable": k, "expression": v} for k, v in results.items()],
                columns=["variable", "expression"]
            )
    
            if output == "csv":
                df.to_csv(filepath, index=False)
                print(f"\nData written to [CSV] file {filepath}\nAND returned into a [dictionary] format")
                return results
    
            # excel
            if len(df) > 1_048_576:
                raise ValueError("Excel export limited to 1,048,576 rows. Use CSV for larger outputs.")
            df.to_excel(filepath, index=False)
            print(f"\nData written to [Excel] file {filepath}\nAND returned into a [dictionary] format")
            return results
    
        raise ValueError("Unsupported output format. Use 'dict', 'df', 'csv', or 'excel'.")
    
    def run_PREVIOUS(self, output: str = "dict", filepath: Optional[str] = None):
        """
        FR
        --
        Exécute la génération.
        - Retourne par défaut un dict {variable_name: expression}
        - output="df"   → pandas.DataFrame (2 colonnes)
        - output="csv"  → écrit un CSV (filepath requis)
        - output="excel"→ écrit un XLSX (<= 1_048_576 lignes)

        EN
        --
        Runs generation.
        - Returns a dict by default {variable_name: expression}
        - output="df"   → pandas.DataFrame (2 columns)
        - output="csv"  → writes a CSV (requires filepath)
        - output="excel"→ writes an XLSX (<= 1_048_576 rows)
        """
        # 1) Validate configuration
        variable = self._variable_pattern
        formula = self._formula_pattern
        if not variable or not formula:
            raise ValueError("Both 'variable' and 'formula' patterns must be set via set_formula().")

        has_weight = "{weight}" in formula
        if has_weight and not self._weight_fn:
            raise ValueError("Formula uses {weight} but no weight filter is configured. Call set_weight_filter().")
        if (self._weight_fn is not None) and not has_weight:
            raise ValueError("A weight filter is configured but the formula has no {weight} token.")

        # Re-check weight filter validity if configured (dimensions may have changed)
        if has_weight:
            tok_dims = re.findall(r"\{(C0|S0|T0|C1|S1|T1)\}", self._weight_key or "")
            all_dims_ready = all(self._dimensions.get(d) for d in tok_dims)
            if all_dims_ready:
                self._validate_weight_filter_config(phase="run")

        dims_all = {k: (v or []) for k, v in self._dimensions.items()}  # unify to lists

        # 2) Extract placeholders (order-preserving)
        fn_var, simple_var = self._extract_placeholders(variable)
        fn_for, simple_for = self._extract_placeholders(formula)

        # tokens like "parent(S0)" used in the variable name → virtual dims for naming
        name_virtual_tokens, name_virtual_lists = self._compute_virtual_tokens_for_name(fn_var, dims_all)

        # Dimensions referenced simply in variable (naming granularity)
        dims_in_variable_simple = [tok for tok in simple_var if tok in dims_all]
        dims_in_variable_simple = self._unique_in_order(dims_in_variable_simple)

        # Dimensions referenced in formula (including function args in var/formula)
        fn_dims_in_variable = [dim for (_, dim) in fn_var if dim in dims_all]
        fn_dims_in_formula = [dim for (_, dim) in fn_for if dim in dims_all]
        dims_in_formula = self._unique_in_order(
            [tok for tok in simple_for if tok in dims_all] + fn_dims_in_variable + fn_dims_in_formula
        )

        # Check every referenced dimension has a provided list
        missing = [d for d in self._unique_in_order(dims_in_variable_simple + dims_in_formula) if not dims_all.get(d)]
        if missing:
            raise ValueError(
                "Missing values for dimension(s): " + ", ".join(missing) +
                ". Provide them via set_dimensions(...)."
            )

        # 3) Build name iteration axes (simple dims + virtual tokens)
        dims_for_names: List[str] = list(dims_in_variable_simple) + name_virtual_tokens
        lists_for_names: List[List[Optional[str]]] = []
        for d in dims_for_names:
            if d in name_virtual_lists:
                lists_for_names.append(name_virtual_lists[d])
            else:
                lists_for_names.append(dims_all[d])
        if not lists_for_names:
            lists_for_names = [[None]]  # single no-dim variable

        # 4) Determine aggregation axes (standard rule)
        #    aggregate dims: present in formula (simple/args) but not in the simple naming dims
        dims_formula_only = [d for d in dims_in_formula if d not in dims_in_variable_simple]
        lists_for_sum: List[List[Optional[str]]] = [dims_all[d] for d in dims_formula_only] or [[None]]

        # 5) Debug — initial info
        est_vars = self._prod([len(lst) for lst in lists_for_names]) if lists_for_names else 1
        est_terms_per_var = self._prod([len(lst) for lst in lists_for_sum]) if lists_for_sum else 1
        est_total_terms = est_vars * est_terms_per_var
        self._debug_info_initial(dims_in_variable_simple, dims_formula_only, est_vars, est_terms_per_var, est_total_terms)

        # 6) Generation
        results: Dict[str, str] = {}
        shown_debug_vars = 0
        for combo_names in product(*lists_for_names):
            # Build context for naming (simple dims + virtual tokens)
            ctx_name: Dict[str, Optional[str]] = {}
            for d, val in zip(dims_for_names, combo_names):
                ctx_name[d] = val
                if d in self._DIM_KEYS:
                    ctx_name[d] = val

            # Evaluate variable_name (virtual tokens replaced too)
            variable_name = self._substitute(variable, ctx_name, fn_eval_needed=True)

            # Prepare per-variable info
            terms: List[str] = []
            terms_shown_for_debug = 0  # limit sample log

            # Build a base context that includes the *simple* naming dims for sum loops
            base_ctx_sum: Dict[str, Optional[str]] = {}
            for d in dims_in_variable_simple:
                base_ctx_sum[d] = ctx_name.get(d)

            # Iterate aggregate axes
            for combo_sum in product(*lists_for_sum):
                ctx_sum: Dict[str, Optional[str]] = dict(base_ctx_sum)
                for d, val in zip(dims_formula_only, combo_sum):
                    ctx_sum[d] = val

                # Apply skip rules (decision to skip is independent of debug)
                skip_reason = self._should_skip(ctx_sum)
                if skip_reason is not None:
                    if self._debug_level >= 2 and shown_debug_vars < self._debug_max_vars:
                        self._print(f"[SKIP] Rule {skip_reason} triggered "
                                    f"(C0={ctx_sum.get('C0')}, S0={ctx_sum.get('S0')}, T0={ctx_sum.get('T0')}; "
                                    f"C1={ctx_sum.get('C1')}, S1={ctx_sum.get('S1')}, T1={ctx_sum.get('T1')})")
                    continue

                # Weighted filter (if any)
                ctx_for_key = dict(ctx_sum)  # simple placeholder values available
                if self._weight_fn and self._weight_dict is not None and self._weight_key:
                    key_resolved = self._substitute(self._weight_key, ctx_for_key, fn_eval_needed=False)
                    weight_val = self._weight_fn(self._weight_dict, key_resolved)
                    if weight_val is None or weight_val == 0:
                        # skip term
                        continue
                    ctx_for_formula = dict(ctx_sum)
                    ctx_for_formula["weight"] = f"{weight_val}"
                else:
                    ctx_for_formula = dict(ctx_sum)

                # Evaluate functional placeholders used in formula (add to context)
                self._apply_fn_calls_to_context(self._formula_pattern or "", ctx_for_formula)

                # Substitute final term
                term_expr = self._substitute(formula, ctx_for_formula, fn_eval_needed=True)
                terms.append(term_expr)

                # Debug samples (first 5 variables only)
                if self._debug_level >= 1 and shown_debug_vars < self._debug_max_vars and terms_shown_for_debug < 2:
                    self._print(f"[DEBUG]   + term example: {term_expr}")
                    terms_shown_for_debug += 1

            # --------------------------
            # 6.bis) Post-aggregation: apply aggregate_mode
            # --------------------------
            if self._aggregate_mode == "unique":
                # Preserve order, remove duplicates
                terms = list(dict.fromkeys(terms))

            elif self._aggregate_mode == "count":
                from collections import Counter
                counter = Counter(terms)
                # keep insertion order of first appearance
                seen = {}
                for t in terms:
                    if t not in seen:
                        seen[t] = counter[t]
                new_terms = []
                for term, count in seen.items():
                    if count == 1:
                        new_terms.append(term)
                    else:
#                        new_terms.append(f"{count} * {term}")
                        new_terms.append(f"{term} (x {count})")
                terms = new_terms

            # elif "duplicates": do nothing

            # Aggregate: join terms with "+"
            if terms:
                results[variable_name] = " + ".join(terms)
                if self._debug_level >= 1 and shown_debug_vars < self._debug_max_vars:
                    self._print(f"[DEBUG] → variable_name = {variable_name}")
                    self._print(f"[DEBUG]   → {len(terms)} term(s) kept")
                    shown_debug_vars += 1

        # 7) Output formatting
        if output == "dict":
            print("\nData returned into a [dictionary] format")
            return results

        if output == "df":
            if pd is None:
                raise RuntimeError("pandas is required for output='df'. Please install pandas.")
            df = pd.DataFrame(
                [{"variable": k, "expression": v} for k, v in results.items()],
                columns=["variable", "expression"]
            )
            print("\nData returned into a [dataframe] format")
            return df

        if output in ("csv", "excel"):
            if filepath is None:
                raise ValueError("When output is 'csv' or 'excel', you must provide a 'filepath'.")
            if pd is None:
                raise RuntimeError("pandas is required for CSV/Excel export. Please install pandas.")

            df = pd.DataFrame(
                [{"variable": k, "expression": v} for k, v in results.items()],
                columns=["variable", "expression"]
            )

            if output == "csv":
                df.to_csv(filepath, index=False)
                print(f"\nData written to [CSV] file {filepath}\nAND returned into a [dictionary] format")
                return results

            # excel
            if len(df) > 1_048_576:
                raise ValueError("Excel export limited to 1,048,576 rows. Use CSV for larger outputs.")
            df.to_excel(filepath, index=False)
            print(f"\nData written to [Excel] file {filepath}\nAND returned into a [dictionary] format")
            return results

        raise ValueError("Unsupported output format. Use 'dict', 'df', 'csv', or 'excel'.")

    def help(self, topic: Optional[str] = None) -> None:
        """
        FR
        --
        Affiche une aide de référence rapide.
        Sans paramètre: liste les topics.
        Topics: dimensions, functions, weight_filter,
                aggregate_skip_rules, aggregate_mode,
                placeholders, debug, run, output.

        EN
        --
        Displays quick reference help.
        No parameter: lists topics.
        Topics: dimensions, functions, weight_filter,
                aggregate_skip_rules, aggregate_mode,
                placeholders, debug, run, output.
        """
        topics = {
            "dimensions": "set_dimensions(C0=[...], ...); get_dimensions()",
            "functions": "set_user_functions({'parent': lambda s: s[:2], ...})",
            "weight_filter": "set_weight_filter(weight_fn, weight_dict, key='{C0}_{S0}_{C1}_{S1}')",
            "aggregate_skip_rules": "set_aggregate_skip_rules('C','CS','CST', ...) or None to reset",
            "aggregate_mode": "set_aggregate_mode('unique'|'duplicates'|'count')",
            "placeholders": "{C0},{S1},{T0},{weight} and {fname(PX)} like {parent(S0)}",
            "debug": "set_debug(level=0/1/2); level 1 shows summary & samples; level 2 adds skip traces",
            "run": "set_formula(variable, formula) then run(output='dict'|'df'|'csv'|'excel', filepath=...)",
            "output": "dict (default), df (pandas), csv, excel (<=1,048,576 rows)"
        }
        if topic is None:
            print("Help topics:", ", ".join(topics.keys()))
            return
        if topic not in topics:
            print(f"Unknown topic '{topic}'. Available:", ", ".join(topics.keys()))
            return
        print(topics[topic])

    # -------------------------
    # Internal helpers (readable)
    # -------------------------

    def _collect_weighted_candidates(
        self,
        lists_for_sum: List[List[str]],
        dims_formula_only: List[str],
        base_ctx_sum: Dict[str, Optional[str]],
    ) -> List[Dict[str, object]]:
        """
        EN
        ===
        Phase 1: scan all combinations and collect only candidates
        with strictly valid weights.
    
        Behaviour:
        - Build ctx_sum for each combination.
        - Apply skip-rules.
        - Resolve weight key and compute weight.
        - Keep only weights != None and != 0.
        - Record original index for stable sorting.
    
        FR
        ===
        Phase 1 : parcourt toutes les combinaisons et collecte
        uniquement celles ayant un poids valide.
    
        Comportement :
        - Construit ctx_sum pour chaque combinaison.
        - Applique les skip-rules.
        - Calcule la clé et le poids.
        - Conserve uniquement poids != None et != 0.
        - Stocke l’index initial pour un tri stable.
        """
        candidates: List[Dict[str, object]] = []
        index = 0
    
        for combo_sum in product(*lists_for_sum):
            ctx_sum: Dict[str, Optional[str]] = dict(base_ctx_sum)
            for d, val in zip(dims_formula_only, combo_sum):
                ctx_sum[d] = val
    
            # Skip rules (inchangé)
            skip_reason = self._should_skip(ctx_sum)
            if skip_reason is not None:
                if self._debug_level >= 2:
                    self._print(
                        f"[SKIP] Rule {skip_reason} triggered "
                        f"(C0={ctx_sum.get('C0')}, S0={ctx_sum.get('S0')}, T0={ctx_sum.get('T0')}; "
                        f"C1={ctx_sum.get('C1')}, S1={ctx_sum.get('S1')}, T1={ctx_sum.get('T1')})"
                    )
                continue
    
            # Nécessite une config de filtre pondéré complète
            if not (self._weight_fn and self._weight_dict is not None and self._weight_key):
                continue
    
            # Calcul du poids
            key_resolved = self._substitute(self._weight_key, dict(ctx_sum), fn_eval_needed=False)
            weight_val = self._weight_fn(self._weight_dict, key_resolved)
    
            # Conserver uniquement les poids strictement valides
            if weight_val is None or weight_val == 0:
                continue
    
            candidates.append({"ctx_sum": ctx_sum, "weight": float(weight_val), "index": index})
            index += 1
    
        return candidates


    def _select_top_weighted_candidates(
        self,
        candidates: List[Dict[str, object]],
        max_terms: Optional[int],
    ) -> List[Dict[str, object]]:
        """
        EN
        ===
        Phase 2 of the weighted selection strategy: select the top-N candidates
        based on their weight values.
        Input
        -----
        candidates : list of dict
            Output of `_collect_weighted_candidates()`.
            Each candidate has {ctx_sum, weight, index}.
        max_terms : int | None
            Maximum number of candidates to retain.
            - If None → keep all candidates.
            - If N → keep at most N candidates with the highest weights.
        Sorting logic
        -------------
        - Primary key  : descending weight
        - Secondary key: ascending index (to preserve original iteration order)
          This ensures deterministic and stable behaviour for equal weights.    
        Returns
        -------
        List of candidates, sorted and truncated according to max_terms.
        Each item has the same structure as in the input.
    
        FR
        ===
        Phase 2 de la stratégie pondérée : sélection des meilleurs candidats
        selon leurs poids.
        Entrées
        -------
        candidates : liste de dict
            Résultat de `_collect_weighted_candidates()`.
            Chaque élément contient {ctx_sum, weight, index}.
        max_terms : int | None
            Nombre maximum de candidats à conserver.
            - None = conserver tous les candidats.
            - N = conserver au maximum N candidats parmi les poids les plus élevés.
        Logique de tri
        ---------------
        - Tri principal  : poids décroissant
        - Tri secondaire : index croissant (stabilité / conservation de l’ordre)
          Cela garantit un comportement déterministe même en cas d’égalité parfaite.
        Retour
        ------
        Liste de candidats triés et éventuellement limités selon max_terms.
        Chaque entrée conserve la structure d’origine.
        """
        if not candidates:
            return []
    
        sorted_candidates = sorted(
            candidates,
            key=lambda c: (-float(c["weight"]), int(c["index"]))
        )
        if max_terms is None:
            return sorted_candidates
        return sorted_candidates[: max(0, int(max_terms))]

    @staticmethod
    def _unique_in_order(seq: List[str]) -> List[str]:
        seen = set()
        out = []
        for x in seq:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    @staticmethod
    def _prod(ints: List[int]) -> int:
        p = 1
        for n in ints:
            p *= n
        return p

    def _print(self, msg: str) -> None:
        # Runtime messages in English as agreed
        print(msg)

    def _debug_info_initial(self,
                            dims_in_variable_simple: List[str],
                            dims_formula_only: List[str],
                            est_vars: int,
                            est_terms_per_var: int,
                            est_total_terms: int) -> None:
        if self._debug_level >= 1:
            if dims_formula_only:
                mode = "aggregated on " + ",".join(dims_formula_only)
            else:
                mode = "direct mode (no extra aggregation)"
            self._print("[INFO] Initial analysis:")
            self._print(f"  • {mode}")
            self._print(f"  • Estimated variables: ≈ {est_vars} (name dims = {dims_in_variable_simple or '∅'})")
            self._print(f"  • Estimated terms/variable: ≈ {est_terms_per_var}")
            self._print(f"  • Potential total terms: ≈ {est_total_terms}")
            if est_total_terms > 1000:
                self._print("⚠ Attention: very large potential volume. Consider filtering or narrower lists.")

    def _extract_placeholders(self, text: str) -> Tuple[List[Tuple[str, str]], List[str]]:
        """
        Returns:
          - fn_calls: list of (fname, 'PX') where PX ∈ {'C0','S0','T0','C1','S1','T1'}
          - simples: list of tokens inside {...} excluding function calls and _key (in-order)
        """
        fn_calls = re.findall(r"\{([A-Za-z_]\w*)\(([CST][01])\)\}", text)
        all_braced = re.findall(r"\{([^}]+)\}", text)
        fn_tokens = {f"{fname}({dim})" for (fname, dim) in fn_calls}
        simples = [tok for tok in all_braced if tok not in fn_tokens and tok != "_key"]
        return fn_calls, simples

    def _compute_virtual_tokens_for_name(
        self,
        fn_calls_var: List[Tuple[str, str]],
        dims_all: Dict[str, List[str]]
    ) -> Tuple[List[str], Dict[str, List[str]]]:
        """
        FR
        --
        Pour chaque {fname(PX)} apparaissant dans le gabarit du NOM de variable,
        construit une "dimension virtuelle" (liste de valeurs dérivées uniques).

        EN
        --
        For each {fname(PX)} in the variable NAME pattern, builds a "virtual dimension"
        (list of unique derived values).
        """
        name_virtual_lists: Dict[str, List[str]] = {}
        name_virtual_order: List[str] = []

        for fname, dim in fn_calls_var:
            token = f"{fname}({dim})"
            if token in name_virtual_lists:
                continue
            if fname not in self._user_functions:
                raise ValueError(f"Unknown function in variable pattern: '{fname}'. Register it via set_user_functions().")
            src = dims_all.get(dim) or []
            if not src:
                raise ValueError(f"Dimension '{dim}' used in {token} but no values provided in set_dimensions().")
            derived = sorted({str(self._user_functions[fname](v)) for v in src})
            name_virtual_lists[token] = derived
            name_virtual_order.append(token)

        return name_virtual_order, name_virtual_lists

    def _apply_fn_calls_to_context(self, pattern: str, context: Dict[str, Optional[str]]) -> None:
        """
        FR
        --
        Evalue les {fname(PX)} présents dans `pattern` et insère les résultats
        dans `context` sous la clé "fname(PX)".

        EN
        --
        Evaluates {fname(PX)} found in `pattern` and injects results into `context`
        under the key "fname(PX)".
        """
        matches = re.findall(r"\{([A-Za-z_]\w*)\(([CST][01])\)\}", pattern)
        for fname, dim in matches:
            if fname not in self._user_functions:
                raise ValueError(f"Unknown function '{fname}' used in pattern.")
            dim_val = context.get(dim)
            if dim_val is None:
                raise ValueError(f"Missing value for '{dim}' before applying '{fname}()'.")
            context[f"{fname}({dim})"] = str(self._user_functions[fname](dim_val))

    def _substitute(self, pattern: str, values: Dict[str, Optional[str]], *, fn_eval_needed: bool) -> str:
        """
        FR
        --
        Remplace d'abord {fname(PX)} puis les placeholders simples {C0}... {weight}.
        _key n'est jamais substitué ici (réservé au filtre si besoin).

        EN
        --
        Replaces {fname(PX)} first, then simple placeholders {C0}... {weight}.
        _key is never substituted here.
        """
        expr = pattern

        # 1) {fname(PX)}
        fn_matches = re.findall(r"\{([A-Za-z_]\w*)\(([CST][01])\)\}", expr)
        if fn_eval_needed and fn_matches:
            tmp_values = dict(values)
            for fname, dim in fn_matches:
                token = f"{fname}({dim})"
                if token not in tmp_values:
                    if fname not in self._user_functions:
                        raise ValueError(f"Unknown function '{fname}' in pattern.")
                    dim_val = tmp_values.get(dim)
                    if dim_val is None:
                        raise ValueError(f"Missing value for '{dim}' before applying '{fname}()'.")
                    tmp_values[token] = str(self._user_functions[fname](dim_val))
            values = tmp_values

        for fname, dim in fn_matches:
            token = f"{fname}({dim})"
            if token not in values or values[token] is None:
                raise ValueError(f"Unresolved functional placeholder: {{{token}}}")
            expr = expr.replace("{" + token + "}", str(values[token]))

        # 2) simple placeholders
        simple_matches = re.findall(r"\{([^}]+)\}", expr)
        for key in simple_matches:
            if key == "_key":
                continue
            if key not in values or values[key] is None:
                raise ValueError(f"Unresolved placeholder: {{{key}}}")
            expr = expr.replace("{" + key + "}", str(values[key]))

        return expr

    def _should_skip(self, ctx: Dict[str, Optional[str]]) -> Optional[str]:
        """
        FR
        --
        Applique les skip rules actives. Retourne le code de règle déclenchée,
        sinon None.

        EN
        --
        Applies active skip rules. Returns triggered rule code, else None.
        """
        def eq(a: Optional[str], b: Optional[str]) -> bool:
            return (a is not None) and (b is not None) and (a == b)

        C0, S0, T0 = ctx.get("C0"), ctx.get("S0"), ctx.get("T0")
        C1, S1, T1 = ctx.get("C1"), ctx.get("S1"), ctx.get("T1")

        if "CST" in self._skip_rules and eq(C0, C1) and eq(S0, S1) and eq(T0, T1):
            return "CST"
        if "CS" in self._skip_rules and eq(C0, C1) and eq(S0, S1):
            return "CS"
        if "CT" in self._skip_rules and eq(C0, C1) and eq(T0, T1):
            return "CT"
        if "ST" in self._skip_rules and eq(S0, S1) and eq(T0, T1):
            return "ST"
        if "C" in self._skip_rules and eq(C0, C1):
            return "C"
        if "S" in self._skip_rules and eq(S0, S1):
            return "S"
        if "T" in self._skip_rules and eq(T0, T1):
            return "T"
        return None

    # ===============================================================
    # Weight dict intelligent validation with suggestions
    # ===============================================================
    def _validate_weight_filter_config(self, phase: str) -> None:
        """Check if weight_dict and key template are compatible.
           If not, suggest up to 3 valid templates based on dict keys."""
        if not (self._weight_fn and self._weight_dict and self._weight_key):
            return

        sample_generated = self._sample_generated_keys(self._weight_key)
        if not sample_generated:
            raise ValueError(
                f"Weight filter misconfigured during {phase}: "
                f"No dimension values available for generating keys."
            )

        dict_keys = set(self._weight_dict.keys())
        matches = dict_keys.intersection(sample_generated)
        if matches:
            return  # OK ✅ at least one match exists

        observed = next(iter(dict_keys)) if dict_keys else None
        example_gen = next(iter(sample_generated))

        msg = [
            "Weight filter misconfigured.",
            f"No generated key from \"{self._weight_key}\" matches weight_dict entries.",
            "",
        ]

        if observed:
            msg.append(f"Example observed key: \"{observed}\"")
        msg.append(f"Example generated key: \"{example_gen}\"")
        msg.append("")
        msg.append("Possible template fixes:")

        suggestions = self._suggest_key_templates(observed, sample_generated, top=3)
        for tpl, ex in suggestions:
            msg.append(f" • {tpl} → \"{ex}\"")

        msg.append("")
        msg.append("Check key template accordingly and retry.")

        raise ValueError("\n".join(msg))

    def _sample_generated_keys(self, key_tpl: str) -> List[str]:
        """Generate a small sample (max 50) of possible keys based
           on current dimensions and key placeholders."""
        dims = re.findall(r"\{(C0|S0|T0|C1|S1|T1)\}", key_tpl)
        lists = []
        for d in dims:
            vals = self._dimensions.get(d) or []
            if not vals:
                return []
            lists.append(vals)
        sample = []
        for combo in product(*lists):
            tmp = key_tpl
            for d, v in zip(dims, combo):
                tmp = tmp.replace(f"{{{d}}}", v)
            sample.append(tmp)
            if len(sample) >= 50:
                break
        return sample

    def _suggest_key_templates(self, observed: Optional[str],
                               generated: List[str],
                               top: int = 3) -> List[tuple]:
        """Heuristic template suggestions: rank by similarity to observed."""
        if not generated:
            return []

        if not observed:
            observed = generated[0]

        obs_parts = observed.split("_")
        N = len(obs_parts)

        # collect which dims are defined (have values)
        used_dims = [d for d, vals in self._dimensions.items() if vals]

        # generate permutations of used dims with the same arity (no repeats)
        perms = []
        for p in product(used_dims, repeat=N):
            if len(set(p)) < N:
                continue
            perms.append(p)

        scored = []
        for p in perms:
            tpl = "_".join("{" + d + "}" for d in p)
            # Use sample keys to compute a best example and a simple score
            best_score = -1
            best_example = generated[0]
            for g in generated:
                g_parts = g.split("_")
                score = sum(gp == op for gp, op in zip(g_parts, obs_parts))
                if score > best_score:
                    best_score = score
                    best_example = g
            scored.append((best_score, tpl, best_example))

        # sort by score desc, then template for stability
        scored.sort(key=lambda x: (-x[0], x[1]))
        return [(tpl, ex) for _, tpl, ex in scored[:top]]
