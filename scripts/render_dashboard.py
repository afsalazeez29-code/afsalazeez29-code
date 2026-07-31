"""Render native SVG dashboard components from data/dashboard.json."""
from __future__ import annotations

import json
import textwrap
from datetime import datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "dashboard.json").read_text(encoding="utf-8"))
BG, BORDER, MUTED, TEXT, GREEN, BLUE = "#0d1117", "#30363d", "#8b949e", "#c9d1d9", "#9FE4FB", "#58a6ff"
LANG_COLORS = {"JavaScript":"#f1e05a", "TypeScript":"#3178c6", "Python":"#3572A5", "Java":"#b07219", "PHP":"#4F5D95", "HTML":"#e34c26", "CSS":"#563d7c", "EJS":"#a91e50", "Shell":"#89e051", "Dockerfile":"#384d54"}


def base(width: int, height: int, title: str, description: str) -> list[str]:
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">', f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>', '<style>text{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}.reveal{animation:reveal .42s ease-out both}@keyframes reveal{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}</style>', f'<rect width="{width}" height="{height}" rx="12" fill="{BG}"/><rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="12" fill="none" stroke="{BORDER}"/>']


def render_languages() -> None:
    languages = DATA["languages"]
    width, height, x, bar_y, bar_w = 860, 230, 24, 59, 812
    parts = base(width, height, "Most Used Languages", "Real language usage across public GitHub repositories.")
    parts.append(f'<text x="{x}" y="32" fill="{TEXT}" font-size="14">Most Used Languages</text><text x="{width-x}" y="32" text-anchor="end" fill="{MUTED}" font-size="11">GitHub Linguist data</text>')
    offset = x
    for index, lang in enumerate(languages):
        segment = bar_w * lang["percent"] / 100
        color = LANG_COLORS.get(lang["name"], BLUE)
        parts.append(f'<rect class="reveal" x="{offset:.2f}" y="{bar_y}" width="{segment:.2f}" height="16" rx="3" fill="{color}" style="animation-delay:{index*.07:.2f}s"><title>{escape(lang["name"])}: {lang["percent"]}%</title></rect>')
        offset += segment
    for index, lang in enumerate(languages):
        col, row = index % 2, index // 2
        lx, ly = x + col * 410, 113 + row * 24
        color = LANG_COLORS.get(lang["name"], BLUE)
        parts.append(f'<g class="reveal" style="animation-delay:{.18+index*.06:.2f}s"><circle cx="{lx+5}" cy="{ly-4}" r="5" fill="{color}"/><text x="{lx+18}" y="{ly}" fill="{TEXT}" font-size="11">{escape(lang["name"])}</text><text x="{lx+190}" y="{ly}" fill="{MUTED}" font-size="11">{lang["percent"]:.1f}%</text></g>')
    parts.append('</svg>')
    (ROOT / "languages.svg").write_text("".join(parts), encoding="utf-8")


