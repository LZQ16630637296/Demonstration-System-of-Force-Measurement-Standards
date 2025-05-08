from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.views.generic import TemplateView
from django.shortcuts import render

# Create your views here.
def test(request):
    return HttpResponse("HELLo")

def test_index(request, *args, **kwargs):
    return TemplateResponse(request, 'std_app/index.html')

# 使用函数试图
class TestIndex(TemplateView):
    template_name = 'std_app/index.html'

    #上下文处理
    def get_context_data(self, **kwargs):
        return {"word": 'hello oowd'}
