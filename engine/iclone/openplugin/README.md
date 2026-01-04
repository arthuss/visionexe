# iClone OpenPlugin wrappers

These folders are thin wrappers so VisionExe iClone scripts appear in the
Plugins menu and can be launched without browsing for files.

## Install (one-time)

1. Set user environment variables (recommended):
   - `VISIONEXE_ROOT` = `C:\Users\sasch\visionexe`
   - `ICLONE_CONFIG_PATH` = `C:\Users\sasch\visionexe\engine\iclone\iclone_config.json`
2. Create a junction or copy the wrapper folders into iClone's OpenPlugin path:

```
C:\Program Files\Reallusion\iClone 8\Bin64\OpenPlugin
```

Recommended (junction):

```powershell
New-Item -ItemType Junction `
  -Path "C:\Program Files\Reallusion\iClone 8\Bin64\OpenPlugin\visionexe_remote_server" `
  -Target "C:\Users\sasch\visionexe\engine\iclone\openplugin\visionexe_remote_server"

New-Item -ItemType Junction `
  -Path "C:\Program Files\Reallusion\iClone 8\Bin64\OpenPlugin\visionexe_md_probe" `
  -Target "C:\Users\sasch\visionexe\engine\iclone\openplugin\visionexe_md_probe"
```

Now launch via **Plugins > Python > visionexe_remote_server** or
**visionexe_md_probe**.

You can also use the helper installer:

```powershell
engine\launchers\Install-iCloneOpenPlugin.ps1
```

Content indexer:

```powershell
New-Item -ItemType Junction `
  -Path "C:\Program Files\Reallusion\iClone 8\Bin64\OpenPlugin\visionexe_content_indexer" `
  -Target "C:\Users\sasch\visionexe\engine\iclone\openplugin\visionexe_content_indexer"
```

Launch via **Plugins > Python > visionexe_content_indexer**.
