from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
lines = [("identity", "Afsal A Azeez"), ("role", "Full-Stack Developer"), ("location", "Kerala, India"), ("focus", "Modern web applications"), ("frontend", "Next.js · React · TypeScript"), ("backend", "Node.js · Express · REST APIs"), ("data", "PostgreSQL · MongoDB · Prisma"), ("delivery", "AWS · Vercel · Nginx")]
w, h = 560, 310
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">Afsal A Azeez developer information</title><desc id="desc">A concise terminal-style developer card.</desc><style>text{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}}.line{{opacity:0;animation:show .35s ease-out forwards}}@keyframes show{{to{{opacity:1}}}}</style>', f'<rect width="{w}" height="{h}" rx="12" fill="#0d1117"/><rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="none" stroke="#30363d"/><text x="22" y="28" fill="#8b949e" font-size="12">afsal@github: ~/info</text><line x2="{w}" y1="42" y2="42" stroke="#30363d"/>']
for i, (key, value) in enumerate(lines):
    y = 73 + i * 27
    svg.append(f'<g class="line" style="animation-delay:{i*.13:.2f}s"><text x="22" y="{y}" fill="#58a6ff" font-size="13">{key:<9}</text><text x="145" y="{y}" fill="#c9d1d9" font-size="13">{value}</text></g>')
svg.append('</svg>')
(ROOT / 'info-card.svg').write_text(''.join(svg), encoding='utf-8')
print('wrote info-card.svg')
