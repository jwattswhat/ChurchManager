"""Generate the ChurchDBTest relationship reference from live metadata."""

from __future__ import annotations

import html
import json
from pathlib import Path
import sys

import mariadb

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from churchmanager_mode import resolve_database


OUTPUT = Path(__file__).with_name("ChurchDB-table-connections.html")


def query_rows(connection, sql):
    """Return all rows for one read-only metadata query."""
    cursor = connection.cursor()
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        cursor.close()


def load_schema():
    """Read the guarded local test schema and return browser-ready metadata."""
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    production = config["database_settings"]
    settings = resolve_database(
        {
            "server": production["host"],
            "database": production["database"],
            "user": production["user"],
            "password": None,
            "test_mode": True,
            "jsform_database": None,
        },
        config,
    )
    if settings["database"].casefold() == "churchdb" or "test" not in settings["database"].casefold():
        raise RuntimeError("Safety stop: documentation generation requires a test database.")
    connection = mariadb.connect(
        host=settings["server"],
        port=settings["port"],
        database=settings["database"],
        user=settings["user"],
        password=settings["password"],
        connect_timeout=5,
    )
    try:
        tables = query_rows(connection, """
            SELECT t.TABLE_NAME,t.TABLE_TYPE,COALESCE(t.TABLE_ROWS,0),
                   COALESCE(t.TABLE_COMMENT,'')
            FROM information_schema.TABLES t
            WHERE t.TABLE_SCHEMA=DATABASE()
            ORDER BY t.TABLE_TYPE,t.TABLE_NAME
        """)
        columns = query_rows(connection, """
            SELECT c.TABLE_NAME,c.COLUMN_NAME,c.COLUMN_TYPE,c.IS_NULLABLE,c.COLUMN_KEY,
                   COALESCE(c.EXTRA,''),COALESCE(c.COLUMN_DEFAULT,'')
            FROM information_schema.COLUMNS c
            WHERE c.TABLE_SCHEMA=DATABASE()
            ORDER BY c.TABLE_NAME,c.ORDINAL_POSITION
        """)
        foreign_keys = query_rows(connection, """
            SELECT k.CONSTRAINT_NAME,k.TABLE_NAME,k.COLUMN_NAME,
                   k.REFERENCED_TABLE_NAME,k.REFERENCED_COLUMN_NAME,
                   r.UPDATE_RULE,r.DELETE_RULE
            FROM information_schema.KEY_COLUMN_USAGE k
            JOIN information_schema.REFERENTIAL_CONSTRAINTS r
              ON r.CONSTRAINT_SCHEMA=k.CONSTRAINT_SCHEMA
             AND r.CONSTRAINT_NAME=k.CONSTRAINT_NAME
            WHERE k.TABLE_SCHEMA=DATABASE() AND k.REFERENCED_TABLE_NAME IS NOT NULL
            ORDER BY k.TABLE_NAME,k.CONSTRAINT_NAME,k.ORDINAL_POSITION
        """)
        indexes = query_rows(connection, """
            SELECT TABLE_NAME,INDEX_NAME,NON_UNIQUE,GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX)
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA=DATABASE()
            GROUP BY TABLE_NAME,INDEX_NAME,NON_UNIQUE
            ORDER BY TABLE_NAME,INDEX_NAME
        """)
        migrations = query_rows(connection, "SELECT version FROM schema_migrations ORDER BY applied_at,version")
    finally:
        connection.close()

    by_table = {name: {"name": name, "type": kind, "rows": int(rows), "comment": str(comment),
                       "columns": [], "indexes": []} for name, kind, rows, comment in tables}
    for table, name, kind, nullable, key, extra, default in columns:
        by_table[table]["columns"].append({"name": name, "type": kind, "nullable": nullable == "YES",
                                            "key": key, "extra": extra, "default": str(default)})
    for table, name, non_unique, names in indexes:
        by_table[table]["indexes"].append({"name": name, "unique": not bool(non_unique), "columns": names})
    links = [{"name": name, "from": table, "column": column, "to": target,
              "targetColumn": target_column, "update": update, "delete": delete}
             for name, table, column, target, target_column, update, delete in foreign_keys]
    return {
        "database": settings["database"],
        "tables": list(by_table.values()),
        "links": links,
        "migration": migrations[-1][0] if migrations else "none",
        "migrationCount": len(migrations),
    }


def render(data):
    """Render a self-contained interactive HTML schema reference."""
    payload = json.dumps(data, ensure_ascii=True, separators=(",", ":")).replace("</", "<\\/")
    title = html.escape(f"{data['database']} Table Connections")
    return f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>{title}</title>
