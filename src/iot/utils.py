import contextlib
import dataclasses
import datetime
from itertools import islice
from typing import Union

from openpyxl.cell import Cell

DATE_FORMAT = '%d-%m-%Y'


@dataclasses.dataclass
class Values:
    """
    Wraps a list of values from an excel file (either a row of columns, or
    column of rows) so that we can provide 'named access' to those values,
    e.g.

    >>> from collections import namedtuple
    >>> values = Values(['a', 'b', 'c'], [1, 2, 3])
    >>> values['a']
    1
    >>> values['d']
    Traceback (most recent call last):
      ...
    KeyError: 'd'

    It is possible to have duplicate keys, in which case slicing can be used
    to get the nth item (0 based) with a particular name, e.g.

    >>> values = Values(['a', 'a', 'a'], [10, 20, 30])
    >>> values['a', 2]
    30
    """

    fields: list
    values: list

    def get(self, field, default=None):
        try:
            return self[field]
        except KeyError:
            return default

    def __getitem__(self, field):
        """
        Get the item with the name field, if field is a tuple then the first
        item is the name of the field, the second item is the nth index to
        retrieve.
        """
        if isinstance(field, tuple):
            requested_field, nth = field
            matches = (
                i for i, field in enumerate(self.fields) if field == requested_field
            )
            matching_index = next(islice(matches, nth, nth + 1), None)
            if matching_index is not None:
                matching_value = self.values[matching_index]
                val = (
                    matching_value.value
                    if isinstance(matching_value, Cell)
                    else matching_value
                )
                return val.strip() if isinstance(val, str) else val
        else:
            # raise KeyError when field not present
            with contextlib.suppress(ValueError):
                matching_value = self.values[self.fields.index(field)]
                val = (
                    matching_value.value
                    if isinstance(matching_value, Cell)
                    else matching_value
                )
                return val.strip() if isinstance(val, str) else val

        # didn't return yet, then item could not be found
        raise KeyError(field)


def parse_date(value: Union[str, datetime.date, datetime.datetime]):
    """
    Parse a date value, it may be that the value came from loading an excel
    file in which case it will already be a date.
    """
    if isinstance(value, str):
        return datetime.datetime.strptime(value, DATE_FORMAT)
    elif isinstance(value, (datetime.date, datetime.datetime)):
        return value
    else:
        raise TypeError(
            f'Expected `str`, `date` or `datetime` instance got {type(value)}'
        )


def remove_all(relation):
    for entity in relation.all():
        relation.remove(entity)
