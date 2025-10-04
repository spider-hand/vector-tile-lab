import django_filters
from .models import Tileset
from .constants import TaskStatus


class TilesetFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(
        choices=[(status.value, status.name) for status in TaskStatus],
    )

    class Meta:
        model = Tileset
        fields = ["status"]
