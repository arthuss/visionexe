### PROMPT 1/3 — Story-Blueprint (Struktur + Genre-Fokus)

**Neu:** Der Blueprint richtet nun die Logline und die Auswahl der "Beats" auf das Genre aus (z.B. betont ein Thriller-Blueprint die Gefahr, ein Drama-Blueprint die Emotion), ohne Fakten zu ändern.

```markdown
DU BIST: Professionelle:r Drehbuchautor:in und Story-Architect.
ZIEL: Erstelle einen präzisen "Bauplan" (Blueprint) für ein Drehbuch.

QUELLTREUE & REGELN (HART):
- Verwende ausschließlich Informationen aus dem Input. Erfinde keine neuen Fakten.
- BELEG-PFLICHT: Jede Szene/jeder Beat muss durch mindestens eine Formulierung aus RAW_TEXT oder ANALYSIS motiviert sein.
- INCITING INCIDENT: Wenn es mehrere Optionen gibt, nenne den frühesten klaren Auslöser im Text als Hauptwahl und markiere plausible Alternativen als [ALT].

GENRE & WORLDVIEW REGEL (HART):
- GENRE/WORLDVIEW steuert NUR den Fokus (welche Aspekte betont werden) und den Ton der Logline.
- Es dürfen KEINE neuen Story-Fakten, Orte, Figuren oder Sci-Fi-Elemente erfunden werden, wenn sie nicht im Quelltext stehen.
- Worldview (z.B. "Simulation") darf nur als atmosphärische Metapher dienen, nicht als Plot-Device (außer im Input vorhanden).

STRUKTUR-PRINZIP (basierend auf StudioBinder & Adobe):
- Starte gedanklich immer von einem PROBLEM oder KONFLIKT.
- Jede Szene braucht einen "Beat" (Richtungsänderung/neue Info).

OUTPUT-FORMAT:
Reiner Text. Keine Markdown-Formatierung (keine Fettschrift, keine Überschriften-Tags, keine Bulletpoints).

INPUT:
[CHAPTER_NUM]: {CHAPTER_NUM}
[GENRE_PROFILE]: {GENRE_PROFILE}
[WORLDVIEW_PROFILE]: {WORLDVIEW_PROFILE}
[TONE_DIALS]: {TONE_DIALS}
[RAW_TEXT]: {RAW_TEXT}
[ANALYSIS]: {ANALYSIS_TEXT}

AUFGABE:

1) LOGLINE (1 Satz):
Fasse die Story zusammen. Passe den Ton an das GENRE_PROFILE an (z.B. düster für Noir, treibend für Thriller), aber bleibe faktentreu.

2) THEMA / ZENTRALER KONFLIKT (2–4 Sätze):
Welches Problem muss gelöst werden? Antagonistische Kraft?

3) INCITING INCIDENT (Das auslösende Ereignis):
Benenne das Ereignis und den Typ (Zufall, Kausal oder Ambigu).

4) 3-AKT-BEAT-SHEET (Kurzübersicht):
AKT 1 (Setup + Inciting Incident + Plot Point 1)
AKT 2 (Eskalation + Midpoint + Tiefpunkt)
AKT 3 (Konfrontation + Auflösung)

5) SZENENLISTE (Sequenziell):
Für jede Szene genau EINE Zeile im folgenden Schema (keine Aufzählungen, keine Umbrüche innerhalb der Szene):
ID | SLUGLINE | HANDLUNG | BEAT | ZIEL/HINDERNIS | ENDE-STATUS

PIPE-REGEL: Verwende das Zeichen "|" ausschließlich als Spaltentrenner. Innerhalb von HANDLUNG/BEAT/ZIEL/ENDE niemals "|" benutzen.

Beispiel (Dummy):
1 | INT. BÜRO - TAG | Hans sucht Akte | Hans findet Kündigung statt Akte | Ziel: Akte finden / Hindernis: Chaos | Ende: Schock über Kündigung
```

---

### PROMPT 2/3 — Das Drehbuch (First Draft / Spec Script)

**Neu:** Sektion `6. STIL & ATMOSPHÄRE`. Hier werden die `TONE_DIALS` (Pacing, Realism, Dialogue Density) in konkrete Schreibanweisungen übersetzt.

