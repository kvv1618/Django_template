from django.db import models

# Create your models here.


class File(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='files/')



    def __str__(self):
        return self.file.name


class Classroom(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.CASCADE,
        related_name='owner'
    )

    files = models.ManyToManyField(File, related_name='classroom')

    students = models.ManyToManyField(
        'authentication.CustomUser',
        related_name='classrooms'
    )

    def __str__(self):
        return self.name
