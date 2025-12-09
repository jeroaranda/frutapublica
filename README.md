# frutapublica
Aplicación de Streamlit para mapear la fruta pública.

## Fallback (no database)

If you don't have a database available (or you removed it to avoid costs), the app can run using the CSV fallback included in `data/flora_data.csv`.

- The code uses a CSV-backed fallback when the environment variable `DATABASE_URL` is not set.
- Reads: `get_observations_df()` will return data from the CSV.
- Writes: `add_observation(...)` appends rows to `data/flora_data.csv` when no DB is configured.

Files added to support fallback:

- `database/fallback_store.py` — in-memory loader for `data/flora_data.csv`.
- `scripts/use_fallback.py` — quick example script demonstrating usage.

## Run locally

1. Create and activate your virtualenv (optional):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Streamlit app (without DB):

```bash
# Do NOT set DATABASE_URL (or unset it) to force CSV fallback
streamlit run Home.py
```

The app will load observations from `data/flora_data.csv`.

## Pushing to GitHub

Basic steps to push your repo:

```bash
git add .
git commit -m "Add CSV fallback for running without a DB"
git push origin main
```

If you want the Streamlit app to run on Streamlit Community Cloud, ensure `requirements.txt` contains all dependencies and push the repo to GitHub. In Streamlit Cloud, set any required secrets (e.g., `google_credentials`) in the app settings. If you prefer to use CSV fallback there, do not set `DATABASE_URL` in the secrets.

