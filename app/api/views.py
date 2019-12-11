import json
from decimal import Decimal
from django.views.generic import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
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
        except KeyError as e:
            error = f'{e} required'
            status = 400
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
    settings = None

    def dispatch(self, request, *args, **kwargs):
        self.settings = models.Settings.get_settings()
        if not self.settings.base_ready:
            return JsonResponse({'error': 'Try again later', 'result': None}, status=500)
        try:
            body = json.loads(request.body.decode('utf8'))
            user = authenticate(email=body['email'], password=body['password'])
            if not user:
                raise Exception('Error Auth')
            self.user = user
            self.body = body
        except KeyError as e:
            return JsonResponse({'error': f'{e} required', 'result': None}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e), 'result': None}, status=401)
        else:
            return super().dispatch(request, *args, **kwargs)


class TransactionView(Auth):

    def get(self, request):
        transaction_qset = models.Transaction.objects.filter(Q(user_from=self.user) | Q(user_to=self.user))
        self.result = [{
            'from': transaction.user_from.email,
            'to': transaction.user_to.email,
            'amount_from': transaction.amount_from,
            'amount_to': transaction.amount_to,
            'currency_from': transaction.user_from.currency.name,
            'currency_to': transaction.user_to.currency.name,
        } for transaction in transaction_qset]
        return JsonResponse({'error': self.error, 'result': self.result})

    def post(self, request):
        try:
            amount = Decimal(self.body['amount'])
            if amount > self.user.balance:
                raise Exception('Not enough money')
            user_to = self.User.objects.get(email=self.body['to'])
            if not self.user.currency or not user_to.currency:
                raise Exception('User currency not selected')
            if self.user.currency == user_to.currency:
                amount_to = amount
            else:
                amount_main = amount * self.user.currency.rate
                amount_to = amount_main / user_to.currency.rate
            transaction = models.Transaction.make_transaction(self.user, user_to, amount, amount_to)
        except KeyError as e:
            self.error = f'{e} required'
            status = 400
        except Exception as e:
            self.error = str(e)
            status = 400
        else:
            self.result = transaction.amount_to
            status = 200
        return JsonResponse({'error': self.error, 'result': self.result}, status=status)
