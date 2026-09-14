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

        # Also copy repository zip to root for convenient installation
        if addon_id == 'repository.sportsurge':
            root_zip = os.path.join(REPO_ROOT, zip_filename)
            shutil.copy2(target_zip, root_zip)
            print(f"  Installer zip ready: {root_zip}")

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
    print("\nRepository build completed successfully!")


if __name__ == '__main__':
    generate_repo()
