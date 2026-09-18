# -*- coding: utf-8 -*-
"""
Kodi Repository Generator Script.
Builds addons.xml, addons.xml.md5, and packages zip archives for the repository.
"""

import os
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

    # Generate index.html for GitHub Pages and Kodi File Manager source
    index_html_path = os.path.join(REPO_ROOT, 'index.html')
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sportsurge Kodi Repository</title>
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
            max-width: 720px;
            width: 100%;
            background: #1e293b;
            border-radius: 12px;
            padding: 28px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            border: 1px solid #334155;
        }
        h1 {
            margin-top: 0;
            color: #38bdf8;
            font-size: 1.8rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        p {
            color: #94a3b8;
            line-height: 1.6;
        }
        .file-list {
            list-style: none;
            padding: 0;
            margin: 20px 0;
        }
        .file-list li {
            background: #0f172a;
            margin-bottom: 12px;
            border-radius: 8px;
            border: 1px solid #334155;
            transition: border-color 0.2s;
        }
        .file-list li:hover {
            border-color: #38bdf8;
        }
        .file-list a {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 18px;
            color: #f1f5f9;
            text-decoration: none;
            font-weight: 500;
        }
        .badge {
            background: #0284c7;
            color: white;
            padding: 3px 10px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .badge-green {
            background: #16a34a;
        }
        .instructions {
            background: #0f172a;
            border-left: 4px solid #38bdf8;
            padding: 14px 18px;
            border-radius: 0 8px 8px 0;
            margin-top: 24px;
        }
        .instructions h3 {
            margin-top: 0;
            color: #f8fafc;
            font-size: 1rem;
        }
        .instructions ol {
            margin: 0;
            padding-left: 20px;
            color: #94a3b8;
            line-height: 1.6;
        }
        .instructions code {
            background: #1e293b;
            color: #38bdf8;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏈 Sportsurge Kodi Repository</h1>
        <p>Live repository files for automated add-on installation and background updates across Kodi 19 Matrix, Kodi 20 Nexus, and Kodi 21 Omega.</p>
        
        <ul class="file-list">
            <li>
                <a href="repository.sportsurge-1.0.0.zip">
                    <span>📦 repository.sportsurge-1.0.0.zip</span>
                    <span class="badge">Repository Installer</span>
                </a>
            </li>
            <li>
                <a href="plugin.video.sportsurge-1.3.0.zip">
                    <span>⚡ plugin.video.sportsurge-1.3.0.zip</span>
                    <span class="badge badge-green">v1.3.0 Latest</span>
                </a>
            </li>
            <li>
                <a href="repo/zips/plugin.video.sportsurge/plugin.video.sportsurge-1.3.0.zip">
                    <span>📁 repo/zips/plugin.video.sportsurge/plugin.video.sportsurge-1.3.0.zip</span>
                </a>
            </li>
            <li>
                <a href="repo/addons.xml">
                    <span>📋 repo/addons.xml</span>
                </a>
            </li>
        </ul>

        <div class="instructions">
            <h3>📲 How to Add in Kodi File Manager:</h3>
            <ol>
                <li>In Kodi, open <strong>Settings (Gear)</strong> &gt; <strong>File Manager</strong> &gt; <strong>Add source</strong>.</li>
                <li>Enter the URL: <code>https://jay181020.github.io/repository.sportsurge/</code></li>
                <li>Name the media source: <strong>Sportsurge</strong> and click <strong>OK</strong>.</li>
                <li>Go back to <strong>Settings</strong> &gt; <strong>Add-ons</strong> &gt; <strong>Install from zip file</strong> &gt; select <strong>Sportsurge</strong> &gt; click <code>repository.sportsurge-1.0.0.zip</code>.</li>
            </ol>
        </div>
    </div>
</body>
</html>
"""
    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated: {index_html_path}")
    print("\nRepository build completed successfully!")


if __name__ == '__main__':
    generate_repo()
