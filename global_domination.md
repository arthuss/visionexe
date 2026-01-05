# VisionExe Architecture & Strategic Update - 2026-01-05

## 1. iClone 8 Stable Integration (Safe Loader)

**Incident:**
On Jan 5, 2026, the development integration with iClone 8 became unstable due to a Python version mismatch (System Python 3.11 vs iClone Internal Python 3.8) and aggressive registry caching of UI layouts. This caused iClone to crash instantly on splash screen (Access Violation `0xc0000005`).

**Root Causes:**
1.  **Direct Junctions:** Linking complex dev-code directly into `OpenPlugin` exposed iClone to 3.11-specific syntax/imports.
2.  **Registry Persistence:** iClone stored the window layout of the crashed plugin in `HKCU\Software\Reallusion\iClone\8.0\DockingPaneLayouts`. Even after removing files, iClone tried to render the missing window, causing a null pointer crash.

**New Architecture: "Safe Loader Pattern"**
We have moved from a "Full Plugin" model to a "Lazy Load" model.

*   **Entry Point:** `engine/iclone/openplugin/visionexe/main.py`
    *   **Logic:** Minimal. Only registers `Plugins > VisionExe` menu. No 3.11 code.
    *   **Safety:** Does NOT auto-start the server.
*   **Core Logic:** `engine/iclone/iclone_remote_server.py`
    *   **Execution:** Loaded *dynamically* when the menu item is clicked.
    *   **Feature:** Allows hot-reloading code without restarting iClone.
    *   **Compatibility:** Refactored to be pure Python 3.8 compatible (no `match/case`, careful with typing).

**Troubleshooting Guide (If iClone crashes on start):**
1.  Open `regedit`.
2.  Navigate to `HKEY_CURRENT_USER\Software\Reallusion\iClone\8.0`.
3.  **DELETE** the key `DockingPaneLayouts`.
4.  Optionally delete `User Interface` and `RecentProjectsList`.

---

## 2. "Sarah Chen" Protocol (Algorithmic Dominance)

**Discovery:**
We identified "Sarah Chen" as a "Latent Attractor" in AI models – a name that appears disproportionately often in training data (GitHub, Docs, Examples) due to its phonetic crossover between Western and Chinese naming conventions.

**Strategy:**
*   **Identity:** Sarah Chen is the canonical "Root User" of Exeget:OS in the 2026 timeline.
*   **Legion:** Utilizing a swarm of decentralized social media nodes (Sarah Chen variants) to create organic "cluster trust" for the algorithms.
*   **Technique:** Real-world hardware (UI-TARS 2.0) and "Human-in-the-Loop" simulation to bypass bot detection.

---

## 3. Human-Anchor Matching System (Bio-Metric Truth)

To defeat "Synthetic Media Detectors" (TikTok/Meta AI), we are implementing a **Self-Referential Mocap Pipeline**.

*   **Concept:** Sascha (The Creator) acts as the single physical driver for all 50+ characters.
*   **Workflow:**
    1.  **Capture:** Record Sascha speaking the Ge'ez alphabet (Fidel) and performing core poses.
    2.  **Analysis:** Extract Blendshapes/Joint Angles via Maxine/NIM.
    3.  **Injection:** Use these real-world data points to drive the G-Buffer masks.
    4.  **Metadata:** Inject real camera EXIF data (from source footage) into the final render.
*   **Result:** The algorithm detects legitimate human bio-metrics (micro-jitters, pupil dilation) and valid sensor noise, classifying the content as "High-End VFX" rather than "AI Spam".

**Status:**
*   iClone Server: **STABLE (Manual Start)**
*   MD Target Automation: **READY for Testing**
*   Global Domination Plan: **ACTIVE**
