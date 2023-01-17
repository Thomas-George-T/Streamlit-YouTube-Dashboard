"""
Function to import Transformations and run the streamlit dashboard
"""
import altair as alt
import plotly.graph_objects as go
import streamlit as st


from transform import parse_video

st.set_page_config(
    page_title="Real-Time YouTube Analytics Dashboard",
    page_icon="💹",
    layout="wide",
)

st.title('Real Time YouTube Analytics')

video_url = st.text_input('Enter the URL of the YouTube Video')
if video_url:

    st.subheader("Video")
    st.video(video_url)
    df = parse_video(video_url)

    st.subheader("Top Comments")
    df_top = df[['Author', 'Comment', 'Timestamp', 'Likes']].sort_values(
        'Likes', ascending=False).reset_index(drop=True)
    st.table(df_top.head())

    st.subheader("Top Languages")
    df_langs = df['Language'].value_counts().rename_axis(
        'Language').reset_index(name='counts')

    lang = alt.Chart(df_langs).mark_bar().encode(
        y=alt.X('Language', sort=None, axis=alt.Axis(title='')),
        x=alt.Y('counts', axis=alt.Axis(title=''))
    )

    st.altair_chart(lang, theme='streamlit', use_container_width=True)

    st.subheader("Most Replied Comments")
    df_replies = df[['Author', 'Comment', 'Timestamp', 'TotalReplies']].sort_values(
        'TotalReplies', ascending=False).reset_index(drop=True)
    st.table(df_replies.head())

    st.subheader("Sentiments")
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