<style>
:root{{--bg:#f5f7fb;--panel:#fff;--ink:#172033;--muted:#667085;--line:#d8deea;--accent:#2457d6;--accent2:#e8efff;--view:#7a3eaa}}
@media(prefers-color-scheme:dark){{:root{{--bg:#111827;--panel:#1f2937;--ink:#f3f4f6;--muted:#aab3c2;--line:#3b4658;--accent:#8ab4ff;--accent2:#24395e;--view:#d2a8ff}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.4 system-ui,Segoe UI,sans-serif}}
header{{padding:20px 24px 12px}}h1{{font-size:24px;margin:0 0 4px}}.sub{{color:var(--muted)}}
.stats,.toolbar{{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}}.pill{{background:var(--panel);border:1px solid var(--line);border-radius:999px;padding:6px 10px}}
.toolbar{{position:sticky;top:0;background:var(--bg);padding:10px 24px;z-index:5;border-bottom:1px solid var(--line)}}
input,select,button{{font:inherit;color:inherit;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:8px 10px}}input{{min-width:260px;flex:1}}button{{cursor:pointer}}button.active{{background:var(--accent);color:var(--panel)}}
main{{display:grid;grid-template-columns:minmax(0,1.8fr) minmax(320px,1fr);gap:14px;padding:14px 24px 24px}}.panel{{background:var(--panel);border:1px solid var(--line);border-radius:12px;min-width:0}}
#map{{width:100%;height:720px;display:block}}.edge{{stroke:var(--line);stroke-width:1.2}}.edge.on{{stroke:var(--accent);stroke-width:2.4}}.node circle{{fill:var(--panel);stroke:var(--accent);stroke-width:1.5}}.node.view circle{{stroke:var(--view)}}.node.dim{{opacity:.14}}.node text{{fill:var(--ink);font-size:11px;pointer-events:none}}.node{{cursor:pointer}}
#detail{{padding:16px;max-height:720px;overflow:auto}}#detail h2{{font-size:18px;margin:0 0 4px}}#detail h3{{font-size:14px;margin:18px 0 6px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:6px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{color:var(--muted);font-weight:600}}code{{font:12px ui-monospace,Consolas,monospace}}.muted{{color:var(--muted)}}.fk{{color:var(--accent)}}
@media(max-width:850px){{main{{grid-template-columns:1fr}}#map{{height:560px}}#detail{{max-height:none}}}}
</style></head><body>
<header><h1>{title}</h1><div class=\"sub\">Live metadata snapshot from the guarded local test database. Select a table or view to inspect its fields and direct relationships.</div>
<div class=\"stats\"><span class=\"pill\" id=\"tableStat\"></span><span class=\"pill\" id=\"viewStat\"></span><span class=\"pill\" id=\"fkStat\"></span><span class=\"pill\">Latest migration: <code>{html.escape(data['migration'])}</code></span></div></header>
<div class=\"toolbar\"><input id=\"search\" type=\"search\" placeholder=\"Find a table, view, or column\" aria-label=\"Find a table, view, or column\"><select id=\"kind\" aria-label=\"Object type\"><option value=\"all\">Tables and views</option><option value=\"BASE TABLE\">Tables only</option><option value=\"VIEW\">Views only</option></select><button id=\"reset\">Reset selection</button></div>
<main><section class=\"panel\"><svg id=\"map\" role=\"img\" aria-label=\"Database table relationship diagram\"><g id=\"viewport\"><g id=\"edges\"></g><g id=\"nodes\"></g></g></svg></section><aside class=\"panel\" id=\"detail\"><h2>Choose a table</h2><p class=\"muted\">The map shows declared foreign-key connections. Views are shown with a purple outline.</p></aside></main>
<script id=\"schema-data\" type=\"application/json\">{payload}</script><script>
const data=JSON.parse(document.getElementById('schema-data').textContent), ns='http://www.w3.org/2000/svg';
const svg=document.getElementById('map'), vp=document.getElementById('viewport'), edgeLayer=document.getElementById('edges'), nodeLayer=document.getElementById('nodes'), detail=document.getElementById('detail');
const objects=data.tables, byName=new Map(objects.map(x=>[x.name,x]));
document.getElementById('tableStat').textContent=`${{objects.filter(x=>x.type==='BASE TABLE').length}} tables`;
document.getElementById('viewStat').textContent=`${{objects.filter(x=>x.type==='VIEW').length}} views`;
document.getElementById('fkStat').textContent=`${{data.links.length}} foreign-key columns`;
let selected=null, scale=1, tx=0, ty=0, dragging=false, px=0, py=0;
function layout(){{const w=1040,h=720,cx=w/2,cy=h/2, rings=[[],[],[]];objects.forEach(o=>{{const d=data.links.filter(l=>l.from===o.name||l.to===o.name).length;rings[d>4?0:d?1:2].push(o)}});rings.forEach((ring,ri)=>{{const radius=[175,300,420][ri];ring.forEach((o,i)=>{{const a=2*Math.PI*i/ring.length-(Math.PI/2);o.x=cx+Math.cos(a)*radius;o.y=cy+Math.sin(a)*radius}})}});svg.setAttribute('viewBox','0 0 1040 720')}}
function draw(){{layout();data.links.forEach((l,i)=>{{const a=byName.get(l.from),b=byName.get(l.to),e=document.createElementNS(ns,'line');e.setAttribute('x1',a.x);e.setAttribute('y1',a.y);e.setAttribute('x2',b.x);e.setAttribute('y2',b.y);e.classList.add('edge');e.dataset.i=i;edgeLayer.append(e)}});objects.forEach(o=>{{const g=document.createElementNS(ns,'g');g.classList.add('node');if(o.type==='VIEW')g.classList.add('view');g.setAttribute('transform',`translate(${{o.x}} ${{o.y}})`);g.dataset.name=o.name;const c=document.createElementNS(ns,'circle');c.setAttribute('r',o.type==='VIEW'?7:9);const t=document.createElementNS(ns,'text');t.setAttribute('x',12);t.setAttribute('y',4);t.textContent=o.name;g.append(c,t);g.addEventListener('click',()=>select(o.name));nodeLayer.append(g)}})}}
function esc(s){{return String(s??'').replace(/[&<>\"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}}[c]))}}
function select(name){{selected=name;const o=byName.get(name),links=data.links.filter(l=>l.from===name||l.to===name),related=new Set([name]);links.forEach(l=>{{related.add(l.from);related.add(l.to)}});document.querySelectorAll('.node').forEach(n=>n.classList.toggle('dim',!related.has(n.dataset.name)));document.querySelectorAll('.edge').forEach(e=>e.classList.toggle('on',data.links[e.dataset.i].from===name||data.links[e.dataset.i].to===name));detail.innerHTML=`<h2>${{esc(o.name)}}</h2><div class=\"muted\">${{esc(o.type==='VIEW'?'View':`${{o.rows}} estimated rows`)}} · ${{o.columns.length}} columns · ${{o.indexes.length}} indexes</div><h3>Direct relationships (${{links.length}})</h3>${{links.length?`<table><thead><tr><th>Field</th><th>Connected to</th><th>Rules</th></tr></thead><tbody>${{links.map(l=>{{const outbound=l.from===name;return `<tr><td><code>${{esc(outbound?l.column:l.targetColumn)}}</code></td><td class=\"fk\"><code>${{esc(outbound?l.to:l.from)}}.${{esc(outbound?l.targetColumn:l.column)}}</code></td><td><code>U:${{esc(l.update)}} D:${{esc(l.delete)}}</code></td></tr>`}}).join('')}}</tbody></table>`:'<p class=\"muted\">No declared foreign keys.</p>'}}<h3>Columns</h3><table><thead><tr><th>Name</th><th>Type</th><th>Flags</th></tr></thead><tbody>${{o.columns.map(c=>`<tr><td><code>${{esc(c.name)}}</code></td><td><code>${{esc(c.type)}}</code></td><td>${{esc([c.key,c.nullable?'nullable':'required',c.extra].filter(Boolean).join(', '))}}</td></tr>`).join('')}}</tbody></table><h3>Indexes</h3>${{o.indexes.length?`<table><tbody>${{o.indexes.map(i=>`<tr><td><code>${{esc(i.name)}}</code></td><td>${{i.unique?'unique':'non-unique'}}</td><td><code>${{esc(i.columns)}}</code></td></tr>`).join('')}}</tbody></table>`:'<p class=\"muted\">No indexes reported.</p>'}}`}}
function filter(){{const q=document.getElementById('search').value.trim().toLowerCase(),kind=document.getElementById('kind').value;document.querySelectorAll('.node').forEach(n=>{{const o=byName.get(n.dataset.name),hit=!q||o.name.toLowerCase().includes(q)||o.columns.some(c=>c.name.toLowerCase().includes(q));n.style.display=(hit&&(kind==='all'||o.type===kind))?'':'none'}})}}
document.getElementById('search').addEventListener('input',filter);document.getElementById('kind').addEventListener('change',filter);document.getElementById('reset').addEventListener('click',()=>{{selected=null;document.querySelectorAll('.node').forEach(n=>n.classList.remove('dim'));document.querySelectorAll('.edge').forEach(e=>e.classList.remove('on'));detail.innerHTML='<h2>Choose a table</h2><p class=\"muted\">The map shows declared foreign-key connections. Views are shown with a purple outline.</p>'}});
svg.addEventListener('wheel',e=>{{e.preventDefault();scale=Math.max(.45,Math.min(3,scale*(e.deltaY<0?1.1:.9)));vp.setAttribute('transform',`translate(${{tx}} ${{ty}}) scale(${{scale}})`) }},{{passive:false}});svg.addEventListener('pointerdown',e=>{{dragging=true;px=e.clientX;py=e.clientY;svg.setPointerCapture(e.pointerId)}});svg.addEventListener('pointermove',e=>{{if(!dragging)return;tx+=e.clientX-px;ty+=e.clientY-py;px=e.clientX;py=e.clientY;vp.setAttribute('transform',`translate(${{tx}} ${{ty}}) scale(${{scale}})`)}});svg.addEventListener('pointerup',()=>dragging=false);
draw();
</script></body></html>"""


if __name__ == "__main__":
    schema = load_schema()
    OUTPUT.write_text(render(schema), encoding="utf-8")
    print(f"Updated {OUTPUT} with {len(schema['tables'])} objects and {len(schema['links'])} foreign-key columns.")
