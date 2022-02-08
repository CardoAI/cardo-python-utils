from datetime import date
from decimal import Decimal

import pytest

# DJANGO UTILS FIXTURES
from tests.testapp.models import Invoice, Company
from tests.utils import Dummy


@pytest.fixture()
def initial_invoices():
    for i in range(3):
        Invoice.objects.create(id=i + 1, code=f'T-{i}', amount=Decimal(str(i * 100)), issue_date=date(2021, 1, 1))


@pytest.fixture()
def initial_db_models_with_relations():
    c = Company.objects.create(id=1, name=f'C1')
    for i in range(3):
        Invoice.objects.create(id=i + 1, code=f'T-{i}', amount=Decimal(str(i * 100)), issue_date=date(2021, 1, 1),
                               company=c)


# FINDER CLASS FIXTURES
@pytest.fixture()
def initial_objects():
    data = [Dummy(i_number=i, text=f'T-{i}') for i in range(1, 6)]
    data.append(Dummy(i_number=6, text='T-6', child=Dummy(i_number=7, text='T-7')))
    return data
