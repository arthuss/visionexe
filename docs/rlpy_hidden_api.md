# RLPy Hidden API Notes

Reallusion ships the real Python API surface inside the local `RLPy.py` file.
The official docs can be incomplete; use this file as the source of truth.

## Where to find it

Character Creator 4:
- `C:\Program Files\Reallusion\Character Creator 4\Bin64\RLPy.py`

iClone 8:
- `C:\Program Files\Reallusion\iClone 8\Bin64\RLPy.py`

## Quick search helper

Use the repo tool:
```
python engine/tools/rlpy_api_finder.py "C:\Program Files\Reallusion\Character Creator 4\Bin64\RLPy.py" RHeadshot EHSMode EHSBodyType --context 2
```

List symbols (classes and functions):
```
python engine/tools/rlpy_api_finder.py "C:\Program Files\Reallusion\iClone 8\Bin64\RLPy.py" --list-symbols --limit 200
```

## Wiki compatibility checker

If you have a local Reallusion wiki HTML dump, compare it against `RLPy.py`:
```
python engine/tools/rlpy_wiki_compat.py --rlpy-path "C:\Program Files\Reallusion\iClone 8\Bin64\RLPy.py" --output-dir C:\temp\rlpy_wiki
```

Notes:
- Set `RL_WIKI_ROOT` to the wiki dump root, or pass `--wiki-root`.
- Default wiki root: `C:\projects\my-selenium-scripts\advanced_web_scraper\data\raw\wiki` (if present).
- Outputs: `wiki_symbols.jsonl`, `rlpy_symbols.jsonl`, `compat_report.json`, `compat_report.md`.

## Example (Headshot)

In `RLPy.py` you will find:
- `class RHeadshotOption`
- `class RHeadshot`
- `RHeadshot.CreateHeadFromPhoto(strPhotoPath, eMode, kOption)`
- Enums: `EHSMode_Auto`, `EHSMode_Pro`, `EHSBodyType_Male/Female/Baby/Neutral/Current`

Minimal CC4 script:
```
import RLPy

opt = RLPy.RHeadshotOption()
opt.eBodyType = RLPy.EHSBodyType_Female

result = RLPy.RHeadshot.CreateHeadFromPhoto(
    r"C:\path\photo.png",
    RLPy.EHSMode_Auto,
    opt
)
print(result)
```

## Notes

- Treat `RLPy.py` as authoritative. It reflects the actual bindings the host exports.
- Many APIs exist but are undocumented on the public site.
- For automation, prefer official bindings over UI automation or Lua hooks.
