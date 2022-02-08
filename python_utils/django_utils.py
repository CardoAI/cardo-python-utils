import logging
import sys
import time
from typing import Dict, Union, Optional, IO, TypeVar
from typing import List, Any
from typing import Tuple

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Model
from django.db.models import Sum, Min, Avg, Max, Subquery, Case, When, ExpressionWrapper, F
from django.db.models.fields.files import FieldFile
from django.forms import model_to_dict
from django.utils import timezone

from python_utils.imports import import_optional_dependency
from python_utils.db import fetch_all

Model_T = TypeVar('Model_T', bound=Model)


class ExtendedEncoder(DjangoJSONEncoder):  # pragma no cover
    """Custom JSON Encoder that processes fields like date etc."""

    def default(self, o):
        if isinstance(o, Model):
            return model_to_dict(o)
        elif isinstance(o, FieldFile):
            return o.name
        return super().default(o)


def record_to_dict(record: Model_T, exclude: List = None) -> Dict:
    """
    Transform a django record to a dict.

    Args:
        record: django object to be transformed to dict
        exclude: list of keys/fields to exclude in the final dict
    Returns:
        dict with model's field:value pairs
    """

    if exclude is None:
        exclude = []

    initial_data = {
        key: value
        for key, value in record.__dict__.items() if not (key.startswith('_') or key in exclude)
    }

    # Replace choices with their human representation
    for field, value in initial_data.items():
        if value is None:
            continue

        if get_field_display := getattr(record, f'get_{field}_display', None):
            initial_data[field] = get_field_display()

    return initial_data


def get_choices_list_and_dict(choices) -> Tuple[List, Dict]:
    """
    From a Choices object return a list and dict of these choices.
    Args:
        choices: Choices object to get the representations from
    Returns:
        tuple of list with human_value and dict-> {human_value: value}
    Examples:
        >>> from model_utils import Choices
        >>> get_choices_list_and_dict(Choices((1, 'hello', 'HELLO')))
        ([('HELLO', 'HELLO')], {'HELLO': 1})
    """
    import_optional_dependency('model_utils', dependency='django-model-utils')

    choices_list = [(human_value, human_value) for _, human_value in choices]
    choices_dict = {human_value: value for value, human_value in choices}
    return choices_list, choices_dict


def perform_query(
        sql_query: str,
        params: Optional[List] = None,
        expected_results=True,
) -> Optional[List[Dict]]:
    """
    Execute a sql statement to the database and get the results as a list of dict or None
    if no result is expected

    Args:
        sql_query: string representing the query to be executed
        params: list with params to be passed to the query
        expected_results: indicating whether the query executed will return or not results
    Returns:
        List of dict with the fetched records or None if expected_result=False
    """
    from django.db import connection

    with connection.cursor() as cursor:
        if params:
            cursor.execute(sql_query, tuple(params))
        else:
            cursor.execute(sql_query)
        if expected_results:
            return fetch_all(cursor)


def get_total(records: models.QuerySet, aggregation_field: str) -> Optional[int]:
    """
    Calculate the total value of the aggregation field for the provided records

    Args:
        records: queryset with the records to get the total sum of the passed field
        aggregation_field: string representing the field we want to get the sum of
    Returns:
        Total sum of the field or None if all values of field are empty or empty queryset
    """
    return records.aggregate(total=Sum(aggregation_field)).get("total")


def get_min(records: models.QuerySet, aggregation_field: str) -> Optional[int]:
    """
    Calculate the min value of the aggregation field for the provided records

    Args:
        records: queryset with the records to get the min value of the passed field
        aggregation_field: string representing the field we want to get the min value of
    Returns:
        Min value found of the field or None if all values of field are empty or empty queryset
    """
    return records.aggregate(min=Min(aggregation_field)).get("min")


def get_average(records: models.QuerySet, aggregation_field: str) -> Optional[int]:
    """
    Calculate the average value of the aggregation field for the provided records
    Args:
        records: queryset with the records to get the average of the passed field
        aggregation_field: string representing the field we want to get the average of
    Returns:
        Average of the field or None if all values of field are empty or empty queryset
    """
    return records.aggregate(avg=Avg(aggregation_field)).get("avg")


def get_max(records: models.QuerySet, aggregation_field: str) -> Optional[int]:
    """
    Calculate the max value of the aggregation field for the provided records

    Args:
        records: queryset with the records to get the max of the passed field
        aggregation_field: string representing the field we want to get the max of
    Returns:
        Max of the field or None if all values of field are empty or empty queryset
    """
    return records.aggregate(max=Max(aggregation_field)).get('max')


def compute_weighted_average(
        records: models.QuerySet,
        field: str,
        weight: str = "amount",
        is_field_subquery=False,
        is_weight_subquery=False,
        output=models.FloatField,
) -> models.QuerySet:
    field = Subquery(field) if is_field_subquery else F(field)
    weight = Subquery(weight) if is_weight_subquery else F(weight)
    return records.aggregate(
        weight_sum=Sum(weight),
        average=Case(
            When(weight_sum=0, then=0),
            default=ExpressionWrapper(
                Sum(field * weight) / Sum(weight), output_field=output()
            ),
            output_field=output(),
        ),
    ).get("average")


