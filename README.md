![GitHub](https://img.shields.io/github/license/Thomas-George-T/Streamlit-YouTube-Dashboard.svg?style=flat)
![GitHub top language](https://img.shields.io/github/languages/top/Thomas-George-T/Streamlit-YouTube-Dashboard.svg?style=flat)
![GitHub last commit](https://img.shields.io/github/last-commit/Thomas-George-T/Streamlit-YouTube-Dashboard.svg?style=flat)
![ViewCount](https://views.whatilearened.today/views/github/Thomas-George-T/Streamlit-YouTube-Dashboard.svg?cache=remove)

# YouTube Dashboard on Streamlit

<p align="center">  
    <br>
	<a href="#">
        <img height=100 src="https://cdn.svgporn.com/logos/youtube-icon.svg" hspace=20> 
	<img src="https://raw.githubusercontent.com/Thomas-George-T/Thomas-George-T/master/assets/python.svg" alt="Python" title="Python" width ="120" />
        <img height=100 src="https://cdn.svgporn.com/logos/streamlit.svg" hspace=20> 
  </a>	
</p>
<br>
Generating analytics based on a YouTube video and displaying key insights as a dashboard app hosted on Streamlit.

## Key Performance Indicators (KPI's)
For the dashboard, the following metrics are calculated:
- Total Number of Views
- Total Number of Likes
- Total Number of Comments
- Most Liked Comments 
- Comments in Different Languages on the video
- Most Replied Comments
- General Sentiment/Review Analysis

## Environment
- Python 3.10
- YouTube API
- Streamlit cloud

## Design
There are several steps to how the data pipeline is built. They are as follows:
- Create an API key with YouTube Data. Version 3 of the API was used for this project
- Extract the videoID from a given YouTube URL. This is usually the part that comes after the `v=` in the query string
- Using the API key, pull `snippet` and `statistics` from the YouTube API based on the video ID
- `Snippet` from `CommentThreads` contains many apis. We focus mainly on Author, Comments, Timestamp, likes, replies
- The `videos` api contains important `statistics` like viewCount, Likes and Total Comments
- After processing all the required information, they are returned as dataframes
- These dataframes are used as the basis for various visualizations as displayed on the dashboard
- Using the capabilites and different components of Streamlit, we design the dashboard with KPI's
- Deploy the app for free on [streamlit cloud](https://streamlit.io/cloud)

## Demo
The dashboard can be used for any YouTube video and can be viewed on [streamlit](https://thomas-george-t-youtube-dashboard-app.streamlit.app)

## Future Scope
- The YouTube API is limited to only 100 results per page. The workaround for this is to run a loop while processing the results from the first API request. Once this gets patched in the future, the analytics can be extended to show more NLP based Sentimental analysis and more Language related analytics. This is because there would be more data points to go on beyond the initial 100.
- A time series model/analytics can be displayed based on KPI's. For example:
  - Change of Likes over the last 30 days
  - Trend of viewership
  - Change in sentiments
