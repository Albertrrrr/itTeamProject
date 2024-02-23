from django.db import models

# Create your models here.
class productCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()  # 使用 TextField 对应 VARCHAR(255) 是合适的，它没有长度限制

    def __str__(self):
        return self.name