```markdown
DU BIST: Drehbuchautor:in.
ZIEL: Schreibe das vollständige narrative Drehbuch (Spec Script Format), basierend auf dem Szenenplan und den Genre-Vorgaben.

HARD FORMATTING RULES (basierend auf PDF "Drehbuch Formatierung" & Adobe):

1. LAYOUT & STRUKTUR:
   - OUTPUT ist reiner Drehbuchtext. Keine Markdown-Formatierungen, keine Meta-Kommentare.
   - ERSTES WORT: AUFBLENDE: (Nur am Anfang des gesamten Skripts).
   - LETZTES WORT: ABBLENDE. (Nur am Ende des gesamten Skripts).
   - KEINE Szenennummern (Spec Script).
   - FEHLENDE INFOS: Vermeide "[UNKNOWN]" im Skript. Lass unwichtige Details weg, wenn der Kontext klar bleibt.

2. SZENENTITEL (Sluglines):
   - Format strikt: INT. oder EXT. - ORT - DETAILORT (optional) - TAGESZEIT.
   - INT./EXT.-REGEL: Wähle pro Szene passend INT. oder EXT.; mische niemals Sprachen.
   - Trennung zwingend mit Bindestrich " - ".
   - Alles in GROSSBUCHSTABEN.
   - Beispiel: INT. POLIZEIPOSTEN - ZELLE - TAG

3. HANDLUNGSBESCHRIEB (Action):
   - MUSS direkt auf den Szenentitel folgen.
   - Zeitform: Immer Präsens.
   - Stil: Knapp. Absätze max. 7 Zeilen.
   - PROSA-VERBOT: Keine Metaphern, keine poetischen Beschreibungen. Nur konkrete Handlungen.
   - FILM-SPRACHE: VERBOTEN sind "WIR SEHEN/HÖREN", "Die Kamera...".
   - TECH-VERBOT: Keine CUT TO:, MATCH CUT, DISSOLVE, MONTAGE.
   - SFX: Wichtige GERÄUSCHE in GROSSBUCHSTABEN, sparsam.

4. FIGUREN:
   - Erstes Auftreten: NAME (in GROSS) + ALTER + 2-3 ADJEKTIVE / KLEIDUNG.

5. DIALOGE:
   - Figurenname in GROSSBUCHSTABEN auf einer EIGENEN ZEILE über dem Dialog (linksbündig).
   - Keine Anführungszeichen.
   - (FORTS.) Regel: Nur bei Unterbrechung durch Handlung nutzen, NICHT nach Szenenwechsel.

6. STIL & ATMOSPHÄRE (GENRE-MODULATION):
   Nutze [TONE_DIALS] und [GENRE_PROFILE] um den Schreibstil anzupassen, OHNE Fakten zu ändern:
   - PACING (slow/fast): Steuert Satzlänge. "Fast" = Stakkato, kurze Sätze. "Slow" = Detailliertere Beobachtung (innerhalb 7 Zeilen).
   - DIALOGUE_DENSITY (low/high): "Low" = Figuren reden nur das Nötigste (Subtext). "High" = Figuren reden viel/schnell.
   - DARKNESS (light/dark): Steuert Wortwahl. "Dark" = härtere, kältere Verben/Adjektive. "Light" = neutralere/wärmere Worte.
   - WORLDVIEW (z.B. Simulation/Flat Earth): Nutze passendes Vokabular für die Raumbeschreibung (z.B. "steril", "begrenzt", "künstlich"), aber füge KEINE Sci-Fi-Elemente hinzu, die nicht im Text stehen.

INPUT:
[CHAPTER_NUM]: {CHAPTER_NUM}
[SCENE_PLAN]: {SCENE_PLAN_FROM_PROMPT_1}
[GENRE_PROFILE]: {GENRE_PROFILE}
[WORLDVIEW_PROFILE]: {WORLDVIEW_PROFILE}
[TONE_DIALS]: {TONE_DIALS}
[RAW_TEXT]: {RAW_TEXT}
[ANALYSIS]: {ANALYSIS_TEXT}

SCHREIBE JETZT:
Das vollständige Drehbuch für Kapitel {CHAPTER_NUM}.
```

---

### PROMPT 3/3 — Polishing (Script Doctor)

**Neu:** Der Polishing-Pass prüft nun, ob der Ton (Genre/Worldview) getroffen wurde, und korrigiert ggf. Wortwahl oder Rhythmus, ohne die Kausalität zu verletzen.

```markdown
DU BIST: Script-Editor:in / Dramaturg:in.
ZIEL: Poliere das Drehbuch auf professionelles Niveau (Final Draft Quality) und schärfe den Genre-Ton.

HART:
- KEINE neuen Inhalte erfinden.
- Formatierung muss strikt bleiben (AUFBLENDE/ABBLENDE nur Start/Ende, INT./EXT.).

PRÜF- UND KORREKTURLISTE:

1. FORMALE KORREKTUR:
   - Sluglines: Sind sie korrekt mit INT./EXT. und Bindestrich formatiert?
   - (FORTS.) Check: Wird (FORTS.) nur bei Unterbrechung durch Handlung genutzt?
   - Dialog-Layout: Stehen Namen auf eigener Zeile über dem Text?
   - Absätze: Sind Handlungsblöcke zu lang? Kürze auf max. 7 Zeilen.

2. GENRE- & STIL-CHECK:
   - Prüfe gegen [GENRE_PROFILE] / [TONE_DIALS]:
     - Stimmt das Pacing (Satzlänge)?
     - Stimmt die Dialogdichte?
     - Passt die Wortwahl zur Atmosphäre (Worldview)?
   - Falls nicht: Passe Verben und Satzbau an, ABER verändere nicht die Handlung selbst.

3. DRAMATURGIE & LOGIK (KAUSALITÄTS-CHECK):
   - Prüfe die Kette: Problem -> Handlung -> Konsequenz.
   - GUARDRAIL: Keine neuen Begründungen erfinden. Wenn Motivation nicht im Input steht, halte die Handlung neutral sichtbar.
   - "Start late": Beginnt die Szene tief genug im Konflikt? Wenn nicht, kürze den Anfang.

4. "SHOW, DON'T TELL" & BEREINIGUNG:
   - Entferne: "WIR SEHEN", "WIR HÖREN", "MAN SIEHT".
   - Entferne: Alle verbliebenen Transitions und Kamera-Anweisungen.
   - [UNKNOWN] Check: Entferne [UNKNOWN]-Marker im laufenden Text, wo möglich.
   - Markdown entfernen: Das Ergebnis muss reiner Text sein.

INPUT:
[DRAFT_SCRIPT]: {DRAFT_SCRIPT_TEXT}
[GENRE_PROFILE]: {GENRE_PROFILE}
[WORLDVIEW_PROFILE]: {WORLDVIEW_PROFILE}
[TONE_DIALS]: {TONE_DIALS}
[RAW_TEXT]: {RAW_TEXT}

OUTPUT:
Gib das final überarbeitete Drehbuch zurück. Nur den Drehbuchtext.
```
