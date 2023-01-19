"""
Function to import Transformations and run the streamlit dashboard
"""
import time
import json
import altair as alt
import streamlit as st
from streamlit_echarts import st_echarts
from millify import millify
from transform import parse_video
from yt_metrics import youtube_metrics


st.set_page_config(
    page_title="YouTube Analytics Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
)

st.title('YouTube Analytics Dashboard')

video_url = st.text_input('Enter URL',
                          placeholder='Example: https://www.youtube.com/watch?v=Il0S8BoucSA')
if video_url:
    df = parse_video(video_url)
    df_metrics = youtube_metrics(video_url)

    with st.spinner('Crunching numbers...'):
        time.sleep(3)

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("**Views**", millify(df_metrics[0], precision=2))
    col2.metric("**Likes**", millify(df_metrics[1], precision=2))
    col3.metric("**Comments**", millify(df_metrics[2], precision=2))

    # Embedded Video
    st.video(video_url)

    # Top Comments
    st.subheader("Most liked comments")
    df_top = df[['Author', 'Comment', 'Timestamp', 'Likes']].sort_values(
        'Likes', ascending=False).reset_index(drop=True)
    st.table(df_top.head(10))

    # Top Languages
    st.subheader("Languages")
    df_langs = df['Language'].value_counts().rename_axis(
        'Language').reset_index(name='count')

    lang = alt.Chart(df_langs).mark_bar().encode(
        y=alt.X('Language', sort=None, axis=alt.Axis(title='')),
        x=alt.Y('count', axis=alt.Axis(title='', tickCount=5))
    ).configure_axis(grid=False, domain=False)

    st.altair_chart(lang, theme='streamlit', use_container_width=True)


    # Most Replied Comments
    st.subheader("Most Replied Comments")
    df_replies = df[['Author', 'Comment', 'Timestamp', 'TotalReplies']].sort_values(
        'TotalReplies', ascending=False).reset_index(drop=True)
    st.table(df_replies.head())

    # Sentiments of the Commentors
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
