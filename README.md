# bean-counter

This experimental project aims to answer simple financial questions from the household budget.

- Munge the Google Budget spreadsheets to a single CSV
- Use Sketch to generate Python code to run analysis and plots

## Usage

Run the development server:

```bash
uvicorn src.bean_counter.main:app --port 7998 --reload
```

### Run

To ingest all costs from the Family Google Sheets, run with `httpie`:

```bash
http POST http://127.0.0.1:7998/run
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

- Using FastAPI with AWS SAM the Easy Way!

  - https://www.sensibledefaults.io/blog/fastapi-mangum-aws-sam/index

- Deploy FastAPI on AWS Lambda
  - https://www.youtube.com/watch?v=RGIM4JfsSk0

## AWS Lambda

If you have the credentials, run mine:

- https://ixbcimiswyj7g3yp2q2k7d3lgy0dwexa.lambda-url.eu-west-2.on.aws

After installation/credentials set up AWS CLI v2:

- ```bash
  aws lambda list-functions
  ```

### To manually create and run Lambda in Management Console

> Already created the Lambda and need to update it?
>
> `bash make update-lambda`

1. Get Python 3.10 packages (see ./aws/3.10-requirements.txt)

2. Create zip file `lambda_function.zip`:

   ```bash
   pip install -t lib -r 3.10-requirements.txt

   (cd lib; zip ../lambda_function.zip -r .)

   (cd src/bean_counter; zip ../../lambda_function.zip -u main.py; zip ../../lambda_function.zip -u .env; cd -)

   zip lambda_function.zip -r config

   ```

3. Upload it to S3 with:

   ```bash
   aws s3 cp lambda_function.zip s3://projects-bean-counter/lambda_function.zip
   ```

4. Create the Lambda function:

5. Upload by giving it S3 address

   ```bash
   aws lambda update-function-code --function-name bean-counter --s3-bucket projects-bean-counter --s3-key lambda_function.zip
   ```

6. Tweak Configuration (Memory, Timeout)

7. Deactivate/Reactivate (Optional)

   Deactivate:

   ```bash
   aws lambda put-function-concurrency --function-name bean-counter --reserved-concurrent-executions 0
   ```

   Reactivate:

   ```
   aws lambda put-function-concurrency --function-name bean-counter --reserved-concurrent-executions 10
   ```

## Sample summary gsheet

> Generated from https://jakebathman.github.io/Markdown-Table-Generator/

| **Direction** |       **Name**        | **Category** | **Date** | **GBP** |
| :-----------: | :-------------------: | :----------: | :------: | :-----: |
|   Outgoing    |        Petrol         |              |  05/23   |   400   |
|   Incoming    |        Salary         |              |  03/23   |  3,500  |
|   Incoming    | Carry over from Joint |              |  12/22   |   400   |
