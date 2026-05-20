from django.db import models
import os

class CompressedFile(models.Model):
    original_file = models.FileField(upload_to='originals/')
    compressed_file = models.FileField(upload_to='compressed/', null=True, blank=True)
    original_size = models.BigIntegerField(null=True, blank=True)
    compressed_size = models.BigIntegerField(null=True, blank=True)
    file_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.original_file.name} (Compressed: {self.savings_percentage}%)"

    @property
    def savings_percentage(self):
        if self.original_size and self.compressed_size and self.original_size > 0:
            savings = 100 - (self.compressed_size / self.original_size * 100)
            return round(savings, 2)
        return 0
