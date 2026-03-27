import urllib.request
try:
    response = urllib.request.urlopen('http://127.0.0.1:8081/user_data/sv01/sv01_visual_tree.html')
    print("STATUS:", response.getcode())
    print("HEADERS:")
    for k, v in response.getheaders():
        print(f"  {k}: {v}")
except Exception as e:
    print("ERROR:", e)
