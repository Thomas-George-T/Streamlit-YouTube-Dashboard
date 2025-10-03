"""
Function to import Transformations and run the streamlit dashboard
"""

import json
import streamlit as st
from streamlit_echarts import st_echarts
from millify import millify
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from transform import (
    parse_video,
    youtube_metrics,
    get_video_published_date,
    get_delta_str,
)
import pandas as pd


st.set_page_config(page_title="YouTube Analytics Dashboard")

st.title("YouTube Analytics Dashboard")

VIDEO_URL = st.text_input("Enter URL")

if st.button("Example"):
    VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

try:
    if VIDEO_URL:
        with st.spinner("Crunching numbers..."):
            df = parse_video(VIDEO_URL)
            df_metrics = youtube_metrics(VIDEO_URL)

            # Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("**Views**", millify(df_metrics[0], precision=2))
            col2.metric("**Likes**", millify(df_metrics[1], precision=2))
            col3.metric("**Comments**", millify(df_metrics[2], precision=2))

            # Embedded Video
            st.video(VIDEO_URL)

            # Published timestamp metric with timezone selector and relative delta
            @st.fragment
            def tz_choice_section():
                """Fragment to display the timezone selector and the published timestamp metric"""
                df_published_date = get_video_published_date(VIDEO_URL)
                delta_str = get_delta_str(df_published_date)
                title = df_published_date.get("Title", "")
                creator = df_published_date.get("Creator", "")
                if title:
                    st.subheader(title)
                if creator:
                    st.markdown(f"**Creator:** {creator}")
                tz_choice = st.segmented_control(
                    "Published",
                    label_visibility="hidden",
                    options=["UTC", "EST", "IST"],
                    default="UTC",
                    selection_mode="single",
                )

                st.metric(
                    f"**Published ({tz_choice})**",
                    df_published_date[tz_choice],
                    delta=delta_str,
                )

            tz_choice_section()

            # Top Comments
            st.subheader("Most liked comments")
            df_top = (
                df[["Author", "Comment", "Timestamp", "Likes"]]
                .sort_values("Likes", ascending=False)
                .reset_index(drop=True)
            )
            # st.dataframe(df_top.head(11))

            top_11 = df_top.head(11)
            gd1 = GridOptionsBuilder.from_dataframe(top_11)
            gd1.configure_auto_height(True)
            gridoptions1 = gd1.build()

            AgGrid(
                top_11,
                gridOptions=gridoptions1,
                key="top_comments",
                theme="streamlit",
                update_on="MANUAL",
            )

            # Top Languages
            st.subheader("Languages")
            df_langs = (
                df["Language"]
                .value_counts()
                .rename_axis("Language")
                .reset_index(name="count")
            )

            options2 = {
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "shadow"},
                    "formatter": "{b}: {c}%",
                },
                "yAxis": {
                    "type": "category",
                    "data": df_langs["Language"].tolist(),
                },
                "xAxis": {"type": "value", "axisTick": {"alignWithLabel": "true"}},
                "series": [{"data": df_langs["count"].tolist(), "type": "bar"}],
            }
            st_echarts(options=options2, height="500px")

            # Most Replied Comments
            st.subheader("Most Replied Comments")
            df_replies = (
                df[["Author", "Comment", "Timestamp", "TotalReplies"]]
                .sort_values("TotalReplies", ascending=False)
                .reset_index(drop=True)
            )
            # st.dataframe(df_replies.head(11))

            gd2 = GridOptionsBuilder.from_dataframe(df_replies.head(11))
            gd2.configure_auto_height(True)
            gridoptions2 = gd2.build()
            AgGrid(
                df_replies.head(11),
                gridOptions=gridoptions2,
                key="top_replies",
                theme="streamlit",
                update_on="MANUAL",
            )

            # Sentiments of the Commentors
            st.subheader("Reviews")
            sentiments = df[df["Language"] == "English"]
            data_sentiments = (
                sentiments["TextBlob_Sentiment_Type"]
                .value_counts()
                .rename_axis("Sentiment")
                .reset_index(name="counts")
            )

            data_sentiments["Review_percent"] = (
                100.0 * data_sentiments["counts"] / data_sentiments["counts"].sum()
            ).round(1)

            # Build chart data safely without assuming fixed category positions
            if "No sentiment data" in data_sentiments["Sentiment"].values:
                data_list = [
                    {
                        "value": int(data_sentiments["counts"].iloc[0]),
                        "name": "No sentiment data",
                    }
                ]
            else:
                percent_map = {
                    row["Sentiment"]: float(row["Review_percent"]) for _, row in data_sentiments.iterrows()
                }
                data_list = [
                    {"value": percent_map.get("NEUTRAL", 0.0), "name": "NEUTRAL"},
                    {"value": percent_map.get("POSITIVE", 0.0), "name": "POSITIVE"},
                    {"value": percent_map.get("NEGATIVE", 0.0), "name": "NEGATIVE"},
                ]

            options = {
                "tooltip": {"trigger": "item", "formatter": "{d}%"},
                "legend": {"top": "5%", "left": "center"},
                "series": [
                    {
                        "name": "Sentiment",
                        "type": "pie",
                        "radius": ["40%", "70%"],
                        "avoidLabelOverlap": False,
                        "itemStyle": {
                            "borderRadius": 10,
                            "borderColor": "#fff",
                            "borderWidth": 2,
                        },
                        "label": {"show": False, "position": "center"},
                        "emphasis": {
                            "label": {
                                "show": True,
                                "fontSize": "30",
                                "fontWeight": "bold",
                            }
                        },
                        "labelLine": {"show": False},
                        "data": data_list,
                    }
                ],
            }
            st_echarts(
                options=options,
                height="500px",
            )

except Exception as e:
    st.error(
        e,
        icon="🚨",
    )
