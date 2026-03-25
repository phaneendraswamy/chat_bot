# Personal AI Assistant Project Files

This repository now uses neutral personal-project branding.

Core files:
- `app.py` for the Flask backend
- `index.html` for the UI shell
- `script.js` for client-side chat behavior
- `styles.css` for styling
- `build_vectordb.py` and `vector_search.py` for retrieval

To add your own project knowledge:
1. Put plain text notes in `knowledge_base/`
2. Add source URLs to `links.txt`
3. Run `python build_vectordb.py`
