from django.http import HttpResponse

def hello_view(request):
    return HttpResponse("Hello, this is a simple Django response!")