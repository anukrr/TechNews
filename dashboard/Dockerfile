FROM python:latest

WORKDIR /dashboard

COPY . /dashboard

RUN pip3 install -r requirements.txt

RUN bash setup_nlp.sh

EXPOSE 8501

CMD ["streamlit", "run", "Homepage.py"]