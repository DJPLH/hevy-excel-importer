import hashlib, json

def stable_row_hash(row_dict) -> str:
    as_bytes = json.dumps(row_dict, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(as_bytes).hexdigest()[:24]
