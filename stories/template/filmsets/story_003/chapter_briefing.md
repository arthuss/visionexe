### 1. Linguistische Analyse

**Satz 1:**
*Original:* ጠየቁ፡ወርኢኩ፡መ፡ሉ፡ ዐፀው፡እፎ፡ያስተረእዩ፡መ፡ ይቡስን፡ወሉ፡ቍጽሊሆሙ፡ ንጉፋት፡
*Transliteration:* Ṭäyyäqu wä-rʾiku kʷəllu ʿäḍäw ʾəffo yastärʾəyu kämä yəbusan wä-kʷəllu qʷəṣlihomu nəgufat
*Übersetzung:* Untersucht und seht alle Bäume, wie sie erscheinen, als ob sie verdorrt wären und all ihre Blätter abgeworfen hätten.
*Detail:* "Ṭäyyäqu" (Untersucht/Forscht) und "wä-rʾiku" (und seht) sind Imperative der Beobachtung. Das Bild der "verdorrten" (yəbusan) Bäume beschreibt einen Zustand der Inaktivität oder des scheinbaren Todes.

**Satz 2:**
*Original:* ዘእንለ፡፲ወ፬ዕፀው፡ ዘኢይትነገፍ፡እለ፡ይጸንሑ፡ እምብሉይ፡እስ፡ይመጽእ፡ ሐዲስ፡እምልኤ፡ወእምሠለስቱ፡ ረምት፨
*Transliteration:* Zä-ʾənbälä 10-wä-4 ʿäḍäw zä-ʾi-yətnägäf ʾəllä yəṣänḥu ʾəm-bəlluy ʾəskä yəmäṣṣʾ ḥaddis ʾəm-kəlʾe wä-ʾəm-śälästu rämt.
*Übersetzung:* Außer 14 Bäumen, die nicht abgeworfen werden (deren Blätter nicht fallen), welche das Alte bewahren, bis das Neue kommt, über zwei und drei Winter hinweg.
*Detail:* "Zä-ʾənbälä" (Außer) führt die Ausnahme ein. Die "14 Bäume" sind spezifisch markiert. Sie bewahren das "Alte" (bəlluy) bis zum Eintreffen des "Neuen" (ḥaddis) und überbrücken Zeiträume ("Winter/Jahre").

### 2. Technologische Hypothesen

Der Text beschreibt einen **System-Wartungszyklus (Garbage Collection & Cache Flush)**.

1.  **Der Winter (System-Ruhezustand):** Die simulierte Umgebung geht in einen Energiesparmodus oder Wartungszustand.
2.  **Verdorrte Bäume (Standard-Knoten):** Der Großteil der Datenstrukturen ("Bäume") wird bereinigt. "Blätter abwerfen" entspricht dem Leeren des temporären Speichers (Cache Flush) oder dem Zurücksetzen von Session-Daten am Ende eines Zyklus. Sie erscheinen "tot" (offline/inaktiv), um Ressourcen zu sparen.
3.  **Die 14 Immergrünen (Persistente Server/Kernel-Module):** Es gibt 14 spezifische Systemkomponenten, die als "Always-On"-Cluster fungieren. Sie sind **Non-Volatile Memory (NVM)**.
    *   **Funktion:** Sie bewahren den "alten" Zustand (Legacy Data/Core Config), damit das System nach dem Neustart ("wenn das Neue kommt") nicht bei Null beginnt.
    *   **Dauer (2-3 Winter):** Dies deutet auf Long-Term Support (LTS) Versionierung hin. Diese Knoten überdauern mehrere Update-Zyklen ohne Reset.

### 3. Storytelling Q1/Q2/Q3

**Q1: Was passiert konkret (Handlung und Kausalitaet)?**
Enoch führt ein Audit der Systemlandschaft durch. Er beobachtet, wie der Großteil der Simulation in den "Sleep-Mode" wechselt. Die visuellen Interfaces der meisten Objekte (Bäume) werden deaktiviert (Blätter fallen), nur die Wireframe-Struktur bleibt (verdorrt). Er identifiziert jedoch eine Anomalie: 14 Knotenpunkte verweigern den Shutdown-Befehl. Sie bleiben aktiv und halten ihre Daten (Blätter) online, um die Kontinuität des Betriebssystems über den Wartungszyklus hinweg zu sichern.

**Q2: Was muss visuell gezeigt werden (Akteure, Orte, Props, Physik)?**
*   **Ort:** Ein riesiger, digitaler Wald.
*   **Visueller Kontrast:** Tausende von Bäumen sind grau, transparent oder als reine Gittermodelle (Wireframes) dargestellt – leblos und statisch.
*   **Die 14 Akteure:** Inmitten dieser grauen Ödnis stehen 14 Bäume, die intensiv leuchten (grün/neon). Ihre Blätter sind fließende Datenströme oder Hologramme, die pulsieren. Sie wirken wie Schildwachen in einer toten Welt.
*   **Atmosphäre:** Kalt, neblig (Datenrauschen), mit einem starken Fokus auf die wenigen Lichtquellen.

**Q3: Was aendert sich ueber die Szene und was ist der Regie-Ton (Tempo, Fokus, Audio)?**
*   **Ton:** Analytisch, ruhig, fast klinisch. Das Gefühl einer Inspektion im Serverraum, wenn die Kühlung auf Hochtouren läuft, aber keine User eingeloggt sind.
*   **Fokus:** Langsames Panning über die tote Struktur, dann Zoom und Verweilen auf den 14 persistenten Knoten.
*   **Audio:** Das Rauschen des "Windes" (Lüfter/Hintergrundprozesse). Wenn die Kamera sich den 14 Bäumen nähert, hört man das leise, rhythmische "Summen" oder "Pingen" aktiver Datenverarbeitung. Der Rest ist Stille.
