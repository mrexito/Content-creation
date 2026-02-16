# LangChain vs. LangGraph: Automated Content Rewriting

Master Thesis - Berner Fachhochschule

## 🎯 Projekt-Übersicht

Vergleich von LangChain, LangGraph und einem hybriden Ansatz für
automatisiertes Content-Rewriting von Lern- und Trainingsmaterialien.

## 🚀 Quick Start

### Installation

```bash
# Python Dependencies
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Umgebungsvariablen

```bash
cp .env.example .env
# Füge deine API-Keys hinzu
```

### Prototypen ausführen

```bash
# LangChain
python src/langchain_prototype/run_langchain.py

# LangGraph
python src/langgraph_prototype/run_langgraph.py

# Hybrid
python src/hybrid_prototype/run_hybrid.py
```

### Frontend starten

```bash
cd frontend
npm run dev
```

## 📚 Dokumentation

Siehe `docs/` Ordner für detaillierte Dokumentation.

## 🧪 Tests

```bash
pytest tests/
```

## 📊 Testdomänen

- Mathematik (SymPy-Validierung)
- Sprachwissenschaften (BERTScore)
- Wirtschaftswissenschaften (Konsistenz-Checks)
