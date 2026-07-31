"""Fetch public GitHub contribution calendar data without credentials."""
from pathlib import Path
import datetime as dt, json, os, re
import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_PROFILE_USER", "afsalazeez29-code")
OUT = Path(__file__).resolve().parents[1] / "data" / "contributions.json"
url = f"https://github.com/users/{USERNAME}/contributions"
try:
    response = requests.get(url, headers={"User-Agent":"afsalazeez29-code-profile-readme/1.0","Accept":"text/html"}, timeout=30)
    response.raise_for_status()
except requests.RequestException as exc:
    raise SystemExit(f"Could not fetch public contributions for {USERNAME}: {exc}")
soup = BeautifulSoup(response.text, "html.parser")
days = []
for cell in soup.select("td.ContributionCalendar-day[data-date]"):
    date = cell.get("data-date")
    tooltip = soup.find("tool-tip", attrs={"for": cell.get("id")})
    label = tooltip.get_text(" ", strip=True) if tooltip else cell.get("aria-label", "")
    match = re.search(r"(\d+)\s+contribution", label, re.I)
    count = int(match.group(1)) if match else 0
    level = int(cell.get("data-level", 0) or 0)
    days.append({"date":date, "count":count, "level":max(0,min(4,level))})
if len(days) < 300:
    raise SystemExit("GitHub contribution calendar could not be parsed (fewer than 300 days found).")
days.sort(key=lambda item:item["date"])
def streaks(items):
    longest = run = 0
    for item in items:
        run = run + 1 if item["count"] else 0
        longest = max(longest, run)
    today = dt.date.today().isoformat()
    run = 0
    for item in reversed(items):
        if item["date"] == today and not item["count"]: continue
        if not item["count"]: break
        run += 1
    return run, longest
total = sum(d["count"] for d in days)
current, longest = streaks(days)
best = max(days, key=lambda item:item["count"])
monthly = {}
for day in days: monthly[day["date"][:7]] = monthly.get(day["date"][:7], 0) + day["count"]
payload = {"username":USERNAME,"generated_at":dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),"range":{"start":days[0]["date"],"end":days[-1]["date"]},"total_contributions":total,"current_streak":{"length":current},"longest_streak":{"length":longest},"best_day":{"date":best["date"],"count":best["count"]},"monthly":[{"month":k,"total":v} for k,v in sorted(monthly.items())],"days":days}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(payload, indent=2)+"\n", encoding="utf-8")
print(f"wrote {OUT}: {total} contributions")
