import praw
import tweepy
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import schedule
import time
import tensorflow as tf
import tf_keras as keras
from dotenv import load_dotenv
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
load_dotenv()

def fetch_reddit_trending_topics():
    print("Fetching Reddit trending topics...")
    reddit = praw.Reddit(
        client_id=os.getenv('client_id'),
        client_secret=os.getenv('client_secret'),
        user_agent=os.getenv('user_agent')
    )
    topics = []
    try:
        for submission in reddit.subreddit("technology").hot(limit=5):
            topics.append(submission.title)
    except Exception as e:
        print(f"Error fetching Reddit topics: {e}")
    return topics

def fetch_twitter_trending_topics():
    print("Fetching Twitter trending topics...")
    try:
        client = tweepy.Client(bearer_token=os.getenv('X_TOKEN'))
        response = client.get_place_trends(woeid=1)
        if response.data:
            return [trend["name"] for trend in response.data[0]["trends"][:5]]
        else:
            print("No trending data returned from Twitter.")
    except Exception as e:
        print(f"Error fetching Twitter trends: {e}")
    return []

def fetch_techcrunch_topics():
    print("Fetching TechCrunch topics...")
    url = "https://techcrunch.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    headlines = soup.find_all("h2", class_="post-block__title", limit=5)
    return [headline.get_text(strip=True) for headline in headlines]

def fetch_medium_topics():
    print("Fetching Medium topics...")
    url = "https://medium.com/topic/technology"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    titles = soup.find_all("h2", limit=5)
    return [title.get_text(strip=True) for title in titles]

def generate_blog_post(topic):
    print(f"Generating blog post for: {topic}")
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    prompt = (
        f"Write a detailed, engaging, and professional tech blog post about '{topic}', "
        f"highlighting its global impact, recent trends, and future implications."
    )
    try:
        summary = summarizer(prompt, max_length=300, min_length=200, do_sample=False)
        return summary[0]["summary_text"]
    except Exception as e:
        print(f"Error generating blog post for {topic}: {e}")
        return "Error generating blog post."

def format_post(topic, content):
    return f"**{topic}**\n\n{content}\n\n#Tech #Innovation #AI #FutureOfTech #Trending"

def fetch_all_topics():
    print("Fetching all topics...")
    reddit_topics = fetch_reddit_trending_topics()
    twitter_topics = fetch_twitter_trending_topics()
    techcrunch_topics = fetch_techcrunch_topics()
    medium_topics = fetch_medium_topics()
    return reddit_topics + twitter_topics + techcrunch_topics + medium_topics

def generate_posts():
    print("Fetching trending tech topics...\n")
    topics = fetch_all_topics()
    if not topics:
        print("No topics fetched. Exiting.")
        return
    print(f"Generated topics: {topics}\n")
    print("Generating tech blog posts...\n")
    for topic in topics:
        content = generate_blog_post(topic)
        post = format_post(topic, content)
        print(post)
        print("\n" + "-" * 50 + "\n")  # Separator between posts

# Run once for testing
generate_posts()
