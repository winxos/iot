from celery import Celery

app = Celery('cel', backend='redis://localhost:6379/0', broker='redis://localhost:6379/1')


def manage_sqrt_task(value):
    result = app.send_task('tasks.square_root', args=(value,))
    print(result.get())


if __name__ == '__main__':
    manage_sqrt_task(4)
