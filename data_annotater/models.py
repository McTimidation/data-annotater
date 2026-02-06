from django.db import models

class RetailRow(models.Model):
    class Segment(models.TextChoices):
        FIRST_PARTY = "FIRST_PARTY", "First Party"
        THIRD_PARTY = "THIRD_PARTY", "Third Party"

    merchant = models.CharField(max_length=100)
    sku = models.CharField(max_length=100)
    country = models.CharField(max_length=3)

    retailer = models.CharField(max_length=100, blank=True)
    segment = models.CharField(
        max_length=32,
        choices=Segment.choices,
        null=True,
        blank=True,
    )
    
    class Meta:
            constraints = [
                models.UniqueConstraint(
                    fields=["merchant", "sku", "country"],
                    name="uniq_merchant_sku_country",
                )
            ]