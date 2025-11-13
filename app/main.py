import argparse
import json
import os
import sys
import yaml
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv

from app.api_client import ApiClient, ApiError
from app.mapper import row_to_payload, validate_required
from app.validators import validate_payload
from app.utils import stable_row_hash

def load_config(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def read_excel(path: str, sheet_name: str, header_row: int):
    df = pd.read_excel(path, sheet_name=sheet_name, header=header_row - 1, engine="openpyxl")
    return df

def main():
    parser = argparse.ArgumentParser(description="Excel → Hevy API uploader")
    parser.add_argument("--excel", required=True, help="Path to the Excel file")
    parser.add_argument("--config", default="config/hevy_config_final.yaml", help="Path to YAML config")
    parser.add_argument("--sheet", help="Override sheet name from config")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print payloads without sending")
    parser.add_argument("--limit", type=int, default=None, help="Process only N rows")
    parser.add_argument("--start", type=int, default=0, help="Start index (0-based) within the dataframe")
    parser.add_argument("--output", default="results.csv", help="Where to save results log")
    args = parser.parse_args()

    load_dotenv()
    cfg = load_config(args.config)

    api_cfg = cfg["api"]
    excel_cfg = cfg["excel"]
    mapping = cfg["mapping"]
    required = set(cfg.get("required_fields", []))
    transforms = cfg.get("transforms", {})

    sheet_name = args.sheet or excel_cfg.get("sheet_name", "Sheet1")
    header_row = excel_cfg.get("header_row", 1)

    client = ApiClient(
        base_url=api_cfg["base_url"],
        token=api_cfg.get("auth", {}).get("header_value"),
        auth_type=api_cfg.get("auth", {}).get("type", "header"),
        header_name=api_cfg.get("auth", {}).get("header_name", "api-key"),
        rate_limit_per_minute=api_cfg.get("rate_limit_per_minute", 60),
        timeout_seconds=api_cfg.get("timeout_seconds", 20),
        idempotency_header=api_cfg.get("idempotency", {}).get("header_name"),
        custom_headers=api_cfg.get("custom_headers", {}),
    )

    df = read_excel(args.excel, sheet_name=sheet_name, header_row=header_row)
    if args.limit is not None:
        df = df.iloc[args.start: args.start + args.limit]
    else:
        df = df.iloc[args.start:]

    records = df.fillna("").to_dict(orient="records")
    results = []
    create = api_cfg["create"]
    method = create["method"]
    path = create["path"]

    print(f"Processing {len(records)} row(s)...", file=sys.stderr)
    for idx, row in enumerate(tqdm(records, unit="row")):
        row_id = args.start + idx + header_row + 1
        missing = validate_required(row, required)
        if missing:
            results.append({"row_index": row_id, "status": "skipped_missing_required", "missing": ";".join(missing)})
            continue

        payload = row_to_payload(row, mapping, transforms)
        try:
            validate_payload(payload)
        except ValueError as ve:
            results.append({"row_index": row_id, "status": "skipped_invalid_payload", "error": str(ve)})
            continue

        if args.dry_run:
            print("\n---- DRY RUN REQUEST ----")
            print(f"Row {row_id}")
            print(f"Endpoint: {client.base_url}{path}")
            print("Headers:")
            for k, v in client._auth_headers().items():
                print(f"  {k}: {v}")
            print("Payload:")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            print("--------------------------\n")
            results.append({"row_index": row_id, "status": "dry_run", "payload": payload})
            continue

        idem_key = client.new_idempotency_key()
        try:
            resp = client.request(method=method, path=path, json=payload, idempotency_key=idem_key)
            results.append({"row_index": row_id, "status": "created", "response": resp})
        except ApiError as e:
            results.append({"row_index": row_id, "status": "error", "error": str(e)})

    out_df = pd.DataFrame(results)
    out_df.to_csv(args.output, index=False)
    print(f"Done. Wrote log to {args.output}")

if __name__ == "__main__":
    main()
