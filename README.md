# Google Play Books Pipeline

This repository automates turning StudyRiver articles into short stories and publishing them on Google Play Books.

## Project Goals

1. Fetch new StudyRiver articles.
2. Generate levelled stories from those articles.
3. Translate stories into multiple languages.
4. Package the content as EPUB files.
5. Upload finished books to Google Play Books.

## GitHub Workflows

### Daily Fetch

Runs every day at **12:00 UTC**. It installs dependencies, fetches StudyRiver data, generates stories, translates them and commits the results back to the repository.

### Monthly Publish

Runs at **00:00 UTC on the first day of each month** and can also be triggered manually. It builds and publishes EPUBs using the following environment variables:

- `SOURCE_LANG` – source language for the articles (default `ja`).
- `TRANSLATE_LANGS` – space-separated list of target languages (default `"en es pt hi id zh-Hant"`).
- `TARGET_COUNT` – number of stories to include for each language/level (default `10`).

The workflow iterates over levels `l1`, `l2` and `l3` for each language, builds the story sets, creates EPUBs, generates metadata and uploads the files to Google Play Books.

## Required GitHub Secrets

The workflows expect these secrets to be defined in the repository settings:

- `OPENAI_API_KEY`
- `NEWS_API_KEY`
- `PB_SFTP_USER`
- `PB_SFTP_KEY`

## Running Locally

1. Make sure Python 3 is available.
2. Install any dependencies if `requirements.txt` exists:
   ```bash
   pip install -r requirements.txt
   ```
3. Export the same environment variables and secrets used in CI.
4. Execute the scripts in order, for example:
   ```bash
   python fetch_studyriver.py
   python generate_story.py
   python translate.py
   # Build and upload when ready
   python select_latest_stories.py --level l1 --lang ja --count 10
   python build_story_set.py --level l1 --lang ja
   python build_epub.py --level l1 --lang ja
   python generate_metadata_csv.py --level l1 --lang ja
   python upload_to_gpb.py --level l1 --lang ja
   ```
Adjust the level, language and counts as needed.
