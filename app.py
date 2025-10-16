import pandas as pd
import panel as pn

def get_data():
    return pd.read_csv("data/export_171438604/activities.csv")

df = get_data()

df.info()
