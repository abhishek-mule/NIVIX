import urllib.request, json
req = urllib.request.Request('https://nivix.onrender.com/api/compile', data=b'{"prompt":"test dynamic"}', headers={'Content-Type': 'application/json'})
res = urllib.request.urlopen(req)
data = json.loads(res.read().decode('utf-8'))
print("TEMPLATE RETURNED:", data['cir']['meta']['template'])
