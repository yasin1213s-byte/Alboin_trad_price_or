import requests
import os

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CITIES = ["Martlock", "Lymhurst", "Bridgewatch", "Fort Sterling", "Thetford", "Caerleon"]

def get_prices(item_id):
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{item_id}"
    response = requests.get(url)
    return response.json()

def analyze_item(item_id):
    data = get_prices(item_id)
    
    prices = {}
    for entry in data:
        city = entry["city"]
        sell_price = entry["sell_price_min"]
        if city in CITIES and sell_price > 0:
            prices[city] = sell_price
    
    if not prices:
        return None
    
    cheapest_city = min(prices, key=prices.get)
    expensive_city = max(prices, key=prices.get)
    cheapest_price = prices[cheapest_city]
    expensive_price = prices[expensive_city]
    profit = int((expensive_price - cheapest_price) * 0.945)
    
    lines = [f"📦 *{item_id}*"]
    for city, price in sorted(prices.items(), key=lambda x: x[1]):
        lines.append(f"  {city}: {price:,} silver")
    lines.append(f"✅ بخر از: *{cheapest_city}* ({cheapest_price:,})")
    lines.append(f"💰 بفروش در: *{expensive_city}* ({expensive_price:,})")
    lines.append(f"📈 سود خالص (بعد مالیات): *{profit:,} silver*")
    
    return "\n".join(lines)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    })

def main():
    with open("items.txt") as f:
        items = [line.strip() for line in f if line.strip()]
    
    full_message = "🏪 *گزارش قیمت آلبیون*\n\n"
    
    for item in items:
        result = analyze_item(item)
        if result:
            full_message += result + "\n\n---\n\n"
    
    send_telegram(full_message)

if __name__ == "__main__":
    main()
