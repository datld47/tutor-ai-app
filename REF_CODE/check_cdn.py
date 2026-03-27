import urllib.request
url = "https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/dist/vis-network.min.css"
try:
    urllib.request.urlopen(url)
    print("SUCCESS")
except Exception as e:
    print("ERROR:", e)
url2 = "https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/vis-network.min.js"
try:
    urllib.request.urlopen(url2)
    print("SUCCESS 2")
except Exception as e:
    print("ERROR 2:", e)
