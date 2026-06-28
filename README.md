# మా కుటుంబ ఆహార ప్రణాళిక (Family Diet Plan)

Andhra-style Telugu 10-day family meal plan — built with **MkDocs Material**.
Tiffin mornings/nights, rice lunch, kids' school boxes, homemade snack recipes,
shopping lists, nutrition notes. Search + dark mode + mobile nav.

**Live:** https://ashok-gembali.github.io/maa-aaharam/

## Rebuild
```
python3 -m venv .venv && ./.venv/bin/pip install -r _src/requirements.txt
cd _src && ../.venv/bin/mkdocs build -d ../   # outputs site to repo root
```
Source markdown lives in `_src/docs/`.
