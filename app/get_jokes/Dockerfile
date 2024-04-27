FROM python:3.10

RUN pip install gunicorn

COPY get_jokes.py /

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "get_jokes:generate_joke_prompt"]