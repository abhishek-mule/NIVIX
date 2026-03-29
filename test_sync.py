#!/usr/bin/env python3
"""Test frontend-backend sync"""
import urllib.request, json, sys

def test_compile(prompt):
    url = 'https://nivix.onrender.com/api/compile'
    data = json.dumps({"prompt": prompt}).encode()
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        res = urllib.request.urlopen(req, timeout=30)
        body = json.loads(res.read().decode())
        
        if body.get('status') != 'success':
            print(f"[FAIL] Status: {body.get('status')}")
            return False
            
        cir = body.get('cir', {})
        
        required = ['nodes', 'transforms', 'constraints', 'attention', 'meta']
        for f in required:
            if f not in cir:
                print(f"[FAIL] Missing field: {f}")
                return False
        
        nodes = cir.get('nodes', [])
        transforms = cir.get('transforms', [])
        
        print(f"[OK] Compiled: {len(nodes)} nodes, {len(transforms)} transforms")
        print(f"  Confidence: {cir.get('meta',{}).get('semantic_confidence')}")
        print(f"  Template: {cir.get('meta',{}).get('template')}")
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    prompts = ["explain gravity", "prime numbers", "derivative"]
    print("Testing frontend-backend sync...\n")
    
    all_pass = True
    for p in prompts:
        print(f"Prompt: '{p}'")
        if not test_compile(p):
            all_pass = False
        print()
    
    sys.exit(0 if all_pass else 1)