def compute_grouped_weighted_average(
        records: models.QuerySet,
        group_by: List[str],
        field: str,
        weight: str = "amount",
        label: str = "avg",
        output=models.FloatField
) -> models.QuerySet:
    annotation = {
        label: ExpressionWrapper(
            Sum(F(field) * F(weight)) / Sum(F(weight)), output_field=output()
        )
    }
    return records.values(*group_by).annotate(**annotation)


def compute_grouped_weighted_average_subquery(
        records: models.QuerySet,
        group_by: List[str],
        field_subquery: Subquery,
        weight_subquery: Subquery,
        label: str = "avg",
        output=models.FloatField,
) -> models.QuerySet:
    annotation = {
        label: ExpressionWrapper(
            Sum(field_subquery * weight_subquery) / Sum(weight_subquery),
            output_field=output()
        )
    }
    return records.values(*group_by).annotate(**annotation)


def update_record(record: Model_T, save=True, **data) -> Model_T:
    """
    Update a record with given attributes and return it.
    If save=True also commit to the database the record with the changes

    Args:
        record: db record to be updated
        save: flag whether to save the record
        **data: data to be changed mapped with the record fields as kwargs
    Returns:
        New updated record
    """
    if data:
        for key, value in data.items():
            setattr(record, key, value)
        if save:
            record.save()
    return record


def get_choice_value(choices, human_string: str) -> Optional[Union[int, str]]:
    """
    Get database representation of a choice for a human-readable value

    Args:
        choices: model_utils Choice object to get the db value from
        human_string: string representing the human-readable value
    Returns:
        db representation of choice field
    """

    import_optional_dependency('model_utils', dependency='django-model-utils')

    for value, representation in choices:
        if representation == human_string:
            return value
    return None


def get_or_none(records: models.QuerySet, *args, **kwargs) -> Optional[Model_T]:
    """
    Wrapper around queryset.get to return None if no record is found

    Args:
        records: queryset of objects to get() from
        *args: args to be passed to get() method
        **kwargs: kwargs to be passed to get() method
    Returns:
        record object if found or None
    """
    try:
        return records.get(*args, **kwargs)
    except ObjectDoesNotExist:
        return None


def ids(queryset: models.QuerySet, attr='id') -> List[Any]:
    """
    Given a queryset and an attr, get all distinct values of the attr as a list

    Args:
        queryset: queryset with the objects we want to get the data from
        attr: string representing the field of the model we want to get the distinct values
    Returns:
        List of distinct values
    Examples:
        ids(Invoice.objects.filter(id__gt=50), 'id') \n
        [51, 52, 53, 54, 55 ...]
    """
    return list(queryset.order_by(attr).values_list(attr, flat=True).distinct())


def get_field_config(field: models.Field) -> Dict:
    """
    Get the configuration of a Django field, in the form: {'name': ..., 'type': ..., 'choices': ..., 'description: ...}
    Available types are ["string", "integer", "float", "amount", "datetime", "date", "selection"]
    selection type is used when the value of the field supports choices or when it is a foreign key.
    When the type is selection, the config of the field is in the form
    {
        "type": "selection",
        "choices": [{"id": 1, "name": "Choice"}]
    }

    Args:
        field: The field for which the config is required
    Returns:
        The config of the field.
    """

    field_type = None
    choices = None

    if getattr(field, "choices", None):
        field_type = "selection"
        choices = [{"id": value, "name": label} for value, label in field.choices]
    elif isinstance(field, models.ForeignKey):
        field_type = "selection"
        choices = [
            {"id": record.id, "name": record.name}
            for record in field.related_model.objects.all()
        ]

    elif isinstance(field, (models.CharField, models.TextField)):
        field_type = "string"
    elif isinstance(field, models.IntegerField):
        field_type = "integer"
    elif isinstance(field, models.FloatField):
        field_type = "float"
    elif isinstance(field, models.DecimalField):
        field_type = "amount"
    elif isinstance(field, models.DateTimeField):
        field_type = "datetime"
    elif isinstance(field, models.DateField):
        field_type = "date"
    elif isinstance(field, models.JSONField):
        field_type = "json"
    elif isinstance(field, models.BooleanField):
        field_type = "bool"

    field_config = {
        "name": field.name,
        "type": field_type,
        "description": field.help_text if hasattr(field, "help_text") else "",
    }
    if choices:
        field_config["choices"] = choices

    return field_config


