from django.db import models

class Partner(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    logo = models.ImageField(upload_to='partners_logos/', verbose_name="Логотип", blank=True, null=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Наши клиенты"

    def __str__(self):
        return self.name