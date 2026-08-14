from __future__ import annotations

from html import escape


def render_report(solution: dict) -> str:
    app = solution["application"]
    rec = solution["recommended"] or {"name": "No compatible meter", "score": 0, "why": "Engineering review required."}
    excluded = "".join(f"<li><strong>{escape(item['product'])}</strong>: {escape('; '.join(item['reasons']))}</li>" for item in solution["excluded"])
    path = " -> ".join(solution["architecture"]["path"])
    return f"""<!doctype html>
<html><head><meta charset='utf-8'><title>MeterSpec Report</title>
<style>body{{font-family:Arial,sans-serif;margin:32px;color:#17201b}} h1,h2{{color:#173c43}} table{{border-collapse:collapse;width:100%}} td,th{{border:1px solid #ccd6d0;padding:8px;text-align:left}} .status{{font-weight:700}}</style></head>
<body>
<h1>MeterSpec Electrical Meter Selection & Sizing Report</h1>
<p class='status'>Application Status: {escape(solution['status'])}</p>
<h2>Application</h2><table>
<tr><th>Name</th><td>{escape(app['application_name'])}</td></tr>
<tr><th>System</th><td>{escape(app['system'])} / {escape(app['wiring'])} / {app['nominal_voltage']} V</td></tr>
<tr><th>Maximum Current</th><td>{app['maximum_current']} A</td></tr>
<tr><th>Protocol</th><td>{escape(app['protocol'])}</td></tr>
</table>
<h2>CT Assessment</h2><p>{escape(solution['ct']['recommended_ratio'])}, utilization {solution['ct']['utilization']}%, margin {solution['ct']['margin_amps']} A. {escape(solution['ct']['reason'])}</p>
<h2>PT Assessment</h2><p>{escape(solution['pt']['status'])}: {escape(solution['pt']['reason'])}</p>
<h2>Recommended Meter Specification</h2><p><strong>{escape(rec['name'])}</strong> ({rec['score']}/100). {escape(rec['why'])}</p>
<h2>Communication Architecture</h2><p>{escape(path)}</p><p>{escape(solution['architecture']['notes'])}</p>
<h2>Excluded Products</h2><ul>{excluded}</ul>
<h2>Clarifications</h2><ul>{''.join('<li>'+escape(q)+'</li>' for q in solution['open_questions']) or '<li>None for this demo scenario.</li>'}</ul>
<h2>Disclaimer</h2><p>This report uses a fictional demonstration product catalog and must be validated against actual manufacturer documentation before procurement or installation.</p>
</body></html>"""
