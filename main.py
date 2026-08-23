import urllib.request

url = "https://books.toscrape.com/robots.txt"
req = urllib.request.Request(url, headers={"User-Agent": "FlyRankInternshipA9/1.0"})

try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        print(resp.status)
        print(resp.read().decode())
except Exception as e:
    print("Error: ", e)