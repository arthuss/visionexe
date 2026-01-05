# iClone OpenPlugin (VisionExe)

Use the **single** VisionExe plugin folder. No loose scripts, no junctions.

## Install (one-time)

Copy this folder to iClone's OpenPlugin path:

```
engine\iclone\openplugin\visionexe
```

Target:

```
C:\Program Files\Reallusion\iClone 8\Bin64\OpenPlugin\visionexe
```

Optional helper:

```powershell
engine\launchers\Install-iCloneOpenPlugin.ps1 -Mode Copy
```

## Usage

Restart iClone. Launch via **Plugins > VisionExe > Open VisionExe Panel**,
then click **Start Server**.

Config lives next to the plugin (edit after install):

```
C:\Program Files\Reallusion\iClone 8\Bin64\OpenPlugin\visionexe\iclone_config.json
```
