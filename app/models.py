from django.db import models


class TaskStatus(models.TextChoices):
    IN_PROGRESS = 'IN_PROGRESS'
    DONE_SUCCESS = 'DONE_SUCCESS'
    DONE_FAILED = 'DONE_FAILED'


class BookGenerationTask(models.Model):
    task_status = models.CharField(
        max_length=16,
        choices=TaskStatus.choices
    )
    celery_task_id = models.UUIDField(
        blank=True,
        null=True
    )
    celery_group_id = models.UUIDField(
        blank=True,
        null=True
    )
    result_book = models.TextField(
        blank=True
    )
