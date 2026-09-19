# -*- coding: utf-8 -*-
"""
Kodi Repository Generator Script.
Builds addons.xml, addons.xml.md5, and packages zip archives for the repository.
"""

import os
import sys
import shutil
import hashlib
import zipfile
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(REPO_ROOT, 'repo')
ZIPS_DIR = os.path.join(REPO_DIR, 'zips')

# Paths to source add-on folders
ADDON_SOURCES = [
    os.path.join(REPO_ROOT, 'repository.sportsurge'),
    os.path.abspath(os.path.join(REPO_ROOT, '..', 'plugin.video.sportsurge')),
]


def make_zip(source_dir, output_zip, root_folder_name):
    """Creates a zip archive containing the add-on folder."""
    if os.path.exists(output_zip):
        os.remove(output_zip)
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d != '__pycache__' and not d.startswith('.')]
            for f in files:
                if f.endswith(('.pyc', '.pyo', '.tmp', '.git', '.gitignore')):
                    continue
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, source_dir)
                archive_path = os.path.join(root_folder_name, rel_path)
                zf.write(full_path, archive_path)


def generate_repo():
    os.makedirs(ZIPS_DIR, exist_ok=True)
    addons_root = ET.Element('addons')

    for src in ADDON_SOURCES:
        if not os.path.exists(src):
            print(f"Skipping missing source: {src}")
            continue

        xml_path = os.path.join(src, 'addon.xml')
        if not os.path.exists(xml_path):
            print(f"Skipping (no addon.xml): {src}")
            continue

        tree = ET.parse(xml_path)
        addon_elem = tree.getroot()
        addon_id = addon_elem.attrib['id']
        version = addon_elem.attrib['version']

        print(f"Processing add-on: {addon_id} v{version}")
        addons_root.append(addon_elem)

        # Create target directory: repo/zips/<addon_id>/
        addon_zips_dir = os.path.join(ZIPS_DIR, addon_id)
        os.makedirs(addon_zips_dir, exist_ok=True)

        # Build zip
        zip_filename = f"{addon_id}-{version}.zip"
        target_zip = os.path.join(addon_zips_dir, zip_filename)
        make_zip(src, target_zip, addon_id)
        print(f"  Created: {target_zip} ({os.path.getsize(target_zip):,} bytes)")

        # Copy addon.xml and artwork
        for meta_file in ('addon.xml', 'icon.png', 'fanart.jpg'):
            src_file = os.path.join(src, meta_file)
            if os.path.exists(src_file):
                shutil.copy2(src_file, os.path.join(addon_zips_dir, meta_file))

        # Also copy repository and plugin zips to root for convenient direct Kodi file source installation
        if addon_id == 'repository.sportsurge':
            root_zip = os.path.join(REPO_ROOT, zip_filename)
            shutil.copy2(target_zip, root_zip)
            print(f"  Installer zip ready: {root_zip}")
        elif addon_id == 'plugin.video.sportsurge':
            root_plugin_zip = os.path.join(REPO_ROOT, zip_filename)
            shutil.copy2(target_zip, root_plugin_zip)
            print(f"  Plugin zip ready: {root_plugin_zip}")

    # Write combined addons.xml
    addons_xml_path = os.path.join(REPO_DIR, 'addons.xml')
    addons_tree = ET.ElementTree(addons_root)
    ET.indent(addons_tree, space="  ", level=0)
    addons_tree.write(addons_xml_path, encoding='utf-8', xml_declaration=True)
    print(f"\nGenerated: {addons_xml_path}")

    # Generate addons.xml.md5
    with open(addons_xml_path, 'rb') as f:
        md5_hash = hashlib.md5(f.read()).hexdigest()

    addons_md5_path = os.path.join(REPO_DIR, 'addons.xml.md5')
    with open(addons_md5_path, 'w', encoding='utf-8') as f:
        f.write(md5_hash)
    print(f"Generated: {addons_md5_path} (MD5: {md5_hash})")

    # Generate sportsurge.m3u playlist in REPO_ROOT
    try:
        plugin_lib = os.path.abspath(os.path.join(REPO_ROOT, '..', 'plugin.video.sportsurge', 'resources', 'lib'))
        if plugin_lib not in sys.path:
            sys.path.insert(0, plugin_lib)
        import iptv_server
        m3u_file = os.path.join(REPO_ROOT, 'sportsurge.m3u')
        started, srv_url = iptv_server.start_iptv_server(port=8899)
        if started:
            succ, count, err = iptv_server.export_m3u_file(m3u_file, server_url=srv_url)
            iptv_server.stop_iptv_server()
            if succ:
                print(f"Generated: {m3u_file} ({count} channels)")
    except Exception as e:
        print(f"Warning: Could not export sportsurge.m3u: {e}")

    # Generate root index.html matching Kodi HTTPDirectory.cpp regexes
    index_html_path = os.path.join(REPO_ROOT, 'index.html')
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Index of /</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #0f172a;
            color: #f8fafc;
            padding: 30px 20px;
            margin: 0;
            display: flex;
            justify-content: center;
        }
        .container {
            max-width: 820px;
            width: 100%;
            background: #1e293b;
            border-radius: 12px;
            padding: 28px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            border: 1px solid #334155;
        }
        h1 {
            margin: 0 0 8px 0;
            color: #38bdf8;
            font-size: 1.8rem;
        }
        p {
            color: #94a3b8;
            margin: 0 0 18px 0;
            line-height: 1.5;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-family: monospace, Courier, sans-serif;
            font-size: 1rem;
            margin-top: 10px;
        }
        th, td {
            padding: 10px 12px;
            text-align: left;
        }
        th {
            color: #94a3b8;
            border-bottom: 1px solid #334155;
        }
        td {
            border-bottom: 1px solid #273549;
        }
        a {
            color: #38bdf8;
            text-decoration: none;
            font-weight: 600;
        }
        a:hover {
            text-decoration: underline;
            color: #7dd3fc;
        }
        .instructions {
            background: #0f172a;
            border-left: 4px solid #38bdf8;
            padding: 16px 20px;
            border-radius: 0 8px 8px 0;
            margin-top: 24px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 0.92rem;
        }
        .instructions h3 {
            margin: 0 0 10px 0;
            color: #f8fafc;
            font-size: 1.05rem;
        }
        .instructions ol {
            margin: 0;
            padding-left: 20px;
            color: #94a3b8;
            line-height: 1.7;
        }
        .instructions code {
            background: #1e293b;
            color: #38bdf8;
            padding: 2px 7px;
            border-radius: 4px;
            font-size: 0.95em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Index of /</h1>
        <p>Official Sportsurge Kodi Add-on Repository &mdash; Compatible with Kodi 19, 20 & 21.</p>
        <table>
            <tr><th>Name</th><th style="text-align:right">Last modified</th><th style="text-align:right">Size</th></tr>
            <tr><th colspan="3"><hr style="border:0;border-top:1px solid #334155;margin:0;"></th></tr>
            <tr><td><a href="repository.sportsurge-1.0.0.zip">repository.sportsurge-1.0.0.zip</a></td><td align="right">2026-09-18 19:30  </td><td align="right"> 80K</td></tr>
            <tr><td><a href="plugin.video.sportsurge-1.4.0.zip">plugin.video.sportsurge-1.4.0.zip</a></td><td align="right">2026-09-18 19:30  </td><td align="right">460K</td></tr>
            <tr><td><a href="sportsurge.m3u">sportsurge.m3u</a></td><td align="right">2026-09-18 19:30  </td><td align="right"> 40K</td></tr>
            <tr><td><a href="repo/">repo/</a></td><td align="right">2026-09-18 19:30  </td><td align="right">  - </td></tr>
            <tr><th colspan="3"><hr style="border:0;border-top:1px solid #334155;margin:0;"></th></tr>
        </table>

        <div class="instructions">
            <h3>📲 How to Add in Kodi File Manager:</h3>
            <ol>
                <li>In Kodi, open <strong>Settings (Gear)</strong> &gt; <strong>File Manager</strong> &gt; <strong>Add source</strong>.</li>
                <li>Enter the URL: <code>https://jay181020.github.io/repository.sportsurge/</code></li>
                <li>Name the media source: <strong>Sportsurge</strong> and click <strong>OK</strong>.</li>
                <li>Go back to <strong>Settings</strong> &gt; <strong>Add-ons</strong> &gt; <strong>Install from zip file</strong> &gt; select <strong>Sportsurge</strong> &gt; click <code>repository.sportsurge-1.0.0.zip</code>.</li>
            </ol>
        </div>

        <div class="instructions" style="border-left-color: #22c55e; margin-top: 16px;">
            <h3 style="color: #22c55e;">📺 TiviMate Multi-View (Split-Screen & Quad-Box) Setup:</h3>
            <ol>
                <li>In TiviMate, go to <strong>Settings</strong> &gt; <strong>Playlists</strong> &gt; <strong>Add playlist</strong> &gt; <strong>M3U playlist</strong>.</li>
                <li>Enter URL: <code>http://127.0.0.1:8899/playlist.m3u</code> (or cloud URL: <code>https://jay181020.github.io/repository.sportsurge/sportsurge.m3u</code>).</li>
                <li>Play any channel full screen, then <strong>press &amp; hold Select/OK</strong> on your remote.</li>
                <li>Select the <strong>Multi-View</strong> grid icon &gt; <strong>Add Screen</strong> to watch 2, 3, or 4 games at once!</li>
                <li>Use <strong>D-Pad arrows</strong> to switch game audio instantly.</li>
            </ol>
        </div>
    </div>
</body>
</html>
"""
    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated: {index_html_path}")


    # Also generate repo/index.html
    repo_html_path = os.path.join(REPO_DIR, 'index.html')
    repo_html = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Index of /repo/</title></head>
<body>
<h1>Index of /repo/</h1>
<table>
<tr><th>Name</th><th style="text-align:right">Last modified</th><th style="text-align:right">Size</th></tr>
<tr><th colspan="3"><hr></th></tr>
<tr><td><a href="../">Parent Directory</a></td><td></td><td>-</td></tr>
<tr><td><a href="addons.xml">addons.xml</a></td><td align="right">2026-09-18 18:00  </td><td align="right"> 2K</td></tr>
<tr><td><a href="addons.xml.md5">addons.xml.md5</a></td><td align="right">2026-09-18 18:00  </td><td align="right">32B</td></tr>
<tr><td><a href="zips/">zips/</a></td><td align="right">2026-09-18 18:00  </td><td align="right">-</td></tr>
<tr><th colspan="3"><hr></th></tr>
</table>
</body></html>"""
    with open(repo_html_path, 'w', encoding='utf-8') as f:
        f.write(repo_html)
    print(f"Generated: {repo_html_path}")
    print("\nRepository build completed successfully!")


if __name__ == '__main__':
    generate_repo()
