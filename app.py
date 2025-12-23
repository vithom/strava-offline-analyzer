from datetime import datetime
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

activity_mapping = {
    "Run": "Course",
    "Walk": "Marche",
    "Swim": "Natation",
    "Ride": "Vélo",
    "Hike": "Randonnée",
    "MountainBikeRide": "VTT",
    "Yoga": "Yoga",
    "TrailRun": "Trail",
}

activities = api.get_activities(per_page=200)
print(activities[0])

df_api = pd.DataFrame([
    {
        "Activity Name": a.name,
        "Activity Date": a.start_date_local,
        "Sport": activity_mapping[a.sport_type.value],
        "Distance (km)": round(a.distance / 1000,1),  # convert to km
        "Moving Time (min)": round(a.moving_time / 60),  # convert to minutes"
        "Elapsed Time (min)": round(a.elapsed_time / 60),  # convert to minutes
        "Total Elevation Gain": a.total_elevation_gain,
        "Average Speed": round(a.average_speed * 3.6,1) if a.average_speed else 0,  # convert to km/h
        "Max Speed": round(a.max_speed * 3.6,1) if a.max_speed else 0,  # convert to km/h
        # "Average cadence": a.average_cadence
    }
    for a in activities
])

activity_types = df_api["Sport"].unique()


total_dist_api = sum([a.distance for a in activities])
total_days_on_strava = (datetime.now() - activities[-1].start_date_local.replace(tzinfo=None)).days



# print(df.groupby(df["Activity Date"].dt.weekday)["Distance"].sum().reset_index().rename(columns={"Activity Date": "Month", "Distance": "Total Distance (km)"}))

# dff = df[["Activity Date", "Activity Name", "Activity Type", "Elapsed Time"]].groupby("Activity Type").sum("Elapsed Time")

#graphs
# * Distance / activité / mois



# component = pn.pane.panel(dff)

summary_row = pn.Row(
    pn.Column(
        pn.pane.Markdown(f"# {len(activities)} Activités depuis {total_days_on_strava} jours"),
        pn.pane.Markdown(f"# {total_dist_api/1000:.0f} km parcourus"),
    ),
    pn.pane.Perspective(
        df_api,
        plugin="d3_xy_scatter",
        columns=["Activity Date", "Distance (km)"],
        height=300, sizing_mode="stretch_width")
)

row1 = pn.Row(
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

tabs = pn.Tabs( ("Résumé global", pn.Column(summary_row, row1, row2, row3)), dynamic=True, tabs_location="left", sizing_mode="stretch_both")
for a in activity_types:
    tabs.append( (f"# {a}", pn.Column()) )

tabs.append(("Raw data", pn.pane.DataFrame(df_api, sizing_mode="stretch_width")))
tabs.append(("Raw data (perspective)", pn.pane.Perspective(df_api, sizing_mode="stretch_both")))

pn.template.VanillaTemplate(
    title="Strava analyzer",
    # main = [summary_row, row2, row3, pn.pane.Perspective(df, sizing_mode="stretch_both")],
    main = tabs,
    # accent = "orange"
).servable()
