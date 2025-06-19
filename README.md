# Road to 2112 – GPB Automation

This repo **automates**  
1. fetching the latest StudyRiver article (21:00 JST)  
2. rewriting it into kid-friendly stories (L1 / L2 / L3)  
3. translating them into Tier-A languages  
4. compiling monthly EPUB bundles ready for Google Play Books

## Workflow Overview
| Action | Schedule | Output |
|--------|----------|--------|
| `daily_fetch` | 21:00 JST daily | `stories/<lang>/<level>/YYYY/MM/*.md` |
| `monthly_epub` | 1st 00:00 UTC | `dist/Rt2112_<level>_<lang>_<YYYYMM>.epub` |

## Environment / Secrets
- `OPENAI_API_KEY` – required
- `TRANSLATE_LANGS` – e.g. `en,es,pt,fr,id,zh-hant`
- `TARGET_COUNT` – max stories per bundle (default 31)
- *(Publishing)*
  - `PB_SFTP_USER`, `PB_SFTP_KEY`

## Local test
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/fetch_latest.py
python scripts/story_from_article.py tmp/article.json stories/
python scripts/translate.py stories/
python scripts/compile_epubs.py stories/ dist/
