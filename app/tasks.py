from time import sleep

from celery import chord, shared_task
from celery.result import GroupResult

from .models import BookGenerationTask, TaskStatus

TIME_FOR_COLOR_PAGE_SEC = 40
TIME_FOR_BLACKWHITE_PAGE_SEC = 20


@shared_task
def error_callback(*args, **kwargs):
    task_id = kwargs['task_id']
    task = BookGenerationTask.objects.get(pk=task_id)
    task.task_status = TaskStatus.DONE_FAILED
    task.save()
    # https://github.com/celery/celery/issues/3709


@shared_task
def success_callback(args, task_id):
    task = BookGenerationTask.objects.get(pk=task_id)
    book = '\n'.join(args)
    task.result_book = book
    task.task_status = TaskStatus.DONE_SUCCESS
    task.save()
    return book


@shared_task(autoretry_for=(ZeroDivisionError,),
             default_retry_delay=10,
             retry_kwargs={'max_retries': 3})
def generate_page(page_number, in_color=False):
    if in_color:
        required_time_sec = TIME_FOR_COLOR_PAGE_SEC
    else:
        required_time_sec = TIME_FOR_BLACKWHITE_PAGE_SEC
    sleep(required_time_sec)

    description = 'in color' if in_color else 'in b/w'

    # if page_number == 5:
    #     d = 1 / 0  # noqa

    return f'<page #{page_number} {description}>'


def generate_book(task_id, pages_count, in_color=False):
    group = [generate_page.s(n, in_color) for n in range(pages_count)]
    res = chord(group)(
        success_callback.s(task_id=task_id)
        .on_error(error_callback.s(task_id=task_id))
    )
    group_result = res.parent
    group_result.save()
    return res.id, group_result.id


def task_progress(group_id):
    gr = GroupResult.restore(group_id)
    # gr.ready()
    # gr.waiting()
    # gr.successful()
    # gr.failed()
    return gr.completed_count()
