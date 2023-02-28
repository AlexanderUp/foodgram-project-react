from django.db.models import Q, Value
from django.db.models.constants import LOOKUP_SEP
from rest_framework.filters import SearchFilter


class CustomOrderedIngredientSearchFilter(SearchFilter):

    def filter_queryset(self, request, queryset, view):
        if self.search_param not in request.query_params:
            return queryset

        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        queryset = queryset.order_by()

        search_istartswith = []
        for search_field in search_fields:  # type:ignore
            orm_lookup = LOOKUP_SEP.join((f"{search_field}", "istartswith"))
            search_istartswith_intermediate_list = [
                Q(**{orm_lookup: term}) for term in search_terms]
            search_istartswith.extend(search_istartswith_intermediate_list)

        query_istartswith = (queryset.filter(*search_istartswith)
                                     .annotate(order_field=Value(1)))

        search_icontains = []
        for search_field in search_fields:  # type:ignore
            orm_lookup = LOOKUP_SEP.join((f"{search_field}", "icontains"))
            search_icontains_intermediate_list = [
                Q(**{orm_lookup: term}) for term in search_terms]
            search_icontains.extend(search_icontains_intermediate_list)

        query_icontains = (queryset.filter(*search_icontains)
                                   .exclude(*search_istartswith)
                                   .annotate(order_field=Value(2)))
        return query_istartswith.union(query_icontains).order_by(
            "order_field", "name",
        )
