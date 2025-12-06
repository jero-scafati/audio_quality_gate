from django.db import models

class AudioAnalysis(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    is_multispeaker = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"Audio {self.id} - Processed: {self.processed}"

class AuditLog(models.Model):
    id = models.AutoField(primary_key=True)
    audio_ref_id = models.IntegerField(help_text="ID del audio original")
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log {self.id}: Audio {self.audio_ref_id} rejected"