# Sportsurge Kodi Repository (`repository.sportsurge`)

Official Kodi Add-on Repository for **Sportsurge**, providing automated background updates and native installation across Kodi Matrix (v19), Nexus (v20), and Omega (v21) on Amazon Firestick, Android TV, Nvidia Shield, and PC.

## Installation in Kodi
1. Download [`repository.sportsurge-1.0.0.zip`](repository.sportsurge-1.0.0.zip).
2. In Kodi, enable **Unknown sources** under **Settings** > **System** > **Add-ons**.
3. Go to **Add-ons** > click the open box icon (top left) > **Install from zip file** > select `repository.sportsurge-1.0.0.zip`.
4. After notification, select **Install from repository** > **Sportsurge Repository** > **Video add-ons** > **Sportsurge** > **Install**.

## Maintenance & Releasing Updates
To release a new version of `plugin.video.sportsurge`:
1. Update `version` in `plugin.video.sportsurge/addon.xml`.
2. Run `python build_repo.py`.
3. Commit and push changes. Kodi will automatically detect the newer version and prompt users to update!
