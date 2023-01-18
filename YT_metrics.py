import googleapiclient.discovery
import pandas as pd
import streamlit as st

def youtube_metrics(url)->pd.DataFrame:

    # Get the video_id from the url
    video_id = url.split('?v=')[-1]

    # creating youtube resource object
    youtube = googleapiclient.discovery.build(
        'youtube', 'v3', developerKey=st.secrets["api_key"])

    statistics_request = youtube.videos().list(
        part="statistics",
        id=video_id
    ).execute()

    metrics = []

    # extracting required info from each result object
    for item in statistics_request['items']:

        # Extracting views
        metrics.append(item['statistics']['viewCount'])
        # Extracting likes
        metrics.append(item['statistics']['likeCount'])
        # Extracting Comments
        metrics.append(item['statistics']['commentCount'])

    return metrics

if __name__ == "__main__":
    df_main = youtube_metrics('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
    print(df_main)
