from configparser import ConfigParser
from datetime import datetime
import requests
import re
import time
import os
import json
import bs4

#Log function
def logger(x):
    print(x)
    log_message = {"content": x}
    requests.post(log_webhook_url, json=log_message)

# Config parser
config = ConfigParser()
if os.path.isfile("config.ini"):
    config.read("config.ini", encoding='utf-8')
    urls_str = config["Directory"]["urls"]
    urls = [url.strip().strip('"') for url in urls_str.strip('][').split(',')]
    check_interval = int(config["Function"]["check_interval"].strip('"'))
    past_items_file = config["Function"][f"past_items_file"].strip('"')
    log_webhook_url = config["Discord"]["log_webhook_url"].strip('"')
    alert_webhook_url = config["Discord"]["alert_webhook_url"].strip('"')
    discord_role_id = int(config["Discord"]["discord_role_id"].strip('"'))
    webhook_lang = config["Discord"]["webhook_lang"].strip('"')
else:
    print("[Console] No config.ini found! Exiting...")
    exit()

# Load past items from text file
past_items = set()
if os.path.isfile(past_items_file):
    logger("\n[Console] past_items.txt found!")
    with open(past_items_file, "r") as f:
        for line in f:
            past_items.add(line.strip())
else:
    logger("\n[Console] past_items.txt not found! Exiting...")
    exit()

# Loop indefinitely
logger("[Console] Starting search loop with URLs...\n")
while True:
    try:
        for url in urls:
            response = requests.get(url)
            # log to console and log webhook
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger(f"[{timestamp}] Checking {url}")

            # check for new items
            items = re.findall(r'/order/detailPage/item\?itemCode=(\d+)', response.text)

            for item_id in items:
                item_url = f"https://order.mandarake.co.jp/order/detailPage/item?itemCode={item_id}&lang={webhook_lang}"
                if item_id not in past_items:
                    #Parse the Title HTML data
                    title = "Title Unknown"
                    result = requests.get(item_url)
                    soup = bs4.BeautifulSoup(result.text, "lxml")
                    title = soup.select('title')[0].getText()

                    # Parse the Image HTML data
                    img_url = "https://i.imgur.com/p543OMk.jpg"
                    try:
                        pinterest_link = soup.select_one('a[href^="https://www.pinterest.com/"]')
                        if pinterest_link:
                            pinterest_url = pinterest_link['href']
                            media_param = pinterest_url.split('&')[1]
                            img_url = media_param.split('=')[1]
                        else:
                            logger(f"[Console] @ [{timestamp}] Imaage not found! Ignoring...")
                    except Exception as e:
                        logger(f"[Console] @ [{timestamp}] Error parsing Image: {e}")

                    # Parse the item Condition
                    condition_text = "Condition Unknown"
                    try:
                        condition_div = soup.find("tr", {"class": "condition"})
                        if condition_div:
                            condition_text = condition_div.find("td").getText()
                        else:
                            logger(f"[Console] @ [{timestamp}] Condition not found! Ignoring...")
                    except Exception as e:
                        logger(f"[Console] @ [{timestamp}] Error parsing condition: {e}")

                    # Parse the item Price
                    price = "Price Uknown"
                    try:
                        price_parse = soup.find(itemprop="price")["content"]
                        if price_parse:
                            price = price_parse
                        else:
                            logger(f"[Console] @ [{timestamp}] Price not found! Ignoring...")
                    except Exception as e:
                        logger(f"[Console] @ [{timestamp}] Error parsing Price: {e}")

                    # Parse the items store
                    store = "Store Unkown"
                    try:
                        detail_panel = soup.find("div", {"class": "detail_panel", "itemprop": "offers"})
                        if detail_panel:
                            store = detail_panel.find("p", {"class": "__shop"}).text.strip()
                        else:
                            logger(f"[Console] @ [{timestamp}] Store not found! Ignoring...")
                    except Exception as e:
                        logger(f"[Console] @ [{timestamp}] Error parsing Store: {e}")

                    # send alert webhook
                    message = {
                        "username": "Mandarake Item Notifier",
                        "avatar_url": "https://i.imgur.com/9B8cjkg.png",
                        "content": f"<@&{discord_role_id}>",
                        "embeds": [
                            {
                            "title": "New Item Found! (Click Me)",
                            "url": item_url,
                            "description": title[:-23],
                            "color": 15258703,
                            "fields": [
                                {
                                    "name": "Condition:",
                                    "value": condition_text,
                                    "inline": True
                                },
                                {
                                    "name": "Price:",
                                    "value": f"{price} Yen",
                                    "inline": True
                                },
                                {
                                    "name": "Store:",
                                    "value": store,
                                }

                            ],
                            "image": {
                                "url": img_url
                            }
                            }
                        ]
                    }
                    requests.post(alert_webhook_url, json=message)

                    # log to console and log webhook
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"\n[Console] @ [{timestamp}] New item found!!!\n{item_url}\n[Console] Sending webhook...")
                    log_message = {"content": f"[Console] @ [{timestamp}] New item found!!!"}
                    requests.post(log_webhook_url, json=log_message)

                    # add item to past_items set and save to file
                    past_items.add(item_id)
                    with open(past_items_file, "a") as f:
                        f.write(f"{item_id}\n")
                    time.sleep(1)

        if check_interval != 0:
            logger(f"\n[Console] Waiting {check_interval} seconds...")
            time.sleep(check_interval)

    except Exception as e:
        # log to console and log webhook if there's an error
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger(f"[Console] @ [{timestamp}] Error: {e}")
