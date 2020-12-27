from django.http import JsonResponse
from django.views import View
from django.contrib.auth import get_user_model

from utils.functions import decode_jwt

User = get_user_model()

class APIView(View):
    @classmethod
    def raw_response(cls, content: dict, status: int = 200) -> JsonResponse:
        return JsonResponse(content, status=status)

    def response(self, data, message, status):
        return self.raw_response({'data': data, 'message': message, 'status': status}, status)

    def success(self, data=None, message='') -> JsonResponse:
        return self.response(data, message, 200)

    def fail(self, data=None, message='', status: int = 400) -> JsonResponse:
        return self.response(data, message, status)


class AuthAPIView(APIView):
    def dispatch(self, request, *args, **kwargs):

        token = request.META.get('HTTP_AUTHORIZATION', '')
        if len(token) > 7:
            data = decode_jwt(token[7:])
            try:
                request.user = User.objects.get(id=data['id'])
            except (User.DoesNotExist, TypeError):
                return self.fail('Invalid Auth')
        else:
            return self.fail('Invalid Auth')

        return super(AuthAPIView, self).dispatch(request, *args, **kwargs)
