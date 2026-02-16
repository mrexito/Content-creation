# OCR/Parsing-Vergleich

## Datum: 16.02.2026

## Getestete Technologien

### 1. Mistral OCR (pixtral-12b-2409)

**Status:** ✅ Funktioniert sehr gut

**Test-Ergebnisse:**

- Math PDFs: ~2.8s pro Seite, Formeln erkannt
- Language PDFs: ~2.5s pro Seite, Text vollständig
- Economics PDFs: ~3.1s pro Seite, Tabellen als Text

**Vorteile:**

- Sehr gute Texterkennung
- Erkennt Strukturen (Überschriften, Listen)
- LaTeX-Formeln werden korrekt extrahiert
- Schnelle Verarbeitung (~3s pro Seite)

**Nachteile:**

- Benötigt API-Key und Internet-Verbindung
- Kosten pro API-Call
- Abhängigkeit von externem Service

---

### 2. Nougat OCR

**Status:** ❌ Nicht praktikabel

**Problem:**

- Extrem langsam (>10 Minuten für eine Seite)
- Timeout-Probleme
- Versionsinkompatibilitäten mit Dependencies
- Nicht wartbar

**Entscheidung:**
Wird nicht weiter verfolgt aufgrund inakzeptabler Performance.

---

### 3. Tesseract OCR

**Status:** ✅ Funktioniert gut, GEWÄHLT

**Test-Ergebnisse:**

- Math PDFs: ~1.2s pro Seite, Text erkannt
- Language PDFs: ~0.9s pro Seite, Text vollständig
- Economics PDFs: ~1.5s pro Seite, Tabellen erkannt

**Vorteile:**

- Open Source & kostenlos
- Schnell (~1s pro Seite)
- Offline nutzbar
- Von BFH selbst hostbar
- Stabile, bewährte Software
- Einfache Integration

**Nachteile:**

- LaTeX-Formeln werden nicht automatisch erkannt
- Layout-Erkennung weniger sophisticated

---

## Vergleichstabelle

| Kriterium              | Mistral OCR | Nougat         | Tesseract |
| ---------------------- | ----------- | -------------- | --------- |
| **Geschwindigkeit**    | ~3s/Seite   | >600s/Seite ❌ | ~1s/Seite |
| **Qualität (Text)**    | ⭐⭐⭐⭐⭐  | ?              | ⭐⭐⭐⭐  |
| **Qualität (Formeln)** | ⭐⭐⭐⭐⭐  | ?              | ⭐⭐      |
| **Kosten**             | API-Calls   | Kostenlos      | Kostenlos |
| **Offline**            | ❌          | ✅             | ✅        |
| **Wartbarkeit**        | ✅          | ❌             | ✅        |
| **BFH-hostbar**        | ❌          | ✅             | ✅        |

---

## Finale Entscheidung

**Für alle drei Prototypen wird Tesseract OCR verwendet.**

### Begründung:

1. **Kosteneffizienz:** Komplett kostenlos, keine laufenden API-Kosten
2. **Performance:** Ausreichend schnell für iterative Entwicklung
3. **Autonomie:** Von der BFH selbst hostbar, keine externe Abhängigkeit
4. **Nachhaltigkeit:** Open Source, gut dokumentiert, aktiv maintained
5. **Pragmatismus:** Für Lern-/Trainingsmaterialien ausreichende Qualität

### Kompensation der Schwächen:

Die geringere Qualität bei mathematischen Formeln wird durch
**LLM-basierte Nachbearbeitung** im Agentenworkflow kompensiert:

- SymPy validiert und korrigiert mathematische Ausdrücke
- LLM kann erkannte Textformeln in LaTeX umwandeln
- Validierungsschleifen stellen Korrektheit sicher

---

## Implementierung

Tesseract wird in `src/common/ocr_handler.py` als zentrale
OCR-Komponente implementiert und von allen drei Prototypen
(LangChain, LangGraph, Hybrid) verwendet.
