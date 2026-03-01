# CleanCSV Pro

Fix messy CSV files in seconds:
- Encoding + BOM cleanup (UTF-8 output)
- Header normalization (trim, remove invisible chars, de-dup)
- Row cleanup (drop empty Title, etc.)
- Price normalization (round UP to nearest 0.05 / ends with 0 or 5)
- Shopify mode (common import-safe rules)
- Batch splitting for Shopify (5000 rows per file, but never split a Handle group)

## Install

### Option A: run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
