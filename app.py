"""
Function to import Transformations and run the streamlit dashboard
"""
import time
import altair as alt
import plotly.graph_objects as go
import streamlit as st
from millify import millify
from transform import parse_video
from YT_metrics import youtube_metrics

st.set_page_config(
    page_title="YouTube Analytics Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
)

st.title('YouTube Analytics Dashboard')

video_url = st.text_input('Enter the URL of the YouTube Video')
if video_url:
    with st.spinner('Wait for it...'):
        time.sleep(2)

    df = parse_video(video_url)
    df_metrics = youtube_metrics(video_url)

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
    st.table(df_top.head())

    # Top Languages
    st.subheader("Languages")
    df_langs = df['Language'].value_counts().rename_axis(
        'Language').reset_index(name='count')

    lang = alt.Chart(df_langs).mark_bar().encode(
        y=alt.X('Language', sort=None, axis=alt.Axis(title='')),
        x=alt.Y('count', axis=alt.Axis(title='', tickCount=5))
    ).configure_axis(grid=False, domain=False)

    st.altair_chart(lang, theme='streamlit', use_container_width=True)

    # Sentiments of the Commentors
    st.subheader("General Sentiment")
    sentiments = df[df['Language'] == 'English']
    data_sentiments = sentiments['TextBlob_Sentiment_Type'].value_counts(
    ).rename_axis('Sentiment').reset_index(name='counts')

    palette = {"POSITIVE": "#C0EEE4",
               "NEGATIVE": "#FFCAC8",
               "NEUTRAL": "#F8F988"}
    fig_sentiment = go.Figure(
        go.Pie(values=data_sentiments['counts'],
               labels=data_sentiments['Sentiment'],
               hole=.3,
               texttemplate="%{label}<br>(%{percent})",
               textposition="outside",
               showlegend=False,
               marker_colors=data_sentiments["Sentiment"].map(palette)
               )
    )
    st.plotly_chart(fig_sentiment, use_container_width=True, theme='streamlit')

    # Most Replied Comments
    st.subheader("Most Replied Comments")
    df_replies = df[['Author', 'Comment', 'Timestamp', 'TotalReplies']].sort_values(
        'TotalReplies', ascending=False).reset_index(drop=True)
    st.table(df_replies.head())
