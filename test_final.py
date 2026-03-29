#!/usr/bin/env python3
"""Test working API format"""
import urllib.request, json

# The ONLY working format on deployed version
url = 'https://nivix.onrender.com/api/compile'
tests = [
    {"prompt": "explain gravity"},
    {"prompt": "show derivative"},
    {"prompt": "prime numbers"},
]

for t in tests:
    data = json.dumps(t).encode()
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        res = urllib.request.urlopen(req, timeout=30)
        body = json.loads(res.read().decode())
        cir = body.get('cir', {})
        nodes = cir.get('nodes', [])
        meta = cir.get('meta', {})
        print(f"[OK] {t['prompt'][:20]}: {len(nodes)} nodes, {meta.get('template', 'N/A')}")
    except Exception as e:
        print(f"[FAIL] {t['prompt'][:20]}: {e}")