def render_project_card(project: dict, x: int, index: int) -> str:
    card_w, card_h, y = 396, 255, 50
    dominant = project["languages"][0] if project["languages"] else {"name":"Unknown", "percent":0}
    color = LANG_COLORS.get(dominant["name"], BLUE)
    updated = datetime.fromisoformat(project["updated_at"].replace("Z", "+00:00")).strftime("%d %b %Y")
    description = textwrap.wrap(project["description"], width=48, break_long_words=False)[:2]
    parts = [f'<g class="reveal" style="animation-delay:{.12+index*.14:.2f}s"><rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="10" fill="#111722" stroke="{BORDER}"/>']
    if project.get("logo_url"):
        parts.append(f'<image href="{escape(project["logo_url"], quote=True)}" x="{x+18}" y="{y+18}" width="34" height="34" preserveAspectRatio="xMidYMid meet"/>')
    else:
        parts.append(f'<rect x="{x+18}" y="{y+18}" width="34" height="34" rx="7" fill="#1f6feb"/><text x="{x+35}" y="{y+41}" text-anchor="middle" fill="#fff" font-size="16">{escape(project["title"][0])}</text>')
    parts += [f'<text x="{x+66}" y="{y+34}" fill="{TEXT}" font-size="15">{escape(project["title"])}</text>', f'<text x="{x+66}" y="{y+51}" fill="{MUTED}" font-size="10">{escape(project["repository"])}</text>']
    for line_index, line in enumerate(description): parts.append(f'<text x="{x+18}" y="{y+82+line_index*14}" fill="{MUTED}" font-size="11">{escape(line)}</text>')
    parts += [f'<circle cx="{x+336}" cy="{y+110}" r="34" fill="none" stroke="#30363d" stroke-width="7"/><circle cx="{x+336}" cy="{y+110}" r="34" fill="none" stroke="{color}" stroke-width="7" stroke-dasharray="{dominant["percent"]*2.14:.1f} 214" transform="rotate(-90 {x+336} {y+110})"/><text x="{x+336}" y="{y+114}" text-anchor="middle" fill="{TEXT}" font-size="12">{dominant["percent"]:.0f}%</text>', f'<text x="{x+336}" y="{y+132}" text-anchor="middle" fill="{MUTED}" font-size="9">{escape(dominant["name"])}</text>']
    badge_x = x + 18
    for language in project["languages"][:3]:
        label = f'{language["name"]} {language["percent"]:.0f}%'
        badge_w = 12 + len(label) * 6
        parts.append(f'<rect x="{badge_x}" y="{y+155}" width="{badge_w}" height="20" rx="4" fill="#21262d"/><text x="{badge_x+6}" y="{y+169}" fill="{LANG_COLORS.get(language["name"], BLUE)}" font-size="9">{escape(label)}</text>')
        badge_x += badge_w + 7
    parts += [f'<line x1="{x+18}" x2="{x+378}" y1="{y+196}" y2="{y+196}" stroke="{BORDER}"/>', f'<text x="{x+18}" y="{y+218}" fill="{MUTED}" font-size="10">Updated {updated}</text><text x="{x+378}" y="{y+218}" text-anchor="end" fill="{GREEN}" font-size="10">● {project["visibility"]}</text>', f'<a href="{escape(project["url"], quote=True)}"><text x="{x+18}" y="{y+240}" fill="{BLUE}" font-size="10">github.com/{escape(project["repository"])}</text></a></g>']
    return "".join(parts)


def render_projects() -> None:
    parts = base(860, 330, "Featured Projects", "Two featured public GitHub projects with live repository metadata.")
    parts.append(f'<text x="24" y="32" fill="{TEXT}" font-size="14">Featured Projects</text><text x="836" y="32" text-anchor="end" fill="{MUTED}" font-size="11">Live GitHub metadata</text>')
    for index, project in enumerate(DATA["projects"]): parts.append(render_project_card(project, 24 + index * 416, index))
    parts.append('</svg>')
    (ROOT / "projects.svg").write_text("".join(parts), encoding="utf-8")


def render_connect() -> None:
    buttons = [("LinkedIn", DATA["socials"].get("LinkedIn")), ("GitHub", DATA["socials"].get("GitHub")), ("Instagram", DATA["socials"].get("Instagram")), ("Email", DATA["socials"].get("Email")), ("Portfolio", None)]
    parts = base(860, 125, "Connect", "Links to Afsal S Azeez public social profiles.")
    parts.append(f'<text x="24" y="31" fill="{TEXT}" font-size="14">Connect</text>')
    for index, (label, link) in enumerate(buttons):
        x = 24 + index * 164
        body = f'<rect x="{x}" y="52" width="148" height="45" rx="7" fill="#111722" stroke="{BORDER}"/><text x="{x+18}" y="80" fill="{GREEN if link else MUTED}" font-size="13">{">" if link else "·"}</text><text x="{x+36}" y="80" fill="{TEXT}" font-size="11">{label}</text>'
        if link: body = f'<a href="{escape(link, quote=True)}">{body}</a>'
        else: body += f'<text x="{x+36}" y="91" fill="{MUTED}" font-size="8">Coming Soon</text>'
        parts.append(f'<g class="reveal" style="animation-delay:{index*.08:.2f}s">{body}</g>')
    parts.append('</svg>')
    (ROOT / "connect.svg").write_text("".join(parts), encoding="utf-8")


render_languages(); render_projects(); render_connect()
print("wrote languages.svg, projects.svg, connect.svg")
