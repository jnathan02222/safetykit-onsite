from django.db import models


# makemigrations migrate
# Create your models here.
class Example(models.Model):
    text = models.CharField(max_length=200)
    objects = models.Manager()


class PolicyViolation(models.Model):
    """Model to store policy violation analysis results."""

    url = models.URLField(max_length=500)
    title = models.CharField(max_length=500, blank=True)
    is_adderall_sold = models.BooleanField()
    appears_licensed_pharmacy = models.BooleanField()
    uses_visa = models.BooleanField()
    explanation = models.TextField()
    screenshot_path = models.CharField(max_length=500, blank=True)
    screenshots = models.JSONField(
        default=list, blank=True
    )  # Store list of base64 encoded screenshots
    analyzed_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        ordering = ["-analyzed_at"]

    def __str__(self):
        return f"{self.url} - Adderall: {self.is_adderall_sold}, Licensed: {self.appears_licensed_pharmacy}"
