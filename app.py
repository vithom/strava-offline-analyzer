import pandas as pd
import panel as pn
import plotly.graph_objs as go
import locale


from strava_client.client import StravaClient

api = StravaClient()


pn.extension('perspective', 'plotly', 'echarts')


def get_data():
    return pd.read_csv("data/export_171438604_20251105/activities.csv",
                       parse_dates=['Activity Date']
                       )

df = get_data()
df.info()

activities = api.get_activities()

# print(df.groupby(df["Activity Date"].dt.weekday)["Distance"].sum().reset_index().rename(columns={"Activity Date": "Month", "Distance": "Total Distance (km)"}))

# dff = df[["Activity Date", "Activity Name", "Activity Type", "Elapsed Time"]].groupby("Activity Type").sum("Elapsed Time")

#graphs
# * Distance / activité / mois



# component = pn.pane.panel(dff)

row = pn.Row(
    pn.indicators.Number(
        name="Total Activities",
        value=len(df),
        # format="{value} activities",
        # sizing_mode="stretch_width"
    ),
    pn.indicators.Number(
        name="Total Distance (km)",
        value=round(df["Distance"].sum(), 2),
        # format="{value} km",
        # sizing_mode="stretch_width"
    ),
    pn.pane.Plotly(
        df.groupby(pd.Grouper(key="Activity Date", freq="M"))["Distance"]
            .sum()
            .reset_index()
            .pipe(
            lambda d: {
                "data": [
                    {
                        "x": d["Activity Date"],
                        "y": d["Distance"],
                        "type": "bar",
                    }
                ],
                "layout": {
                    "title": "Total Distance per Month",
                    "xaxis": {"title": "Month"},
                    "yaxis": {"title": "Total Distance (km)"},
                },
            }
        ),
        sizing_mode="stretch_width",
    ),
    pn.pane.Plotly(
        df.groupby([pd.Grouper(key="Activity Date", freq="W-MON"), "Activity Type"])["Distance"]
            .sum()
            .reset_index()
            .pivot(index="Activity Date", columns="Activity Type", values="Distance")
            .fillna(0)
            .pipe(
                lambda pivot: {
                    "data": [
                        {
                            # shift week labels one week earlier so each bar represents the week starting a week before
                            "x": (pivot.index - pd.Timedelta(weeks=1)),
                            "y": pivot[col].values,
                            "type": "bar",
                            "name": str(col),
                        }
                        for col in pivot.columns
                    ],
                    "layout": {
                        "title": "Weekly Distance by Activity Type (Stacked)",
                        "barmode": "stack",
                        "xaxis": {"title": "Week"},
                        "yaxis": {"title": "Total Distance (km)"},
                        "legend": {"orientation": "h", "y": -0.2},
                    },
                }
            ),
        sizing_mode="stretch_width"
    ),
)

df_months = df.groupby(pd.Grouper(key="Activity Date", freq="M"))["Distance"].sum()
df_months2 = df.resample("1W", on="Activity Date", offset="1W").agg({"Distance": "sum", "Max Speed": "max"})
df_month3 = df.groupby([pd.Grouper(key="Activity Date", freq="W-MON"), "Activity Type"])["Distance"].sum()

row2 = pn.Row(
    pn.pane.DataFrame(df_months),
    pn.pane.DataFrame(df_months2),
    # pn.pane.ECharts({
    #     "tooltip": {
    #         "trigger": 'axis',
    #         "axisPointer": {
    #             "type": 'shadow'
    #         }
    #     },
    #     "xAxis": {
    #         "data": df_months2.reset_index()['Activity Date'].apply(lambda x: x.strftime("%d %b %Y"))
    #     },
    #     "yAxis":{},
    #     "series": [{
    #         "type": "bar",
    #         "data": df_months2['Distance'].values.tolist()
    #     },
    #     {
    #         "type": "line",
    #         "yAxisIndex": 1,
    #         "data": df_months2['Max Speed'].values.tolist()
    #     }],
    #     "yAxis": [
    #         {
    #             "type": 'value',
    #             "name": 'Distance (km)',
    #         },
    #         {
    #             "type": 'value',
    #             "name": 'Max Speed (km/h)',
    #         }
    #     ]
    # # }, options={"opts": {"renderer":"svg"}
    # }, sizing_mode="stretch_width", height=500)
    pn.pane.ECharts(df.groupby([pd.Grouper(key="Activity Date", freq="W-MON"), "Activity Type"])["Distance"]
            .sum()
            .reset_index()
            .pivot(index="Activity Date", columns="Activity Type", values="Distance")
            .fillna(0)
            .pipe(
                lambda pivot: {
                    "data": [
                        {
                            # shift week labels one week earlier so each bar represents the week starting a week before
                            "x": (pivot.index - pd.Timedelta(weeks=1)),
                            "y": pivot[col].values,
                            "type": "bar",
                            "name": str(col),
                        }
                        for col in pivot.columns
                    ],
                    "layout": {
                        "title": "Weekly Distance by Activity Type (Stacked)",
                        "barmode": "stack",
                        "xaxis": {"title": "Week"},
                        "yaxis": {"title": "Total Distance (km)"},
                        "legend": {"orientation": "h", "y": -0.2},
                    },
                }
            ), sizing_mode="stretch_width", height=500)
)

print(locale.getlocale())

from time import strftime, gmtime

print(strftime("%B %b", gmtime()))

print(df_months)
print(df_months.reset_index()['Activity Date'].apply(lambda x: x.month_name(locale="fr_FR.UTF-8") + x.strftime(" %Y")))
print(df_months.values.tolist())

echart_bar = {
    "tooltip": {
        "trigger": 'axis',
        "axisPointer": {
            "type": 'shadow'
        }
    },
    "xAxis": {
        "data": df_months.reset_index()['Activity Date'].apply(lambda x: x.month_name(locale="fr_FR.UTF-8") + x.strftime(" %Y"))
    },
    "yAxis":{},
    "series": [{
        "type": "bar",
        "data": df_months.values.tolist()
    }]
}

ec2 = {
    "tooltip": {
        "trigger": 'axis',
        "axisPointer": {
            "type": 'shadow'
        }
    },
    "xAxis":{
        "data": df_month3.reset_index()['Activity Date'].apply(lambda x: x.strftime("%d-%m"))#x.month_name(locale="fr_FR.UTF-8") + x.strftime(" %Y"))
    },
    "yAxis":{},
    "series": [{
        "type": "bar",
        "data": df_month3.values.astype(int).tolist()
    }]
}

row3 = pn.Row(
    pn.pane.ECharts(echart_bar, options={"opts": {"renderer":"svg"}}, height=400, sizing_mode="stretch_width"),
    pn.pane.ECharts(ec2, options={"opts": {"renderer":"svg"}}, height=400, sizing_mode="stretch_width"),
)

pn.template.VanillaTemplate(
    title="Strava analyzer",
    main = [row, row2, row3, pn.pane.Perspective(df, sizing_mode="stretch_both")],
    # accent = "orange"
).servable()
