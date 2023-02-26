from rest_framework.pagination import PageNumberPagination


class CustomPageSizeLimitPaginationClass(PageNumberPagination):
    page_size_query_param = "limit"
