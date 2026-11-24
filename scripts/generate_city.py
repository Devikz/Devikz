"""Generate an animated isometric SVG from GitHub's contribution calendar."""
import os, json, urllib.request, datetime, math
from pathlib import Path
from html import escape

def calendar():
    query = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""
    req=urllib.request.Request("https://api.github.com/graphql",data=json.dumps({"query":query,"variables":{"login":"Devikz"}}).encode(),headers={"Authorization":"Bearer "+os.environ["GH_TOKEN"],"Content-Type":"application/json","User-Agent":"Devikz-contribution-city"})
    with urllib.request.urlopen(req,timeout=40) as response:
        data=json.load(response)
    if data.get("errors"): raise RuntimeError(str(data["errors"]))
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]

def render(cal):
    days=sorted((day for week in cal["weeks"] for day in week["contributionDays"]),key=lambda d:d["date"])
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600" viewBox="0 0 1200 600" role="img" aria-label="Isometric GitHub contribution city">','<rect width="1200" height="600" fill="#050706"/>']
    # Deterministic cosmic background; stars are decorative, not contribution data.
    for i in range(155):
        x=(i*137.51)%1200; y=(i*89.37)%600
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.1 if i%13==0 else .55}" fill="{"#b89a56" if i%9==0 else "#438d77" if i%7 else "#7956a8"}" opacity="{.5 if i%13==0 else .22}"/>')
    parts.append('<text x="35" y="38" font-family="Georgia,serif" font-size="24" fill="#e0c36e">The City of Contributions</text>')
    parts.append(f'<text x="35" y="63" font-family="monospace" font-size="13" fill="#8fc6ad">{cal["totalContributions"]:,} contributions in the past year</text>')
    def poly(points,color,stroke="#173b30"):
        return '<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in points)+'" fill="'+color+'" stroke="'+stroke+'" stroke-width=".6"/>'
    # A compact grid of consecutive days, 21 columns by up to 18 rows.
    cells=[(i%21,i//21,day) for i,day in enumerate(days)]
    for c,r,day in sorted(cells,key=lambda v:v[0]+v[1]):
        n=day["contributionCount"]
        x=565+(c-r)*25; y=130+(c+r)*10.8
        a=12;b=5.2;h=2 if not n else min(140,19+30*math.log1p(n))
        top="#16382b" if not n else "#e0c36e" if n>=15 else "#39b78c" if n>=5 else "#208866"
        left="#10271f" if not n else "#a17b34" if n>=15 else "#12674d"
        right="#0a1a14" if not n else "#5d451e" if n>=15 else "#093c2e"
        parts.append(f'<g><title>{escape(day["date"])}: {n} contributions</title>')
        parts.append(poly([(x-a,y-h),(x,y+b-h),(x,y+b),(x-a,y)],left))
        parts.append(poly([(x,y+b-h),(x+a,y-h),(x+a,y),(x,y+b)],right))
        parts.append(poly([(x-a,y-h),(x,y-b-h),(x+a,y-h),(x,y+b-h)],top))
        if n:
            # Windows stay inside the building facade; their glow is decorative.
            for floor in range(1,int(h//9)):
                wy=y-h+floor*9
                for wx in (x-9,x-5):
                    parts.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="2" height="3" fill="#e0c36e" opacity=".65"><animate attributeName="opacity" values=".25;.9;.25" dur="{3+(c+r+floor)%5}s" begin="-{floor%4}s" repeatCount="indefinite"/></rect>')
        parts.append('</g>')
    parts.append('<text x="35" y="575" font-family="monospace" font-size="12" fill="#8fc6ad">One building per day · Chronological rows · Height reflects activity · Gold: 15+</text></svg>')
    return "".join(parts)

if __name__=="__main__":
    output=Path("assets/contribution-city.svg")
    output.parent.mkdir(exist_ok=True)
    output.write_text(render(calendar()),encoding="utf-8")
