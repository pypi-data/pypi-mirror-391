import requests, re, json

def g():
    h = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get('https://chat-deep.ai/', headers=h, timeout=10)
        if r.status_code != 200:
            return None
        for pat in (r'"nonce":"([a-f0-9]+)"', r'nonce["\']?\s*:\s*["\']([a-f0-9]+)["\']'):
            m = re.search(pat, r.text)
            if m:
                return m.group(1)
        return None
    except:
        return None

def clean(x):
    return re.sub(r'<think>.*?</think>', '', x, flags=re.DOTALL).strip()

def s(m):
    for _ in range(2):
        n = g()
        if not n:
            continue
        u = "https://chat-deep.ai/wp-admin/admin-ajax.php"
        p = {
            'action': 'deepseek_chat',
            'message': m,
            'model': 'deepseek-chat',
            'nonce': n,
            'save_conversation': '0',
            'session_only': '1'
        }
        h = {
            'User-Agent': "Mozilla/5.0",
            'Origin': "https://chat-deep.ai",
            'Referer': "https://chat-deep.ai/",
            'Content-Type': "application/x-www-form-urlencoded"
        }
        try:
            r = requests.post(u, data=p, headers=h, timeout=30)
            if r.status_code == 200:
                j = r.json()
                if j.get('success'):
                    d = j.get('data', {})
                    resp = clean(d.get('response', ''))
                    print(f"\n🤖: {resp}")
                    d['response'] = resp
                    return d
        except:
            pass
    return None

def chat():
    first = input("\nYOU: ").strip()
    s(first)
    while True:
        i = input("\nYOU: ").strip()
        if i.lower() in ['exit', 'خروج']:
            break
        if not i:
            continue
        if not s(i):
            print("❌")