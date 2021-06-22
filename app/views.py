from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import BookGenerationTask, TaskStatus
from .tasks import generate_book, task_progress


def start_book_generation(request):
    pages_count = int(request.GET.get('pages-count', '10'))
    in_color = int(request.GET.get('in-color', '0'))

    task = BookGenerationTask.objects.create(
        task_status=TaskStatus.IN_PROGRESS
    )

    celery_task_id, celery_group_id = generate_book(task.id, pages_count, bool(in_color))  # noqa

    task.celery_task_id = celery_task_id
    task.celery_group_id = celery_group_id
    task.save()

    return JsonResponse({
        'task_id': task.id
    })


def get_book(request, task_id):
    task = get_object_or_404(BookGenerationTask, pk=task_id)
    return JsonResponse({
        'task_id': task.id,
        'book': task.result_book
    })


def get_book_generation_status(request, task_id):
    task = get_object_or_404(BookGenerationTask, pk=task_id)
    if task.task_status in [TaskStatus.DONE_SUCCESS, TaskStatus.DONE_FAILED]:
        return JsonResponse({
            'task_id': task_id,
            'status': task.task_status
        })
    return JsonResponse({
        'task_id': task_id,
        'status': TaskStatus.IN_PROGRESS,
        'progress': task_progress(task.celery_group_id)  # нормализовать
    })
