from django.http                import (HttpResponse, HttpResponseBadRequest, 
                                        HttpResponseForbidden)
from django.utils.decorators    import method_decorator
from django.utils.timezone      import now
from django.views               import View
from django.views.decorators.csrf import csrf_exempt

from .models    import LoginRecord, LoginRecordToken
from .forms     import LoginRecordForm


@method_decorator(csrf_exempt, name='dispatch')
class LoginRecordView(View):
    def post(self, request):
        try:
            lrt = LoginRecordToken.objects.get(
                token=request.POST.get('token',''), expires__gt=now()
            )
            lrt.last_used = now()
            lrt.save()
        except models.ObjectDoesNotExist as e:
            return HttpResponseForbidden()

        form = LoginRecordForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest()
        form.save()
        return HttpResponse()

