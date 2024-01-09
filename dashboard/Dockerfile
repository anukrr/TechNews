FROM python:latest

WORKDIR /dashboard

COPY . /dashboard

RUN pip3 install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py"]