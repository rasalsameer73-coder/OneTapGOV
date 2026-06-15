import json, urllib.request, sys, traceback
body = {"email": "copilot.test+1@example.com", "password": "Password123!", "full_name": "Copilot Test", "phone_number": "+10000000000"}
req = urllib.request.Request('http://127.0.0.1:8000/api/v1/auth/signup', data=json.dumps(body).encode('utf-8'), headers={'Content-Type': 'application/json'})
try:
    resp = urllib.request.urlopen(req)
    print('STATUS', resp.status)
    print(resp.read().decode('utf-8'))
except Exception as e:
    traceback.print_exc()
    if hasattr(e, 'code'):
        print('HTTP_CODE', e.code)
        try:
            body = e.read().decode('utf-8')
            print('BODY', body)
        except Exception:
            pass
    sys.exit(1)
