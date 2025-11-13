from typing import Dict, Any

def validate_payload(payload: Dict[str, Any]) -> None:
    if "exercise" not in payload or not isinstance(payload["exercise"], dict):
        raise ValueError("Missing 'exercise' object")
    ex = payload["exercise"]
    for key in ["title", "exercise_type", "equipment_category", "muscle_group"]:
        if key not in ex or ex[key] in (None, ""):
            raise ValueError(f"Missing exercise.{key}")
    if "other_muscles" in ex:
        if ex["other_muscles"] is None:
            ex["other_muscles"] = []
        if not isinstance(ex["other_muscles"], list):
            raise ValueError("exercise.other_muscles must be a list")
