from django.db.models import Q

def search_queryset(queryset, search_fields=None, search_term=None):
    """
    Search a queryset using the given search_term and search_fields.
    """
    if search_term and search_fields:
        search_term = search_term.lower().split(" ")
        query = Q()
        for field in search_fields:
            for term in search_term:
                query |= Q(**{f"{field}__icontains": term})
        return queryset.filter(query)
    return queryset