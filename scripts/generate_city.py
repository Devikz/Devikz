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
    weeks=cal["weeks"]
    W,H=1200,440
    s=18; dy=5.3
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="440" viewBox="0 0 1200 440" role="img" aria-label="Isometric GitHub contribution city">','<rect width="1200" height="440" fill="#050706"/>','<text x="35" y="38" font-family="Georgia,serif" font-size="24" fill="#e0c36e">The City of Contributions</text>']
    parts.append(f'<text x="35" y="63" font-family="monospace" font-size="13" fill="#8fc6ad">{cal["totalContributions"]:,} contributions in the past year</text>')
    def poly(points,color):
        return '<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in points)+'" fill="'+color+'" stroke="#050706" stroke-width=".65"/>'
    cells=[]
    for w,week in enumerate(weeks):
        for day in week["contributionDays"]:
            d=(datetime.date.fromisoformat(day["date"]).weekday()+1)%7
            cells.append((w,d,day))
    for w,d,day in sorted(cells,key=lambda c:c[0]+c[1]):
        n=day["contributionCount"]
        x=150+(w-d)*s; y=110+(w+d)*dy
        a=8.6;b=4.6;h=1.5 if not n else min(104,10+18*math.log1p(n))
        top="#11251e" if not n else "#c9a34a" if n>=15 else "#15966c" if n>=5 else "#0f6b50"
        left="#0b2119" if not n else "#856728" if n>=15 else "#0b3d2e"
        right="#08120e" if not n else "#4d391a" if n>=15 else "#08291e"
        parts.append(f'<g><title>{escape(day["date"])}: {n} contributions</title>')
        parts.append(poly([(x-a,y-h),(x,y+b-h),(x,y+b),(x-a,y)],left))
        parts.append(poly([(x,y+b-h),(x+a,y-h),(x+a,y),(x,y+b)],right))
        parts.append(poly([(x-a,y-h),(x,y-b-h),(x+a,y-h),(x,y+b-h)],top))
        if n>=5:
            parts.append(f'<circle cx="{x-3}" cy="{y-h+9}" r="1.2" fill="#e0c36e"><animate attributeName="opacity" values=".15;1;.15" dur="{3+(w+d)%4}s" begin="-{(w+d)%4}s" repeatCount="indefinite"/></circle>')
        parts.append('</g>')
    parts.append('<text x="35" y="420" font-family="monospace" font-size="12" fill="#8fc6ad">One building per day · Height represents contribution count · Gold: 15+</text></svg>')
    return "".join(parts)

if __name__=="__main__":
    output=Path("assets/contribution-city.svg")
    output.parent.mkdir(exist_ok=True)
    output.write_text(render(calendar()),encoding="utf-8")
