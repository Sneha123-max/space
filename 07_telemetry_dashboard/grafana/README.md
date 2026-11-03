# Grafana (optional)

The terminal dashboard (`python main.py live ...`) is the core and works without Grafana.
This folder is an optional extra for viewing the same SIMULATED SQLite data in Grafana.

**Honest note: I did not install, run or test Grafana. These steps are from the plugin's
documented usage and may need small adjustments.**

1. Install Grafana locally (OSS edition) from grafana.com and start it.
2. Install the SQLite plugin: `grafana cli plugins install frser-sqlite-datasource`
   (some setups need the plugin allowed as unsigned; see the plugin's docs).
3. Run `python seed.py` so `data/telemetry.db` exists.
4. Edit `provisioning/datasources/sqlite.yaml` so `path` is the real absolute path of the DB,
   then copy it into Grafana's `provisioning/datasources/` folder and restart Grafana.
5. In Explore or a new panel, use this query (Grafana wants a time column in unix seconds):

       SELECT CAST(strftime('%s', ts_utc) AS INTEGER) AS time, battery_v, temp_c
       FROM telemetry ORDER BY id
