from django.db import models

# Create your models here.
class Node(models.Model):
    NODE_CHOICES = (
        (0, 'rec'),
        (1, 'Server'),
        (2, 'Task'),
    )
    STATUS_CHOICES = (
        (0, 'free'),
        (1, 'working'),
    )

    name = models.CharField(max_length=32,unique=True)
    IPaddress = models.CharField(max_length=32)
    port = models.CharField(max_length=32)
    #  keepalive = models.IntegerField(choices = NODE_CHOICES)
    keepalive = models.IntegerField(default=60)
    pid = models.IntegerField(default=-1)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)


# class Task(models.Model):
#     name = models.CharField(max_length=32)
#     task_info = models.CharField()
