from celery import Celery
from math import sqrt

app = Celery('cel', backend='redis://localhost:6379/0', broker='redis://localhost:6379/1')


@app.task
def square_root(value):
    return sqrt(value)
