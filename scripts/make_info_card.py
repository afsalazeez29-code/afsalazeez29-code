"""Generate the terminal-style /info card with wrapped, dotted records."""
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 560, 565
LABEL_X, DOT_X, VALUE_X = 22, 112, 174
ROW_HEIGHT = 20

sections = [
    ("SYSTEM.INFO", [
        ("identity", "Afsal S Azeez"),
        ("role", "Full-Stack Developer"),
        ("location", "Kerala, India"),
        ("education", "BSc Computer Science · Advanced Studies"),
        ("status", "Building · Learning · Shipping"),
    ]),
    ("CORE.STACK", [
        ("Core.Lang", "TypeScript · JavaScript · Python · Java · PHP"),
        ("Core.Frontend", "Next.js · React · Vite · HTML · CSS · Bootstrap"),
        ("Core.Backend", "Node.js · Express · REST APIs · Zod"),
        ("Core.Database", "PostgreSQL · Prisma · MongoDB · Mongoose"),
        ("Core.Cloud", "AWS EC2 · Vercel · Cloudinary · Neon"),
        ("Core.Security", "JWT · RBAC · bcrypt · Validation"),
        ("Core.Deploy", "Ubuntu · PM2 · Nginx · GitHub Actions"),
        ("Core.Tools", "VS Code · Cursor · Claude Code · Codex · Antigravity · Windsurf · Trae IDE · Git · GitHub · Postman · npm"),
        ("Core.Project", "JailMeet 2.0 · Recipe Sharing Platform"),
    ]),
    ("CONTACT", [("GitHub", "@afsalazeez29-code")]),
    ("PORTFOLIO", [("Portfolio", "Coming Soon")]),
]


def wrapped(value: str) -> list[str]:
    """Wrap values at word boundaries without changing the fixed card width."""
    return textwrap.wrap(value, width=49, break_long_words=False, break_on_hyphens=False) or [""]


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">',
    '<title id="title">Afsal S Azeez developer information</title>',
    '<desc id="desc">A detailed terminal dashboard of Afsal S Azeez technical skills and project focus.</desc>',
    '<style>text{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}.line{opacity:0;animation:show .42s ease-out forwards}@keyframes show{to{opacity:1}}</style>',
    f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="#0d1117"/>',
    f'<rect x=".5" y=".5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="12" fill="none" stroke="#30363d"/>',
    '<text x="22" y="28" fill="#8b949e" font-size="12">afsal@github: ~/info</text>',
    f'<line x2="{WIDTH}" y1="42" y2="42" stroke="#30363d"/>',
]

y, animation_index = 67, 0
for section, records in sections:
    parts.append(f'<g class="line" style="animation-delay:{animation_index*.156:.3f}s"><text x="{LABEL_X}" y="{y}" fill="#8b949e" font-size="11" font-weight="700">{section}</text></g>')
    y += ROW_HEIGHT
    animation_index += 1
    for label, value in records:
        value_lines = wrapped(value)
        dots = "." * max(3, 17 - len(label))
        parts.append(
            f'<g class="line" style="animation-delay:{animation_index*.156:.3f}s">'
            f'<text x="{LABEL_X}" y="{y}" fill="#58a6ff" font-size="11">{label}</text>'
            f'<text x="{DOT_X}" y="{y}" fill="#484f58" font-size="11">{dots}</text>'
            f'<text x="{VALUE_X}" y="{y}" fill="#c9d1d9" font-size="11">{value_lines[0]}</text></g>'
        )
        y += ROW_HEIGHT
        animation_index += 1
        for continuation in value_lines[1:]:
            parts.append(f'<g class="line" style="animation-delay:{animation_index*.156:.3f}s"><text x="{VALUE_X}" y="{y}" fill="#c9d1d9" font-size="11">{continuation}</text></g>')
            y += ROW_HEIGHT
            animation_index += 1
    y += 5

parts.append(f'<line x2="{WIDTH}" y1="{HEIGHT-33}" y2="{HEIGHT-33}" stroke="#30363d"/>')
parts.append(f'<text x="{LABEL_X}" y="{HEIGHT-12}" fill="#8b949e" font-size="11">&gt; Building secure, scalable &amp; production-ready web applications.</text>')
parts.append('</svg>')
(ROOT / "info-card.svg").write_text("".join(parts), encoding="utf-8")
print("wrote info-card.svg")
