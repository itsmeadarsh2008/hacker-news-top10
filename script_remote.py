import requests
import datetime as dt
import os

# Constants
WEBHOOK_URL = os.environ['WEBHOOK_URL']
MAX_POSTS = 10
MONTHS = [None, 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
TOP_POSTS_URL = 'https://hacker-news.firebaseio.com/v0/topstories.json'
GET_ITEM_URL = 'https://hacker-news.firebaseio.com/v0/item/{}.json'
REQUEST_HEADER = {"User-Agent": "Hacker News Top 10 Bot v1.0"}

def fetch_top_posts(max_posts):
  with requests.get(TOP_POSTS_URL, headers=REQUEST_HEADER) as response:
    item_ids = response.json()
    item_ids = item_ids[:max_posts]
    posts = [get_item(item_id) for item_id in item_ids]

    return posts

def get_item(item_id):
  with requests.get(GET_ITEM_URL.format(item_id), headers=REQUEST_HEADER) as response:
    data = response.json()

    item = {}
    item['id'] = data.get('id')
    item['time'] = str(dt.datetime.fromtimestamp(data.get('time')))
    item['by'] = data.get('by')
    item['title'] = data.get('title')
    item['comments'] = data.get('descendants')
    item['score'] = data['score']
    item['permalink'] = f'https://news.ycombinator.com/item?id={item["id"]}'
    item['url'] = data.get('url')

    if item['url'] == None:
      item['url'] = item['permalink']

    return item

def send_to_webhook(posts):
  """
  Sends the JSON payload to a Discord Webhook URL

  Parameters
  ----------
  posts : list
    A list of posts.
  """
  current_date = dt.date.today()

  payload = {
    'username': 'Hacker News',
    'content': f"**Top {MAX_POSTS} Posts from Hacker News ({MONTHS[current_date.month]} {current_date.day}, {current_date.year})**",
    'embeds': [
      {
        'title': f"{post['title']}",
        'url': f"{post['url']}",
        'description': f"{post['comments']} comment{'' if post['comments'] == 1 else 's'}",
        'fields': [
          {
            'name': 'Post ID',
            'value': f"[{post['id']}]({post['permalink']})",
            'inline': True
          },
          {
            'name': 'Score',
            'value': f"{post['score']} points",
            'inline': True
          },
          {
            'name': 'Posted by',
            'value': f"{post['by']}",
            'inline': True
          },
          {
            'name': 'Posted on',
            'value': f"{post['time']}",
            'inline': True
          }
        ],
      } for post in posts
    ]
  }

  with requests.post(WEBHOOK_URL, json=payload) as response:
    print(response.status_code)

def main():
  print("Connecting to Hacker News...")
  posts = fetch_top_posts(MAX_POSTS)
  print("Data received. Sending to webhook...")
  send_to_webhook(posts)

if __name__ == "__main__":
  main()
