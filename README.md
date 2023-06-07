# bean-counter

This experimental project aims to answer simple financial questions from the household budget.

- Munge the Google Budget spreadsheets to a single CSV
- Use Sketch to generate Python code to run analysis and plots

## Usage

Run the development server:

```bash
uvicorn src.bean_counter.main:app --port 7998 --reload
```

### Process Inflow

To ingest all incoming costs from the Family Google Sheets, run with `httpie`:

```bash
http POST http://127.0.0.1:7998/process/inflow
```

## Google Sheet API access

1. Enable the Google Drive API and Google Sheets API for the Google Project

2. Add a service account to the Google Project
- https://console.cloud.google.com/iam-admin/serviceaccounts/create?project=bean-counter-387506
  - Create a new key to the service account
  - Download the JSON file and save it to `./config/service_account.json` 

- Google Project Dashboard

  - https://console.cloud.google.com/apis/dashboard?project=bean-counter-387506

- Google APIs

  - https://console.cloud.google.com/apis/library/drive.googleapis.com?project=bean-counter-387506
  - https://console.cloud.google.com/apis/library/sheets.googleapis.com?project=bean-counter-387506

## Resources
- Fam Budget
  - https://docs.google.com/spreadsheets/d/190QeHTRisFY3KwGO3M7wIgrJtvgKg7Dn5Q2a6VC3FWc/edit?usp=drive_web&ouid=108193035389652268079

- Use Google Apps Script to make HTTP requests to trigger munge
  - https://stackoverflow.com/a/23917434

- Develop Lambdas Locally in VS Code using AWS SAM
  - https://www.youtube.com/watch?v=mhdX4znMd2Q

- Build a REST API using AWS Lambda and API Gateway
  - https://www.youtube.com/watch?v=4NY8nst45Rk

- Deploy FastAPI on AWS Lambda
  - https://www.youtube.com/watch?v=RGIM4JfsSk0


## Sample summary gsheet

> Generated from https://jakebathman.github.io/Markdown-Table-Generator/

**Monthly Cashflow ID**|**Direction**|**Name**|**Category**|**Date**|**GBP**
-----|-----|-----|-----|-----|-----
0523-A15-mortgage|Outgoing|Petrol| |05/23|400
0323-A05-saalary|Incoming|Salary| |03/23|3,500
1222-A2-carryjoint|Incoming|Carry over from Joint| |12/22|400

