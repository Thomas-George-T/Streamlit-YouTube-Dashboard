"""
Function that does the transformation to pass onto streamlit
"""

import googleapiclient.discovery
import pandas as pd
import pycountry
from cleantext import clean
from langdetect import detect, LangDetectException
from textblob import TextBlob
import streamlit as st
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
import pytz


def get_polarity(text):
    """Function to get the polarity
    Args:
      text: Text used as input to determin the polarity
    Returns:
      Returns emotions expressed in a sentence.
    """
    return TextBlob(text).sentiment.polarity


def get_sentiment(polarity):
    """Function to get the sentiment based on polarity values
    Args:
        Polarity column
    Returns:
        Sentiment
    """
    if polarity > 0:
        return "POSITIVE"
    if polarity < 0:
        return "NEGATIVE"

    return "NEUTRAL"


def det_lang(language):
    """Function to detect language
    Args:
        Language column from the dataframe
    Returns:
        Detected Language or Other
    """
    try:
        lang = detect(language)
    except LangDetectException:
        lang = "Other"
    return lang


def parse_video(url) -> pd.DataFrame:
    """
    Args:
      url: URL Of the video to be parsed
    Returns:
      Dataframe with the processed and cleaned values
    """

    # Get the video_id from the url
    video_id = _extract_video_id(url)

    # creating youtube resource object
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=st.secrets["api_key"]
    )

    # retrieve youtube video results
    video_response = (
        youtube.commentThreads()
        .list(part="snippet", maxResults=100, order="relevance", videoId=video_id)
        .execute()
    )

    # empty list for storing reply
    comments = []

    # extracting required info from each result object
    for item in video_response["items"]:
        # Extracting comments
        comment = item["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
        # Extracting author
        author = item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
        # Extracting published time
        published_at = item["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
        # Extracting likes
        like_count = int(
            (
                item.get("snippet", {})
                .get("topLevelComment", {})
                .get("snippet", {})
                .get("likeCount", 0)
            )
            or 0
        )
        # Extracting total replies to the comment
        reply_count = int((item.get("snippet", {}).get("totalReplyCount", 0)) or 0)

        comments.append([author, comment, published_at, like_count, reply_count])

    df_transform = pd.DataFrame(
        {
            "Author": [i[0] for i in comments],
            "Comment": [i[1] for i in comments],
            "Timestamp": [i[2] for i in comments],
            "Likes": [i[3] for i in comments],
            "TotalReplies": [i[4] for i in comments],
        }
    )

    # Remove extra spaces and make them lower case. Replace special emojis
    df_transform["Comment"] = df_transform["Comment"].apply(
        lambda x: x.strip().lower().replace("xd", "").replace("<3", "")
    )

    # Clean text from line breaks, unicodes, emojis and punctuations
    df_transform["Comment"] = df_transform["Comment"].apply(
        lambda x: clean(
            x, no_emoji=True, no_punct=True, no_line_breaks=True, fix_unicode=True
        )
    )
    # Detect the languages of the comments
    df_transform["Language"] = df_transform["Comment"].apply(det_lang)

    # Convert ISO country codes to Languages
    df_transform["Language"] = df_transform["Language"].apply(
        lambda x: pycountry.languages.get(alpha_2=x).name
        if (x) != "Other"
        else "Not-Detected"
    )

    # Dropping Not detected languages
    df_transform.drop(
        df_transform[df_transform["Language"] == "Not-Detected"].index, inplace=True
    )

    # Determining the polarity based on english comments
    df_transform["TextBlob_Polarity"] = df_transform[["Comment", "Language"]].apply(
        lambda x: get_polarity(x["Comment"]) if x["Language"] == "English" else "",
        axis=1,
    )

    df_transform["TextBlob_Sentiment_Type"] = df_transform["TextBlob_Polarity"].apply(
        lambda x: get_sentiment(x) if isinstance(x, float) else ""
    )

    # Change the Timestamp
    df_transform["Timestamp"] = pd.to_datetime(df_transform["Timestamp"]).dt.strftime(
        "%Y-%m-%d %r"
    )

    return df_transform


def youtube_metrics(url) -> list:
    """Function to get views, likes and comment counts
    Args:
        URL: url of the youtube video
    Returns:
        List containing views, likes and comment counts
    """

    # Get the video_id from the url
    video_id = _extract_video_id(url)

    # creating youtube resource object
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=st.secrets["api_key"]
    )

    statistics_request = youtube.videos().list(part="statistics", id=video_id).execute()

    metrics = []

    # extracting required info from each result object
    for item in statistics_request["items"]:
        # Extracting views
        metrics.append(int((item.get("statistics", {}).get("viewCount", 0)) or 0))
        # Extracting likes
        metrics.append(int((item.get("statistics", {}).get("likeCount", 0)) or 0))
        # Extracting Comments
        metrics.append(int((item.get("statistics", {}).get("commentCount", 0)) or 0))

    return metrics


def _get_day_ordinal(day: int) -> str:
    """Return day number with English ordinal suffix."""
    if 11 <= day % 100 <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{suffix}"


def _format_with_ordinal(dt: datetime) -> str:
    """Format datetime like 'October 25th, 2025 02:57:33 AM'."""
    day_ordinal = _get_day_ordinal(dt.day)
    return f"{dt.strftime('%B')} {day_ordinal}, {dt.strftime('%Y %I:%M:%S %p')}"


def convert_timestamp(timestamp_str):
    """Converts a timestamp string to human-readable EST and IST times.

    Args:
      timestamp_str: The timestamp string in the format "YYYY-MM-DDTHH:MM:SSZ".

    Returns:
      A dictionary containing the human-readable EST and IST times.
    """
    utc_time = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = pytz.utc.localize(utc_time)

    est_timezone = pytz.timezone("America/New_York")
    ist_timezone = pytz.timezone("Asia/Kolkata")

    est_time = utc_time.astimezone(est_timezone)
    ist_time = utc_time.astimezone(ist_timezone)

    return {
        "EST": _format_with_ordinal(est_time),
        "IST": _format_with_ordinal(ist_time),
        "UTC": _format_with_ordinal(utc_time),
        "UTC_ISO": timestamp_str,
    }


def get_video_published_date(url):
    """Function to get the video published date
    Args:
        URL: url of the youtube video
    Returns:
        Dictionary containing the human-readable UTC,EST and IST times, and the
        original UTC ISO timestamp under key 'UTC_ISO'
    """
    # Get the video_id from the url
    video_id = _extract_video_id(url)

    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=st.secrets["api_key"]
    )

    request = youtube.videos().list(part="snippet", id=video_id)
    response = request.execute()

    if response["items"]:
        snippet = response["items"][0]["snippet"]
        published_at = snippet["publishedAt"]
        converted_times = convert_timestamp(published_at)
        title = snippet.get("title", "")
        creator = snippet.get("channelTitle", "")
        return {
            **converted_times,
            "Title": title,
            "Creator": creator,
        }
    else:
        raise ValueError("Video not found")


