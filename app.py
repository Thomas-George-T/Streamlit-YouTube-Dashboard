from transform import get_polarity, get_sentiment, parse_video
import streamlit as st
import pandas as pd
import numpy as np

st.title('Real Time YouTube Analytics')

video_url = st.text_input('Enter the URL of the YouTube Video')
if video_url:
    st.video(video_url)
    df = parse_video(video_url)
    st.header("Top Comments")
    st.dataframe(df[['Author','Comment','Likes','Timestamp']])