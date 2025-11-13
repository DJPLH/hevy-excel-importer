from typing import Any, Dict, Iterable, List
import math

def set_deep(d: Dict[str, Any], path: str, value: Any) -> None:
    keys = path.split(".")
    cur = d
    for k in keys[:-1]:
        if k not in cur or not isinstance(cur[k], dict):
            cur[k] = {}
        cur = cur[k]
    cur[keys[-1]] = value

def _split_csv(val: Any, do_strip: bool) -> List[str]:
    if val is None or val == "":
        return []
    parts = str(val).split(",")
    return [p.strip() if do_strip else p for p in parts]

def apply_transforms(value: Any, rules: Dict[str, Any]):
    if value is None:
        return None
    out = value
    if rules.get("split_csv"):
        out = _split_csv(out, rules.get("strip", False))
    if "strip" in rules and rules["strip"] and not isinstance(out, list):
        out = str(out).strip()
    if rules.get("uppercase") and not isinstance(out, list):
        out = str(out).upper()
    if rules.get("lowercase") and not isinstance(out, list):
        out = str(out).lower()
    if "cast" in rules and not isinstance(out, list):
        typ = rules["cast"]
        if typ == "float":
            out = float(out)
        elif typ == "int":
            out = int(float(out))
        elif typ == "str":
            out = str(out)
    if isinstance(out, (int, float)) and not math.isnan(out):
        if "min" in rules and out < rules["min"]:
            raise ValueError(f"value {out} < min {rules['min']}")
        if "max" in rules and out > rules["max"]:
            raise ValueError(f"value {out} > max {rules['max']}")
    return out

def row_to_payload(row: Dict[str, Any], mapping: Dict[str, str], transforms: Dict[str, Dict[str, Any]]):
    payload: Dict[str, Any] = {}
    for excel_col, json_path in mapping.items():
        raw = row.get(excel_col)
        rules = transforms.get(excel_col, {})
        val = apply_transforms(raw, rules) if rules else raw
        set_deep(payload, json_path, val)
    return payload

def validate_required(row: Dict[str, Any], required_fields: Iterable[str]):
    missing = [f for f in required_fields if not (row.get(f) or row.get(f) == 0)]
    return missing
