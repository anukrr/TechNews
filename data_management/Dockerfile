FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

COPY manage_records.py ${LAMBDA_TASK_ROOT}

CMD [ "manage_records.lambda_handler" ]
