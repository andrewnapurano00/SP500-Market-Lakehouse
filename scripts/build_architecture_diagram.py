"""Generate the repository's vector architecture diagram and PNG preview."""
from pathlib import Path
from html import escape
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parents[1];W,H=1600,1020
image=Image.new('RGB',(W,H),'#f5f7fb');draw=ImageDraw.Draw(image);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">','<title id="title">S&amp;P 500 Market Lakehouse architecture</title><desc id="desc">FMP and read-only PostgreSQL exports feed local collection, governed Landing, Bronze, Silver and Gold. Validated releases update an active registry for downstream consumers.</desc>','<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#62738b"/></marker></defs>',f'<rect width="{W}" height="{H}" fill="#f5f7fb"/>']
def font(size,bold=False):
 for p in [Path('C:/Windows/Fonts')/('segoeuib.ttf' if bold else 'segoeui.ttf'),Path('/usr/share/fonts/truetype/dejavu')/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')]:
  if p.exists():return ImageFont.truetype(str(p),size)
 return ImageFont.load_default()
def text(x,y,t,size=20,color='#162b45',bold=False):
 draw.text((x,y),t,font=font(size,bold),fill=color)
 svg.append(f'<text x="{x}" y="{y+size}" font-family="Segoe UI,Arial,sans-serif" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}">{escape(t)}</text>')
def box(x,y,w,h,title,lines,fill='#ffffff',stroke='#dce4ef',accent=None):
 draw.rounded_rectangle((x,y,x+w,y+h),radius=16,fill=fill,outline=stroke,width=2);svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
 if accent:draw.rounded_rectangle((x,y,x+7,y+h),radius=3,fill=accent);svg.append(f'<rect x="{x}" y="{y}" width="7" height="{h}" rx="3" fill="{accent}"/>')
 text(x+24,y+17,title,24,bold=True)
 for i,line in enumerate(lines):text(x+24,y+57+i*27,line,19,color='#475c75')
def arrow(points):
 draw.line(points,fill='#62738b',width=3,joint='curve');x,y=points[-1];px,py=points[-2]
 if y>py:tip=[(x,y),(x-6,y-11),(x+6,y-11)]
 elif x>px:tip=[(x,y),(x-11,y-6),(x-11,y+6)]
 else:tip=[(x,y),(x-6,y+11),(x+6,y+11)]
 draw.polygon(tip,fill='#62738b');svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+'" fill="none" stroke="#62738b" stroke-width="3" marker-end="url(#arrow)"/>')
text(40,27,'S&P 500 Market Lakehouse',40,bold=True)
text(42,80,'Source evidence. Canonical identities. Reproducible analytics datasets.',22,color='#526780')
# Cloud boundary, behind all cloud nodes.
draw.rounded_rectangle((815,130,1560,857),radius=22,fill='#eaf1fb',outline='#c9d8ed',width=2);svg.append('<rect x="815" y="130" width="745" height="727" rx="22" fill="#eaf1fb" stroke="#c9d8ed" stroke-width="2"/>')
text(842,143,'DATABRICKS  /  UNITY CATALOG',18,color='#365d91',bold=True)
box(40,153,320,178,'Financial Modeling Prep',['Prices & financial statements','Profiles & membership','Sector, macro, VIX, Treasury'],accent='#176c78')
box(40,363,320,133,'Historical PostgreSQL',['Schema-only recovery DDL','Consistent read-only export'],accent='#4a6ea8')
box(420,153,345,343,'Local collection & export',['Python API clients / SQLAlchemy','Explicit dates and request budgets','Raw wrappers + normalized rows','Stable-security route preflight','SHA256 manifests & checkpoints','No trained models or trading'],accent='#176c78')
arrow([(360,238),(420,238)]);arrow([(360,429),(420,429)]);arrow([(765,240),(844,240)])
box(845,190,685,107,'Landing Volumes',['Immutable JSONL / Parquet + committed capture manifests'],accent='#5078ad')
arrow([(1187,297),(1187,324)])
box(845,326,685,107,'Bronze | source evidence',['Raw responses, source revisions and tagged PG reconstruction'],fill='#fff4e9',stroke='#eacbab',accent='#b97533')
arrow([(1187,433),(1187,460)])
box(845,462,685,107,'Silver | canonical data',['Security & membership bridges, typed facts, feature families'],fill='#f1f4f8',stroke='#c5d0dd',accent='#73849a')
arrow([(1187,569),(1187,596)])
box(845,598,685,107,'Gold | versioned monthly datasets',['Ordered predictors / full membership cohort / separate outcomes'],fill='#fff9e5',stroke='#e9d48a',accent='#b58c19')
arrow([(1187,705),(1187,733)])
box(845,735,685,101,'Validated active-dataset registry',['Pinned Delta versions + expected-parent activation'],fill='#e6f4ed',stroke='#a7d2bc',accent='#287953')
box(40,535,725,193,'Release controls & lineage',['Capture commits, source hashes and quality/read-back checks','Known-return anchoring; unknown outcomes remain NULL','Immutable release history, rollback and quarantine controls','Failed candidates keep the previous healthy release active'],accent='#287953')
arrow([(765,633),(800,633),(800,785),(845,785)])
box(40,764,725,164,'Operational orchestration',['Local runner + parameterized Databricks Jobs','Resumable runs / content-addressed wheels and checkpoints','Optional weekday schedule: machine on and user signed in'],accent='#5078ad')
arrow([(1187,836),(1187,892)])
box(845,894,685,91,'Downstream consumers | outside this repository',['EDA, training, inference and applications read pinned Gold'],fill='#ffffff',stroke='#c5d0dd')
text(42,972,'Repository scope: database creation + ingestion + transformation + dataset contracts.',18,color='#526780')
svg.append('</svg>');assets=D/'docs/assets';assets.mkdir(parents=True,exist_ok=True);(assets/'architecture.svg').write_text('\n'.join(svg),encoding='utf8');image.save(assets/'architecture.png')
print('Architecture SVG and PNG written.')
