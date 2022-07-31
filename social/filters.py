import django_filters


class ListTitleFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        kwargs['data']._mutable = True
        if 'order' not in kwargs['data']:
            kwargs['data']['order'] = "-date_added"
        kwargs['data']._mutable = False
        super(ListTitleFilter, self).__init__(*args, **kwargs)

    order = django_filters.OrderingFilter(
        fields=(
            ("total_rating", "rating"),
            ("name", "name"),
            ("added", "date_added"),
            ("user_rating", "user_rating"),
        )
    )


class CommentsFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        kwargs['data']._mutable = True
        if 'order' not in kwargs['data']:
            kwargs['data']['order'] = "-date_added"
        kwargs['data']._mutable = False
        super(CommentsFilter, self).__init__(*args, **kwargs)

    order = django_filters.OrderingFilter(
        fields=(
            ("total_likes", "rating"),
            ("id", "date_added"),
        )
    )
