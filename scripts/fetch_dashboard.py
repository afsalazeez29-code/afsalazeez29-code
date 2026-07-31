"""Fetch real public GitHub language, project, and social-profile data."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_PROFILE_USER", "afsalazeez29-code")
TOKEN = os.environ.get("GH_TOKEN", "")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "dashboard.json"
API = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": f"{USERNAME}-profile-dashboard"}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

PROJECTS = {
    "RSP-PROJECT": {"title": "Recipe.IO", "description": "Recipe sharing platform"},
    "JailMeet2.0": {"title": "JailMeet", "description": "Secure prison visit and parole management platform"},
}


def get(path: str):
    response = requests.get(f"{API}{path}", headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def logo_url(repo: dict) -> str | None:
    """Use a repository-owned logo/favicon when one is available."""
    try:
        tree = get(f"/repos/{USERNAME}/{repo['name']}/git/trees/{repo['default_branch']}?recursive=1")["tree"]
    except (requests.RequestException, KeyError):
        return None
    candidates = [item["path"] for item in tree if item.get("type") == "blob" and re.search(r"(?:^|/)(?:favicon|logo|icon)[^/]*\.(?:png|jpe?g|svg)$", item["path"], re.I)]
    if not candidates:
        return None
    path = candidates[0]
    return f"https://raw.githubusercontent.com/{USERNAME}/{repo['name']}/{repo['default_branch']}/{path}"


def language_percentages(language_bytes: dict[str, int]) -> list[dict[str, float | str]]:
    total = sum(language_bytes.values())
    if not total:
        return []
    return [{"name": name, "bytes": count, "percent": round(count * 100 / total, 1)} for name, count in sorted(language_bytes.items(), key=lambda item: item[1], reverse=True)]


def social_links() -> dict[str, str]:
    # Verified public profile links; the page fetch below refreshes them when exposed.
    links = {"GitHub": f"https://github.com/{USERNAME}", "LinkedIn": "https://www.linkedin.com/in/afsal-a-azeez29", "Instagram": "https://www.instagram.com/afzyl._"}
    page = requests.get(f"https://github.com/{USERNAME}", headers=HEADERS, timeout=30)
    if page.ok:
        soup = BeautifulSoup(page.text, "html.parser")
        for anchor in soup.select("a[href]"):
            href = anchor["href"].strip()
            if "linkedin.com/in/" in href:
                links["LinkedIn"] = href if href.startswith("http") else f"https://www.linkedin.com{href}"
            elif "instagram.com/" in href:
                links["Instagram"] = href if href.startswith("http") else f"https://www.instagram.com{href}"
    profile = get(f"/users/{USERNAME}")
    if profile.get("email"):
        links["Email"] = f"mailto:{profile['email']}"
    return links


def main() -> None:
    repos = get(f"/users/{USERNAME}/repos?type=owner&sort=updated&per_page=100")
    public_repos = [repo for repo in repos if not repo["private"] and not repo.get("fork")]
    totals: dict[str, int] = {}
    project_data = []
    for repo in public_repos:
        languages = get(f"/repos/{USERNAME}/{repo['name']}/languages")
        for language, byte_count in languages.items():
            totals[language] = totals.get(language, 0) + byte_count
        if repo["name"] in PROJECTS:
            project_data.append({
                **PROJECTS[repo["name"]],
                "repository": repo["name"], "url": repo["html_url"], "visibility": "Public",
                "updated_at": repo["updated_at"], "languages": language_percentages(languages),
                "logo_url": logo_url(repo),
            })
    project_data.sort(key=lambda project: ["Recipe.IO", "JailMeet"].index(project["title"]))
    data = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "languages": language_percentages(totals),
        "projects": project_data,
        "socials": social_links(),
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}: {len(public_repos)} public repositories, {len(totals)} languages")


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as exc:
        raise SystemExit(f"GitHub API request failed: {exc}")
