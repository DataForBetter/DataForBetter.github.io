# Adeyemi Zainab: Portfolio

A portfolio website for a business intelligence analyst, with case studies built in Excel, SQL and Power BI.

## What is in this repository

| Path | Purpose |
| --- | --- |
| `index.html` | The full website in one file: home page, case studies, experience, skills and contact |
| `adun-foods-powerbi/` | The Adun Foods distributor network case study: data, scripts, documentation and dashboards |
| `.gitignore` | Keeps Power BI cache files and system files out of version control |

## Viewing the website

Open `index.html` in any browser. The site needs no build step and no installation.

Once the repository is on GitHub it can be published free with GitHub Pages. In the repository settings choose **Pages**, select the `main` branch and the root folder, then save.

## The Adun Foods case study

Three Power BI dashboards on a synthetic Nigerian distributor network, with the data generator, the analysis script and the documentation that backs every figure. See [adun-foods-powerbi/README.md](adun-foods-powerbi/README.md).

```bash
cd adun-foods-powerbi
pip install -r requirements.txt
python scripts/generate_data.py
python scripts/analyse.py
```

## Still to add

- **Contact details**: email, LinkedIn, GitHub and CV link, marked "to be added" in `index.html`.
- **Coffee and beverage findings**: those two case studies have placeholders where findings belong.

## Data

All data in the Adun Foods project is synthetic and produced by `adun-foods-powerbi/scripts/generate_data.py` from a fixed seed. The client work described in the coffee and beverage case studies is anonymised, with no client names or confidential figures.