def get_model_fields_config(
        model: models.Model.__class__, excluded_fields: List[str] = None, read_only_fields: List[str] = None
) -> List[Dict]:
    """
    Get the configurations for the fields of a model.

    Args:
        model: The model for which the fields config is required
        excluded_fields: A list of field names which should be excluded
        read_only_fields: A list of field names which should be considered as read_only
    Returns:
        A List of dictionaries which represent the field configurations
    """

    if not excluded_fields:
        excluded_fields = []
    if not read_only_fields:
        read_only_fields = []

    fields_config = []

    # Process all fields that can contain values
    for field in [
        field for field in model._meta.get_fields() if field.name not in excluded_fields
    ]:
        field_config = get_field_config(field)
        field_config["input"] = field.name not in read_only_fields
        fields_config.append(field_config)

    return fields_config


def get_fields_config_and_values(
        record: models.Model,
        excluded_fields: List[str] = None,
        read_only_fields: List[str] = None
) -> List[Dict]:
    fields_config = get_model_fields_config(
        type(record), excluded_fields, read_only_fields
    )

    # Add value for each field
    for field_config in fields_config:
        value = getattr(record, field_config["name"])
        if isinstance(value, models.Model):
            value = value.id
        field_config["value"] = value

    return fields_config


def get_model_field_names(model: Union[models.Model.__class__, Model_T]) -> List[str]:
    """
    Iterate over a model fields and return a list of them

    Args:
        model: model object to iterate over and get fields
    Returns:
        list[str] of all the fields
    Examples:
        Invoice:
            code=models.CharField(max_length=100) \n
            amount=models.Integer() \n

        get_model_field_names(Invoice) \n
        [id, code, amount]
    """
    return [field.name for field in model._meta.get_fields()]


def safe_bulk_create(
        model: models.Model.__class__,
        records: List[Model_T],
        refresh_fields: List[str] = None,
        batch_size: int = 500
):
    """
    Given a model and a list of records, bulk_create them and also set the
    refresh fields (foreign keys) if any.

    Args:
        model: The Model to which the records belong
        records: list of objects to be commited to the database
        refresh_fields: list with foreign keys to be updated
        batch_size: how many records we want to insert with a single query
    """
    if not records:
        return

    if refresh_fields:
        for record in records:
            for field in refresh_fields:
                try:
                    setattr(record, f"{field}_id", getattr(record, field).id)
                except AttributeError:
                    continue

    model.objects.bulk_create(records, batch_size=batch_size)


def safe_bulk_update(
        model: models.Model.__class__,
        records: List[Model_T],
        fields: List[str],
        batch_size: int = 500,
        refresh_fields: List[str] = None,
        updated_at_field: str = 'updated_at'
):
    """
    Given a model and a list of records, bulk_update them and also set the
    refresh fields (foreign keys) if any. Supports auto now fields to be updated as well

    Args:
        model: Model.__class__ obj
        records: list of records to be created
        fields: list of fields needed to be updated
        refresh_fields: list with foreign keys to be updated
        batch_size: how many records we want to insert with a single query
        updated_at_field: field datetime/date repr updated at moment
    """
    if not records:
        return

    if refresh_fields:
        for record in records:
            for field in refresh_fields:
                try:
                    setattr(record, f"{field}_id", getattr(record, field).id)
                except AttributeError:
                    continue

    # Auto now fields are not updated automatically in bulk operations.
    if hasattr(model, updated_at_field) and (updated_at_field not in fields):
        # This kind of update supports both `set` and `list`
        fields = [*fields, updated_at_field]
        timestamp = timezone.now()
        for record in records:
            setattr(record, updated_at_field, timestamp)
    model.objects.bulk_update(records, fields, batch_size=batch_size)


logger = logging.getLogger(__name__)


def call_procedure(procedure_name: str, params: List[Any] = None):
    """
    Execute an SQL procedure in the db.

    Args:
        procedure_name: the name of the procedure to be executed
        params: list of the parameters to pass to the procedure
    """
    temp_time = time.time()
    logger.info(f"Started Procedure {procedure_name}")
    query = f"call {procedure_name}"
    if params:
        query += f"({(',%s' * len(params))[1:]});"
    else:
        query += "();"
    perform_query(
        sql_query=query,
        params=params,
        expected_results=False
    )
    logger.info(f"Finished Procedure {procedure_name} in {time.time() - temp_time}")


def get_id_field_map(queryset: models.QuerySet, field: str) -> Dict[int, Any]:
    """
    Given a queryset get a mapping of the form \n
    {
        <id>: <field>, \n
        ...
    }

    Args:
        queryset:   Django models.QuerySet Instance
        field:      Field that needs to be mapped, for ex. `name`, `identifier`, etc.
    Returns:
        Mapping with ids as keys and the given field as values.
    """
    return {
        record[0]: record[1]
        for record in queryset.values_list('id', field)
    }


def generate_file_from_buffer(file_buffer_io: IO[str], content_type: str, filename="file", encoding=None):
    field_type = 'FileField'
    size = sys.getsizeof(file_buffer_io)
    return InMemoryUploadedFile(file_buffer_io, field_type, filename, content_type, size, encoding)
