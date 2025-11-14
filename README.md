# Hevy Excel Importer

Hevy Excel Importer
A clean Python tool for importing custom exercises into the Hevy app via their public API.

This project reads an Excel spreadsheet containing exercise definitions and automatically creates exercise templates inside the Hevy app using the official API.

Fully supports:
	•	Custom exercise titles
	•	Muscle groups
	•	Equipment categories
	•	Lists of secondary muscles
	•	Automatic mapping & validation
	•	Dry-run mode (safe testing)
	•	Rate-limit handling
	•	Safe environment-variable API key loading

Your API key is never stored in the repository.
Users must set their own HEVY_API_KEY.


## 🚀 Quick Start

```bash
git clone https://github.com/DJPLH/hevy-excel-importer.git
cd hevy-excel-importer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 🔑 Set API Key
You first need to generate an API key from the Hevy developer site in order to leverage their public API to create custom exercises in your Hevy account. Here -> https://hevy.com/settings?developer= 
Once you have your API key, run this command on your computer via a terminal window.

macOS / Linux
```bash
export HEVY_API_KEY="your-hevy-api-key-here"
```

Windows PowerShell
```bash
$env:HEVY_API_KEY="your-hevy-api-key-here"
```

## ▶️ Dry Run (Safe testing. No API calls involved)

```bash
python -m app.main --excel data/import.xlsx --config config/hevy_config.yaml
```

## ▶️ Run Importer

```bash
python -m app.main --excel data/import.xlsx --config config/hevy_config.yaml
```

## 🛡 Safety & Error Handling

The importer includes:
	•	API retries (5 attempts, exponential backoff)
	•	Rate limiting (60 requests / minute by default)
	•	Payload validation
	•	Required field checking
	•	Idempotency support
	•	Logging to CSV (results.csv)
