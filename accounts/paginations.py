from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10                         # Standard page size
    page_size_query_param = 'page_size'    # Frontend က page_size=20 ဆိုပြီး စိတ်ကြိုက်တောင်းလို့ရအောင်
    max_page_size = 100                     # မလိုအပ်ဘဲ အများကြီး မတောင်းနိုင်အောင် ကန့်သတ်ချက်