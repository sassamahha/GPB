# GPB

This project automates fetching StudyRiver articles, generating stories in three reading levels, translating them into multiple languages, and publishing monthly EPUB bundles to Google Play Books.

## Environment Variables
- `SOURCE_LANG` - source language for original stories (default `ja`).
- `TRANSLATE_LANGS` - comma separated list of languages to translate (Core6 by default).
- `TARGET_COUNT` - maximum number of stories to include in monthly release.

## GitHub Secrets
- `OPENAI_API_KEY` - used for text generation.
- `PB_SFTP_USER` - SFTP user for Google Play Books.
- `PB_SFTP_KEY` - SSH private key for SFTP.
- `NEWS_API_KEY` - optional; not required when fetching public WordPress articles.

## Workflows
1. **daily_fetch** (`21:00 JST`)
   - Fetch public articles from StudyRiver using the WordPress REST API.
   - Generate L3 stories then rewrite to L2 and L1.
   - Commit the results to the repository.
2. **monthly_publish** (`1st 00:00 UTC`)
   - Select up to `TARGET_COUNT` latest stories generated after 18:45 JST including kids articles.
   - Build and translate story sets for Core6 languages.
   - Package EPUBs and metadata CSV and upload to Google Play Books. The `On Sale Date` field is left blank so the books become available as soon as Google processes them.

To add more translation languages, append the code to `TRANSLATE_LANGS` in the workflow or environment configuration.
