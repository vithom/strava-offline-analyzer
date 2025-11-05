import pandas as pd
import panel as pn

pn.extension('perspective')

def get_data():
    return pd.read_csv("data/export_171438604/activities.csv",
                       parse_dates=['Activity Date']
                       )

df = get_data()

df.info()

# dff = df[["Activity Date", "Activity Name", "Activity Type", "Elapsed Time"]].groupby("Activity Type").sum("Elapsed Time")



# component = pn.pane.panel(dff)

pn.template.FastListTemplate(
    title="Strava analyzer",
    main = [pn.pane.Perspective(df, sizing_mode="stretch_both")],
    accent = "orange"
).servable()
