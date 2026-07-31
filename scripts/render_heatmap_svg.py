from pathlib import Path
import datetime as dt, json
ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT/'data'/'contributions.json').read_text(encoding='utf-8'))
days = {d['date']:d for d in data['days']}
end = dt.date.fromisoformat(data['range']['end'])
start = end - dt.timedelta(days=370)
start -= dt.timedelta(days=(start.weekday()+1)%7)
cell, gap, left, top = 11, 3, 42, 45
cols, rows = 53, 7
w, h = left+cols*(cell+gap)+22, top+rows*(cell+gap)+94
palette=['#21262d','#0e4429','#006d32','#26a641','#39d353']
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{data["username"]} contribution graph</title><desc id="desc">Animated 53-week GitHub-style contribution heatmap with real public activity data.</desc><style>.c{{opacity:0;animation:appear .25s ease-out forwards}}@keyframes appear{{to{{opacity:1}}}}text{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}}</style>',f'<rect width="{w}" height="{h}" rx="12" fill="#0d1117"/><rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="none" stroke="#30363d"/><text x="20" y="25" fill="#c9d1d9" font-size="13">{data["total_contributions"]:,} contributions in the last year</text>']
seen=set()
for col in range(cols):
    d=start+dt.timedelta(days=col*7)
    if d.month not in seen:
        seen.add(d.month); svg.append(f'<text x="{left+col*(cell+gap)}" y="40" fill="#8b949e" font-size="9">{d.strftime("%b")}</text>')
for row,label in [(1,'Mon'),(3,'Wed'),(5,'Fri')]: svg.append(f'<text x="9" y="{top+row*(cell+gap)+9}" fill="#8b949e" font-size="9">{label}</text>')
for col in range(cols):
  for row in range(rows):
    day=start+dt.timedelta(days=col*7+row); item=days.get(day.isoformat()); level=item['level'] if item else 0; count=item['count'] if item else 0; delay=(col*.018+row*.035)
    svg.append(f'<rect class="c" x="{left+col*(cell+gap)}" y="{top+row*(cell+gap)}" width="{cell}" height="{cell}" rx="2" fill="{palette[level]}" style="animation-delay:{delay:.3f}s"><title>{day}: {count} contribution(s)</title></rect>')
y=top+rows*(cell+gap)+20
svg.append(f'<text x="20" y="{y}" fill="#8b949e" font-size="11">Current streak <tspan fill="#58a6ff">{data["current_streak"]["length"]} days</tspan>   ·   Longest <tspan fill="#58a6ff">{data["longest_streak"]["length"]} days</tspan></text>')
svg.append(f'<text x="20" y="{y+24}" fill="#8b949e" font-size="10">Less</text>')
for i,color in enumerate(palette): svg.append(f'<rect x="{48+i*14}" y="{y+14}" width="11" height="11" rx="2" fill="{color}"/>')
svg.append(f'<text x="{120}" y="{y+24}" fill="#8b949e" font-size="10">More · best day {data["best_day"]["count"]} on {data["best_day"]["date"]}</text></svg>')
(ROOT/'contrib-heatmap.svg').write_text(''.join(svg),encoding='utf-8')
print('wrote contrib-heatmap.svg')
