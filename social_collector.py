# social_collector.py
import requests
import tweepy

# ============= FACEBOOK =============
def fetch_facebook_posts(page_id, access_token, limit=5):
    url = f"https://graph.facebook.com/{page_id}/posts"
    params = {"access_token": access_token, "limit": limit, "fields": "message,created_time"}
    res = requests.get(url, params=params)
    data = res.json()
    posts = []
    for item in data.get("data", []):
        if "message" in item:
            posts.append({
                "source": "Facebook",
                "text": item["message"],
                "time": item["created_time"]
            })
    return posts


# ============= TWITTER (X) =============
def fetch_twitter_posts(keyword, api_key, api_secret, access_token, access_secret, limit=5):
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
    api = tweepy.API(auth)
    tweets = api.search_tweets(q=keyword, lang="vi", count=limit)
    results = []
    for t in tweets:
        results.append({
            "source": "Twitter",
            "text": t.text,
            "time": str(t.created_at)
        })
    return results


# ============= INSTAGRAM =============
def fetch_instagram_posts(user_id, access_token, limit=5):
    url = f"https://graph.instagram.com/{user_id}/media"
    params = {"access_token": access_token, "fields": "caption,timestamp", "limit": limit}
    res = requests.get(url, params=params)
    data = res.json()
    posts = []
    for item in data.get("data", []):
        if "caption" in item:
            posts.append({
                "source": "Instagram",
                "text": item["caption"],
                "time": item["timestamp"]
            })
    return posts