def _is_valid_video_id(candidate: str) -> bool:
    if len(candidate) != 11:
        return False
    for ch in candidate:
        if not (ch.isalnum() or ch in ['-', '_']):
            return False
    return True


def _extract_video_id(input_url: str) -> str:
    """Extract a robust YouTube video ID from various URL formats.

    Supports:
    - https://www.youtube.com/watch?v=ID&...
    - https://youtu.be/ID
    - https://www.youtube.com/shorts/ID
    - https://www.youtube.com/embed/ID
    - Raw 11-char ID
    """
    if not input_url:
        return None
    parsed = urlparse(input_url)

    # Raw ID fallback
    raw = input_url.strip()
    if _is_valid_video_id(raw):
        return raw

    # watch?v=ID
    if parsed.query:
        qs = parse_qs(parsed.query)
        vid = qs.get('v', [None])[0]
        if vid and _is_valid_video_id(vid):
            return vid

    # Path-based formats
    host = (parsed.hostname or '').lower()
    path_parts = [p for p in (parsed.path or '').split('/') if p]

    if host in ('youtu.be', 'www.youtu.be') and path_parts:
        candidate = path_parts[0]
        return candidate if _is_valid_video_id(candidate) else None

    if host.endswith('youtube.com') and path_parts:
        if path_parts[0] in ('shorts', 'embed', 'v') and len(path_parts) > 1:
            candidate = path_parts[1]
            return candidate if _is_valid_video_id(candidate) else None

    return None


def get_delta_str(published_date):
    """Function to get the delta string
    Args:
        published_date: Dictionary containing the human-readable UTC,EST and IST times, and the
        original UTC ISO timestamp under key 'UTC_ISO'
    Returns:
        Delta string
    """

    # Compute relative time delta from UTC
    published_utc = datetime.strptime(
        published_date["UTC_ISO"], "%Y-%m-%dT%H:%M:%SZ"
    ).replace(tzinfo=timezone.utc)
    now_utc = datetime.now(timezone.utc)
    delta = now_utc - published_utc
    days = delta.days
    seconds = delta.seconds
    if days > 0:
        delta_str = f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds >= 3600:
        hours = seconds // 3600
        delta_str = f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds >= 60:
        minutes = seconds // 60
        delta_str = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        delta_str = "just now"
    return delta_str


if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    df_main = parse_video(url)
    df_yt = youtube_metrics(url)
    df_published_date = get_video_published_date(url)
    print(df_main.head())
    print(df_yt)
    print(df_published_date["EST"])
    print(df_published_date["IST"])
    df_delta_time = get_delta_str(df_published_date)
    print(df_delta_time)
