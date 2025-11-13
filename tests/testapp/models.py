from django.db import models


class Invoice(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    code = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=40, decimal_places=20, null=True)
    f_amount = models.FloatField(null=True)
    tax = models.DecimalField(max_digits=40, decimal_places=20, default=5)
    issue_date = models.DateField()
    updated_at = models.DateField(null=True)
    company = models.ForeignKey('Company', null=True, on_delete=models.CASCADE,
                                help_text='company this invoice belongs to')
    active = models.BooleanField(default=True)
    history_info = models.JSONField(default=dict())
    created_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'test_invoice'

    def __str__(self):  # pragma no cover
        return f'{self.code}'


class Company(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'test_company'

    def __str__(self):  # pragma no cover
        return f'{self.name}'
