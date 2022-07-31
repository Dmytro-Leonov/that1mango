from .models import Title, Keyword, ReleaseFormat
from django.db.models import Q
import django_filters


class TitleFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        kwargs["data"]._mutable = True
        if "order" not in kwargs["data"]:
            kwargs["data"]["order"] = "-rating"
        kwargs["data"]._mutable = False
        super(TitleFilter, self).__init__(*args, **kwargs)

    name = django_filters.CharFilter(method="filter_by_all_name_fields")
    year = django_filters.RangeFilter(field_name="release_year")
    chapters = django_filters.RangeFilter()
    total_rating = django_filters.RangeFilter()
    age = django_filters.MultipleChoiceFilter(field_name="age_rating", choices=Title.TitleAgeRating.choices)
    type = django_filters.MultipleChoiceFilter(
        field_name="title_type", choices=Title.TitleType.choices, conjoined=False
    )
    status = django_filters.MultipleChoiceFilter(field_name="title_status", choices=Title.TitleStatus.choices)
    licensed = django_filters.BooleanFilter()

    rf = ReleaseFormat.objects.all()
    release_format = django_filters.filters.ModelMultipleChoiceFilter(
        field_name="release_format__slug",
        to_field_name="slug",
        queryset=rf
    )
    release_format_ex = django_filters.filters.ModelMultipleChoiceFilter(
        field_name="release_format__slug",
        to_field_name="slug",
        queryset=rf,
        exclude=True
    )

    kw = Keyword.objects.all()
    keyword = django_filters.filters.ModelMultipleChoiceFilter(
        field_name="keywords__slug",
        to_field_name="slug",
        queryset=kw,
        conjoined=True
    )
    keyword_ex = django_filters.filters.ModelMultipleChoiceFilter(
        field_name="keywords__slug",
        to_field_name="slug",
        queryset=kw,
        exclude=True
    )

    order = django_filters.OrderingFilter(
        fields=(
            ("total_rating", "rating"),
            ("name", "name"),
            ("date_added", "date_added"),
            ("chapter_count", "chapters"),
        ),

    )

    def filter_by_all_name_fields(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(english_name__icontains=value) | Q(alternative_names__icontains=value)
        )

    class Meta:
        model = Title
        fields = [
            "name", "year", "chapters", "total_rating", "age", "type", "status",
            "release_format", "release_format_ex", "keyword", "keyword_ex", "licensed"
        ]


class RelatedTitleFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        kwargs["data"]._mutable = True
        if "order" not in kwargs["data"]:
            kwargs["data"]["order"] = "-rating"
        kwargs["data"]._mutable = False
        super(RelatedTitleFilter, self).__init__(*args, **kwargs)

    order = django_filters.OrderingFilter(
        fields=(
            ("total_rating", "rating"),
            ("name", "name"),
            ("date_added", "date_added"),
            ("chapter_count", "chapters"),
        )
    )
