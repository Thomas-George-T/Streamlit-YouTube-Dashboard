# from transform import get_polarity, get_sentiment, parse_video
from transform import parse_video
import streamlit as st
import altair as alt
# import pandas as pd
# import numpy as np


st.set_page_config(
    page_title="Real-Time YouTube Analytics Dashboard",
    page_icon="✅",
    # layout="wide",
)


st.title('Real Time YouTube Analytics')

video_url = st.text_input('Enter the URL of the YouTube Video')
if video_url:
    
    st.subheader("Video")
    st.video(video_url)
    df = parse_video(video_url) 

    st.subheader("Top Comments")
    df_top = df[['Author','Comment','Likes','Timestamp']].sort_values('Likes', ascending=False)
    st.dataframe(df_top.head())

    st.subheader("Top Languages")
    df_langs =  df['Language'].value_counts().rename_axis('Language').reset_index(name='counts')
    
    lang = alt.Chart(df_langs).mark_bar().encode(
     y=alt.X('Language', sort=None, axis=alt.Axis(title='')),
     x=alt.Y('counts', axis=alt.Axis(title=''))
    )

    st.altair_chart(lang, theme='streamlit', use_container_width=True)

