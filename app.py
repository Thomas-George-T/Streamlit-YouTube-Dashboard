"""
Function to import Transformations and run the streamlit dashboard
"""
import json
import streamlit as st
from streamlit_echarts import st_echarts
from millify import millify
from transform import parse_video, youtube_metrics


st.set_page_config(
    page_title="YouTube Analytics Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
)

st.title('YouTube Analytics Dashboard')

VIDEO_URL = st.text_input('Enter URL')

if st.button('Try Example'):
    VIDEO_URL='https://www.youtube.com/watch?v=dQw4w9WgXcQ'

try:
    if VIDEO_URL:
        with st.spinner('Crunching numbers...'):
            df = parse_video(VIDEO_URL)
            df_metrics = youtube_metrics(VIDEO_URL)

            # Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("**Views**", millify(df_metrics[0], precision=2))
            col2.metric("**Likes**", millify(df_metrics[1], precision=2))
            col3.metric("**Comments**", millify(df_metrics[2], precision=2))

            # Embedded Video
            st.video(VIDEO_URL)

            # Top Comments
            st.subheader("Most liked comments")
            df_top = df[['Author', 'Comment', 'Timestamp', 'Likes']].sort_values(
                'Likes', ascending=False).reset_index(drop=True)
            st.table(df_top.head(11))

            # Top Languages
            st.subheader("Languages")
            df_langs = df['Language'].value_counts().rename_axis(
                'Language').reset_index(name='count')

            options2 = {
                "yAxis": {
                    "type": "category",
                    "data": df_langs['Language'].tolist(),
                },
                "xAxis": {"type": "value"},
                "series": [{"data": df_langs['count'].tolist(), "type": "bar"}],
            }
            st_echarts(options=options2, height="500px")

            # Most Replied Comments
            st.subheader("Most Replied Comments")
            df_replies = df[['Author', 'Comment', 'Timestamp', 'TotalReplies']].sort_values(
                'TotalReplies', ascending=False).reset_index(drop=True)
            st.table(df_replies.head(11))

            # Sentiments of the Commentors
            st.subheader("Sentiments")
            sentiments = df[df['Language'] == 'English']
            data_sentiments = sentiments['TextBlob_Sentiment_Type'].value_counts(
            ).rename_axis('Sentiment').reset_index(name='counts')

            result = data_sentiments.to_json(orient="split")
            parsed = json.loads(result)

            options = {
                "tooltip": {"trigger": "item"},
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
                            "label": {"show": True, "fontSize": "30", "fontWeight": "bold"}
                        },
                        "labelLine": {"show": False},
                        "data": [
                            # NEUTRAL
                            {"value": parsed['data'][1][1],
                             "name": parsed['data'][1][0]},
                            # POSITIVE
                            {"value": parsed['data'][0][1],
                             "name": parsed['data'][0][0]},
                            # NEGATIVE
                            {"value": parsed['data'][2][1],
                             "name": parsed['data'][2][0]}
                        ],
                    }
                ],
            }
            st_echarts(
                options=options, height="500px",
            )
except RuntimeError:
    st.error(
        ' The URL Should be of the form: https://www.youtube.com/watch?v=videoID', icon="🚨")
