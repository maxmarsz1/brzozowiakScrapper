from django.db import models


class Offer(models.Model):
    path = models.URLField(max_length=255, unique=True)
    offer_id = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=255)
    price = models.IntegerField()
    image = models.URLField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    equipment = models.CharField(max_length=255, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    fuel = models.CharField(max_length=64, blank=True, null=True)
    hp = models.CharField(max_length=10, blank=True, null=True)
    color = models.CharField(max_length=64, blank=True, null=True)
    body = models.CharField(max_length=64, blank=True, null=True)
    transmission = models.CharField(max_length=64, blank=True, null=True)
    mileage = models.IntegerField(blank=True, null=True)
    capacity = models.CharField(max_length=10, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'
        ordering = ['-date']


class OfferFailed(models.Model):
    path = models.URLField(max_length=255, unique=True)
    error_message = models.TextField()

    def __str__(self):
        return f"Failed Offer: {self.path}"

    class Meta:
        verbose_name = 'Failed Offer'
        verbose_name_plural = 'Failed Offers'
        ordering = ['path']