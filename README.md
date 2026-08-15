# MissionScope

A simple Streamlit dashboard for exploring the `space_missions.csv` dataset. It offers filters for launch year, provider, outcome, vehicle status, and launch country, along with a data preview, summary metrics, and charts for mission activity and outcomes.

## Run locally

1. Create and activate a Python virtual environment (recommended).
2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Start the app:

   ```bash
   streamlit run app.py
   ```

The app automatically loads `space_missions.csv` from the same directory as `app.py`.
