from rest_framework.pagination import PageNumberPagination


class CustomRecipePaginationClass(PageNumberPagination):
    page_size_query_param = "limit"
