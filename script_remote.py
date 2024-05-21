import requests
import datetime as dt
import re
import html
import os

# Constants
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
MAX_POSTS = 10
TOP_POSTS_URL = 'https://hacker-news.firebaseio.com/v0/topstories.json'
GET_ITEM_URL = 'https://hacker-news.firebaseio.com/v0/item/{}.json'
REQUEST_HEADER = {"User-Agent": "Hacker News Top 10 Bot v1.1"}

def clean_text(text, max_length=100):
    """ Removes HTML tags, unescapes HTML entities, and truncates text to the specified length. """
    cleaned_text = html.unescape(re.sub(re.compile('<.*?>'), '', text))
    if len(cleaned_text) > max_length:
        cleaned_text = f"{cleaned_text[:max_length]}..."
    return cleaned_text

def fetch_top_posts(max_posts):
    """ Fetches post IDs of top posts via the API """
    with requests.get(TOP_POSTS_URL, headers=REQUEST_HEADER) as response:
        item_ids = response.json()
        item_ids = item_ids[:max_posts]
        posts = [get_item(item_id) for item_id in item_ids]
        return posts

def get_item(item_id):
    """ Fetches post metadata """
    with requests.get(GET_ITEM_URL.format(item_id), headers=REQUEST_HEADER) as response:
        data = response.json()
        item = {}
        item['id'] = data.get('id')
        item['timestamp'] = f"{dt.datetime.fromtimestamp(data.get('time')).strftime('%Y-%m-%dT%H:%M:%S')}.000Z"
        item['by'] = data.get('by')
        item['title'] = data.get('title')
        item['comments'] = data.get('descendants')
        item['score'] = data.get('score')
        item['permalink'] = f'https://news.ycombinator.com/item?id={item["id"]}'
        item['url'] = data.get('url')
        item['text'] = data.get('text')
        if item['url'] is None:
            item['url'] = item['permalink']
        if item['text'] is None:
            item['text'] = ""
        else:
            item['text'] = clean_text(item['text'])
        return item

def send_to_webhook(posts):
    """ Sends the JSON payload to a Discord Webhook URL with all posts in a single message. """
    current_date = dt.date.today().strftime('%B %d, %Y')
    payload = {
        'username': 'Hacker News',
        'avatar_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Y_Combinator_logo.svg/240px-Y_Combinator_logo.svg.png',
        'content': f"**Top {MAX_POSTS} Posts from Hacker News ({current_date})**",
        'embeds': [
            {
                'color': '16737792',
                'description': '\n\n'.join([f"**[{post['title']}]({post['url']})**\n{clean_text(post['text'], max_length=100)}\n\n**Post ID:** [{post['id']}]({post['permalink']}) | **Score:** {post['score']} points | **Comments:** {post['comments']}\n**By:** {post['by']} | **Timestamp:** {post['timestamp']}" if post['url'] != post['permalink'] else f"**{post['title']}**\n{clean_text(post['text'], max_length=100)}\n\n**Post ID:** [{post['id']}]({post['permalink']}) | **Score:** {post['score']} points | **Comments:** {post['comments']}\n**By:** {post['by']} | **Timestamp:** {post['timestamp']}" for post in posts]),
                'footer': {
                    'text': 'Hacker News',
                    'icon_url': 'https://news.ycombinator.com/y18.gif'
                }
            }
        ]
    }

    with requests.post(WEBHOOK_URL, json=payload) as response:
        print(f"Sent all posts (Status Code: {response.status_code})")

def main():
    print("Connecting to Hacker News...")
    posts = fetch_top_posts(MAX_POSTS)
    print("Data received. Sending to webhook...")
    send_to_webhook(posts)

if __name__ == "__main__":
    main()