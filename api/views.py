import json
from decimal import Decimal
from django.views.generic import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model, authenticate
from api import models


@method_decorator(csrf_exempt, name='dispatch')
class RegistrationView(View):

    def post(self, request):
        error = None
        result = None
        try:
            body = json.loads(request.body.decode('utf8'))
            if not body['password']:
                raise Exception('Password can not be empty')
            currency = models.Currency.objects.get(name=body['currency'])
            User = get_user_model()
            user = User.objects.create_user(
                body['email'], body['password'], currency=currency, balance=Decimal(body['balance']))
        # except KeyError as e:
        #     error = f'KeyError: {e}'
        #     status = 400
        except Exception as e:
            error = str(e)
            status = 400
        else:
            result = user.balance
            status = 201
        return JsonResponse({'error': error, 'result': result}, status=status)


@method_decorator(csrf_exempt, name='dispatch')
class Auth(View):
    user = None
    body = None
    error = None
    result = None
    User = get_user_model()

    def dispatch(self, request, *args, **kwargs):
        try:
            body = json.loads(request.body.decode('utf8'))
            user = authenticate(email=body['email'], password=body['password'])
            if not user:
                raise Exception('Error Auth')
            self.user = user
            self.body = body
        # except KeyError as e:
        #     return JsonResponse({'error': str(e), 'result': None}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e), 'result': None}, status=401)
        else:
            return super().dispatch(request, *args, **kwargs)


class TransactionView(Auth):

    def post(self, request):
        try:
            amount = Decimal(self.body['amount'])
            if amount > self.user.balance:
                raise Exception('Not enough money')
            to_user = self.User.objects.get(email=self.body['to'])
            if self.user.currency == to_user.currency:
                self.user.balance -= amount
                to_user.balance += amount
                self.user.save()
                to_user.save()
            else:
                amount = amount
        except Exception as e:
            self.error = str(e)
            status = 400
        else:
            self.result = self.user.balance
            status = 200
        return JsonResponse({'error': self.error, 'result': self.result}, status=status)
