# social_collector.py
import requests
import tweepy

# ================== CONFIG ==================
# lấy token : 'me/accounts' -> submit, không lấy token do app tự tạo
FACEBOOK_ACCESS_TOKEN = "EAATH6l0HjMoBQE9FzYKlAx1szkqfoRAimAuLdZBUNPzkiCWzXUSYH9UmeRbd1RXnxDU9lL0P292ymqsZBAQwrYu9IndgKbLxcHu3OBN3tr8UEAl8E1iefKrow7BkHE1wD6JOoZCBcBgZBLDjSjR4fejODLbOBomeuZCuyrCT9FwrNtoLSUsUMJtOgqbuC9lCFAHs0SdtHTyy2WeAu664WfdweQlZAgNL9LF6S67bde"

# Nếu bạn hay lấy bài viết từ 1 page cố định, có thể set luôn PAGE_ID ở đây
FACEBOOK_PAGE_ID = "865644263301929"  # hoặc ID Page, ví dụ: "123456789012345"


# ============= FACEBOOK =============
def fetch_facebook_posts(page_id=FACEBOOK_PAGE_ID, access_token=FACEBOOK_ACCESS_TOKEN, limit=5):
    """
    Lấy bài viết từ Facebook Page qua Graph API.
    - page_id: 'me' nếu token là của page đó, hoặc ID của page
    - access_token: Facebook Page Access Token
    """
    url = f"https://graph.facebook.com/{page_id}/posts"
    params = {
        "access_token": access_token,
        "limit": limit,
        "fields": "message,created_time"
    }
    res = requests.get(url, params=params)
    data = res.json()

    # Debug nếu lỗi
    if "error" in data:
        print("Facebook API Error:", data["error"])
        return []

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


# ============= TEST ĐƠN GIẢN =============
if __name__ == "__main__":
    # Test lấy 5 bài viết Facebook gần nhất
    fb_posts = fetch_facebook_posts(limit=5)
    for p in fb_posts:
        print(p["time"], "=>", p["text"])
