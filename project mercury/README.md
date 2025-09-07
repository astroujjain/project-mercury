# Project Mercury (Lightweight)

This repo generates a daily PDF commodity outlook for Gold & Silver.
It is lightweight and designed to run on GitHub Actions (free for public repos).

## Run locally
1. python -m venv venv
2. source venv/bin/activate  # or venv\Scripts\activate on Windows
3. pip install -r requirements.txt
4. python -m project_mercury.cli

Output: output/Project_Mercury_Report.pdf

## GitHub Actions
A workflow is included at .github/workflows/daily.yml to run daily and upload the PDF as artifact.

Optional: Set NEWSAPI_KEY as repo secret to enable news headlines fetching.