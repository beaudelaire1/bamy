
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
XEROS PROJECT – AUDIT SCRIPT (file + app + arborescence)
Usage:
    python audit_xeros.py  [--root .]
Outputs:
    audit_report.md  (résultats lisibles)
    audit_findings.txt (liste brute d'observations)
Notes:
    - Exécuter depuis la racine du projet (celle qui contient manage.py).
    - Aucune dépendance externe ; analyse statique (ne lance pas Django).
"""
import os, re, sys, argparse, json, ast
from pathlib import Path
from datetime import datetime

IGNORES = {'.git', '.idea', '.vscode', '__pycache__', 'node_modules', 'venv', '.venv', 'env', '.mypy_cache', '.ruff_cache'}
IGNORE_FILE_EXTS = {'.pyc', '.pyo', '.DS_Store'}

KEYWORDS = [
    # Panier / Checkout
    r'\bclass\s+Cart\b', r'\bCART_SESSION_ID\b', r'\bdef\s+add\(', r'checkout_success',
    # Paiements
    r'STRIPE_SECRET_KEY', r'PAYPAL_CLIENT_ID', r'PAYPAL_SECRET',
    # URLs
    r"name=['\"]add['\"]", r"name=['\"][^'\"]*cart_add['\"]",
]

SETTINGS_NAMES = [
    'DEBUG', 'ALLOWED_HOSTS', 'INSTALLED_APPS', 'DATABASES', 'CACHES',
    'STATIC_URL', 'STATIC_ROOT', 'MEDIA_URL', 'MEDIA_ROOT', 'CSRF_TRUSTED_ORIGINS',
    'SECURE_HSTS_SECONDS', 'SECURE_SSL_REDIRECT', 'SESSION_COOKIE_SECURE', 'CSRF_COOKIE_SECURE',
    'DEFAULT_FILE_STORAGE', 'STORAGES',
]

def find_project_root(root: Path) -> Path:
    # Heuristic: folder containing manage.py
    candidates = [root] + [p for p in root.iterdir() if p.is_dir()]
    for c in candidates:
        if (c / 'manage.py').exists():
            return c
    return root

def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORES and not d.startswith('.')]
        for f in sorted(filenames):
            ext = os.path.splitext(f)[1]
            if ext in IGNORE_FILE_EXTS:
                continue
            yield Path(dirpath) / f

def is_code_file(p: Path) -> bool:
    return p.suffix in {'.py', '.html', '.txt', '.md', '.json', '.yml', '.yaml', '.css', '.js'}

def relative(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except Exception:
        return str(p)

def draw_tree(root: Path):
    # Simple flat tree with indentation based on relative parts
    lines = []
    for p in sorted([p for p in iter_files(root) if is_code_file(p)], key=lambda x: relative(x, root)):
        rel = relative(p, root)
        parts = rel.split(os.sep)
        indent = "    " * (len(parts) - 1)
        glyph = "└── " if parts else ""
        lines.append(f"{indent}{glyph}{parts[-1]}")
    return "\n".join(lines)

def grep_patterns(root: Path, patterns):
    compiled = [(pat, re.compile(pat)) for pat in patterns]
    matches = {pat: [] for pat in patterns}
    for p in iter_files(root):
        if not is_code_file(p):
            continue
        try:
            text = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        for pat, rx in compiled:
            for m in rx.finditer(text):
                # Keep surrounding context small
                start = max(0, m.start() - 40)
                end = min(len(text), m.end() + 40)
                snippet = text[start:end].replace("\n", " ")
                matches[pat].append((relative(p, root), m.start(), snippet))
    return matches

def analyse_settings(root: Path):
    # Best-effort: find settings.py or settings/ dir
    candidates = []
    for p in iter_files(root):
        if p.name == 'settings.py' or (p.parent.name == 'settings' and p.suffix == '.py'):
            candidates.append(p)
    summary = []
    for p in candidates:
        try:
            src = p.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(src)
            values = {}
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id in SETTINGS_NAMES:
                            try:
                                values[target.id] = ast.literal_eval(node.value)
                            except Exception:
                                # Fallback: raw source slice
                                values[target.id] = "<dynamic or complex>"
            summary.append({
                "file": str(p),
                "values": {k: values.get(k, "<not set>") for k in SETTINGS_NAMES}
            })
        except Exception as e:
            summary.append({"file": str(p), "error": str(e)})
    return summary

def analyse_urls(root: Path):
    # List named url patterns by inspecting urls.py files (static regex; not executing Django)
    url_entries = []
    rx = re.compile(r'path\(\s*["\'][^"\']+["\']\s*,\s*[^,]+,\s*name=["\']([^"\']+)["\']')
    for p in iter_files(root):
        if p.name == 'urls.py':
            try:
                text = p.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            names = rx.findall(text)
            app_name = None
            m = re.search(r"app_name\s*=\s*['\"]([^'\"]+)['\"]", text)
            if m:
                app_name = m.group(1)
            url_entries.append({
                "file": str(p),
                "app_name": app_name or "<none>",
                "named_routes": sorted(set(names))
            })
    return url_entries

def quick_findings(keyword_hits, url_entries):
    findings = []
    # Multiple Cart classes?
    cart_hits = keyword_hits.get(r'\bclass\s+Cart\b', [])
    if len(cart_hits) > 1:
        findings.append(f"PLUSIEURS classes Cart détectées ({len(cart_hits)}). Risque de divergence panier/checkout.")
        for f, pos, snip in cart_hits:
            findings.append(f"  - {f}")
    elif len(cart_hits) == 1:
        findings.append(f"Une seule classe Cart détectée ({cart_hits[0][0]}). OK a priori.")

    # add() signature present?
    add_hits = keyword_hits.get(r'\bdef\s+add\(', [])
    if len(add_hits) == 0:
        findings.append("Aucune méthode add(...) trouvée. Vérifier la classe Cart et les vues cart.add.")
    else:
        findings.append(f"Méthodes add(...) trouvées: {len(add_hits)} occurrence(s).")

    # checkout_success route present?
    success_hits = keyword_hits.get('checkout_success', [])
    if len(success_hits) == 0:
        findings.append("Route/Template 'checkout_success' non détectée. À ajouter.")
    else:
        findings.append("Référence 'checkout_success' détectée (vérifier route + template).")

    # Stripe vs PayPal
    if keyword_hits.get('STRIPE_SECRET_KEY', []):
        findings.append("Utilisation de STRIPE_SECRET_KEY détectée. Si PayPal est prioritaire, isoler Stripe derrière un flag.")
    if not keyword_hits.get('PAYPAL_CLIENT_ID', []) and not keyword_hits.get('PAYPAL_SECRET', []):
        findings.append("Aucune variable PayPal détectée. Prévoir PAYPAL_CLIENT_ID / PAYPAL_SECRET dans .env et settings.")

    # URL names
    has_cart_add = any('cart_add' in entry['named_routes'] for entry in url_entries)
    has_add = any('add' in entry['named_routes'] for entry in url_entries)
    if has_add and not has_cart_add:
        findings.append("Des routes nommées 'add' existent sans prefix explicite (ex: 'cart_add'). Risque de NoReverseMatch.")
    elif has_cart_add:
        findings.append("Route nommée 'cart_add' détectée. OK pour reverse('cart:cart_add').")

    return findings

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Racine du projet (contenant manage.py)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    root = find_project_root(root)

    out_md = root / "audit_report.md"
    out_txt = root / "audit_findings.txt"

    # Tree
    tree = draw_tree(root)

    # Grep
    keyword_hits = grep_patterns(root, KEYWORDS)

    # Settings
    settings_summary = analyse_settings(root)

    # URLs
    url_entries = analyse_urls(root)

    # Findings
    findings = quick_findings(keyword_hits, url_entries)

    # Write Markdown report
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    def codeblock(text, lang=""):
        return f"```{lang}\n{text}\n```"

    md = []
    md.append(f"# Xeros – Audit Projet (généré le {now})")
    md.append("## 1) Arborescence (fichiers principaux)")
    md.append(codeblock(tree, ""))

    md.append("## 2) Résultats de recherche (mots-clés)")
    for pat, hits in keyword_hits.items():
        md.append(f"### Mot-clé: `{pat}` – {len(hits)} occurrence(s)")
        for f, pos, snip in hits[:50]:  # cap to 50 lines
            md.append(f"- **{f}** @ {pos}: `{snip}`")

    md.append("## 3) URLs nommées détectées")
    for entry in url_entries:
        md.append(f"- **{entry['file']}** (app_name: `{entry['app_name']}`)")
        if entry['named_routes']:
            for name in entry['named_routes']:
                md.append(f"  - `{name}`")
        else:
            md.append("  - (aucune route nommée détectée)")

    md.append("## 4) Settings (analyse statique)")
    for item in settings_summary:
        md.append(f"### {item.get('file')}")
        if 'error' in item:
            md.append(f"- Erreur lecture: {item['error']}")
        else:
            vals = item.get('values', {})
            for k in SETTINGS_NAMES:
                v = vals.get(k, "<not set>")
                # Hide secrets if any
                if isinstance(v, str) and ('SECRET' in k or 'PASSWORD' in k):
                    v = "<hidden>"
                md.append(f"- **{k}**: `{v}`")

    md.append("## 5) Observations rapides")
    for f in findings:
        md.append(f"- {f}")

    out_md.write_text("\n".join(md), encoding="utf-8")

    out_txt.write_text("\n".join(findings), encoding="utf-8")

    print(f"[OK] Rapport écrit: {out_md}")
    print(f"[OK] Observations: {out_txt}")
    print("Étapes suivantes:")
    print("  1) Ouvrir audit_report.md et poster ici les sections 3) URLs et 5) Observations.")
    print("  2) On corrige ensemble Cart/URLs/checkout selon ces résultats.")
    print("  3) On enchaîne sur settings & déploiement.")

if __name__ == "__main__":
    main()
