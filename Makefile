.SILENT:


.PHONY: update-lambda
SHELL := /bin/bash

update-lambda:
	(cd src/bean_counter; zip ../../lambda_function.zip -u main.py; zip ../../lambda_function.zip -u .env; cd -);aws s3 cp lambda_function.zip s3://projects-bean-counter/lambda_function.zip;aws lambda update-function-code --function-name bean-counter --s3-bucket projects-bean-counter --s3-key lambda_function.zip