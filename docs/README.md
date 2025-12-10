# GitHub Pages Setup

This directory contains the GitHub Pages website for ApexEngineer.

## Configuration

To enable GitHub Pages for this repository:

1. Go to your repository settings on GitHub
2. Navigate to **Pages** in the left sidebar
3. Under **Source**, select:
   - **Branch**: `main` (or your default branch)
   - **Folder**: `/docs`
4. Click **Save**

Your site will be available at:
`https://sisques-labs.github.io/apex-engineer/`

## Local Preview

To preview the site locally, you can use Python's built-in HTTP server:

```bash
cd docs
python3 -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

## Files

- `index.html` - Main HTML page with all project information
- `.nojekyll` - Prevents Jekyll processing (not needed, but ensures compatibility)

