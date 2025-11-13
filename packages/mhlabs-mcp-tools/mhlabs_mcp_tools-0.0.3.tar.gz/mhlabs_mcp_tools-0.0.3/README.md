# mhlabs-mcp-tools

mcp-name: io.github.MusaddiqueHussainLabs/mhlabs_mcp_tools

`mhlabs-mcp-tools` is a modular collection of MCP tools designed for text preprocessing (`textprep`) and natural language processing (`nlp`) tasks. It provides a structured and extensible registry system to load, execute, and manage AI components.

## ✨ Features
- Hierarchical tool namespaces: `textprep.*`, `nlp.*`
- Configurable preprocessing pipelines
- PII masking utilities
- Tokenization, normalization, and cleaning
- Modular registry for dynamic tool loading

## 🧩 Tool Categories
### TextPrep Tools (`textprep.*`)
- `textprep.remove_email`
- `textprep.remove_phone_number`
- `textprep.remove_punctuation`
- `textprep.preprocess_text`

### NLP Tools (`nlp.*`)
- `nlp.load_component`
- `nlp.predict_component`

## 🧱 Project Structure
