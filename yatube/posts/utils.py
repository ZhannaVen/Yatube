from django.conf import settings
from django.core.paginator import Paginator


def paginator_yatube(request, post_list):
    paginator = Paginator(post_list, settings.NUM)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
