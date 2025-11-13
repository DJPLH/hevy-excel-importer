# Hevy Excel Importer

A clean, safe tool to import exercise templates into the Hevy app from Excel.

## 🚀 Quick Start

```bash
git clone <your repo>
cd hevy-excel-importer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 🔑 Set API Key

```bash
export HEVY_API_KEY="your-key"
```

## ▶️ Run Importer

```bash
python -m app.main --excel data/my.xlsx --config config/hevy_config.yaml
```
