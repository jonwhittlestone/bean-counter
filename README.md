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

## Resources

- Use Google Apps Script to make HTTP requests to trigger munge
  - https://stackoverflow.com/a/23917434

- Develop Lambdas Locally in VS Code using AWS SAM
  - https://www.youtube.com/watch?v=mhdX4znMd2Q

- Build a REST API using AWS Lambda and API Gateway
  - https://www.youtube.com/watch?v=4NY8nst45Rk

- Deploy FastAPI on AWS Lambda
  - https://www.youtube.com/watch?v=RGIM4JfsSk0
