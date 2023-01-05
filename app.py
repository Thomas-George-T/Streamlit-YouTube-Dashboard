from googleapiclient.discovery import build
import pandas as pd
from cleantext import clean
from langdetect import detect
import pycountry
from textblob import TextBlob


def get_polarity(text):
    """Function to get the polarity
    Args:
      text: Text used as input to determin the polarity
    Returns:
      Returns emotions expressed in a sentence.
    """
    return TextBlob(text).sentiment.polarity

def get_sentiment(polarity):
   if polarity > 0:
    return 'POSITIVE'
   elif polarity<0:
    return 'NEGATIVE' 
   else:
     return 'NEUTRAL'


def parse_video(url) -> pd.DataFrame:
    """
    Args:
      url: URL Of the video to be parsed
    Returns:
      Dataframe with the processed and cleaned values
    """

    # Getting the secret API key
    api_key = ''
    
    # Get the video_id from the url
    video_id = url.split('?v=')[-1]

    # creating youtube resource object
    youtube = build('youtube', 'v3',
    developerKey=api_key)

    # retrieve youtube video results
    video_response=youtube.commentThreads().list(
    part='snippet',
    maxResults=1000,
    order='relevance',
    videoId=video_id
    ).execute()

    # empty list for storing reply
    comments = []

    # extracting required info from each result object
    for item in video_response['items']:

        # Extracting comments
        comment = item['snippet']['topLevelComment']['snippet']['textOriginal']
        # Extracting author
        author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
        # Extracting published time
        published_at = item['snippet']['topLevelComment']['snippet']['publishedAt']
        # Extracting likes
        like_count = item['snippet']['topLevelComment']['snippet']['likeCount']
        # Extracting total replies to the comment
        reply_count = item['snippet']['totalReplyCount']

        comments.append([author, comment, published_at, like_count, reply_count])

    df = pd.DataFrame({'Author': [i[0] for i in comments], 
                      'Comment': [i[1] for i in comments], 
                      'Timestamp': [i[2] for i in comments],
                    'Likes': [i[3] for i in comments], 
                    'TotalReplies': [i[4] for i in comments]})

    # Remove extra spaces and make them lower case. Replace special emojis
    df['Comment'] = df['Comment'].apply(lambda x: x.strip().lower().
                                        replace('xd','').replace('<3',''))

    # Clean text from line breaks, unicodes, emojis and punctuations
    df['Comment'] = df['Comment'].apply(lambda x: clean(x, 
    no_emoji=True,
    no_punct=True,
    no_line_breaks=True,
    fix_unicode=True))

    # Detect the languages of the comments
    df['Language'] = df['Comment'].apply(lambda x: detect(x))

    # Convert ISO country codes to Languages
    df['Language'] = df['Language'].apply(lambda x: pycountry.languages.get(alpha_2=x).name)

    # Determining the polarity based on english comments
    df['TextBlob_Polarity'] = df[['Comment','Language']].apply(lambda x: get_polarity(x['Comment']) if x['Language'] == 'English' else '', axis=1)

    df['TextBlob_Sentiment_Type'] = df['TextBlob_Polarity'].apply(lambda x: get_sentiment(x) if type(x)==float else '')


    return df


if __name__ == "__main__":  
    df = parse_video('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
    print(df.head())
