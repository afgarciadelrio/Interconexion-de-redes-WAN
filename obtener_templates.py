
import requests
r = requests.get("http://localhost:3080/v2/templates")
for t in r.json():
    print(f"{t['name']:<40} {t['template_id']}")
