from collections import defaultdict
from functools import wraps

from django.forms import Form
from django.http import JsonResponse
from django.core.exceptions import ValidationError as DjangoValidationError


# def endpoint():
#     def decorator(view_func):
#         @wraps(view_func)
#         def _wrapped_view(request, *args, **kwargs):
#             try:
#                 return view_func(request, *args, **kwargs)
#             except Exception as e:
#                 return JsonResponse({
#                     'message': str(e)
#                 }, status=500)
#
#         return _wrapped_view
#
#     return decorator

class DomainError(Exception): pass


class ValidationError(DomainError):
    def __init__(self):
        self.__error = []
        self.__attr_errors = defaultdict(list)

    def has_errors(self):
        return bool(self.__error or self.__attr_errors)

    def add_error(self, message: str, code: str = 'error'):
        self.__error.append({'code': code, 'message': message})

    def add_attr_error(self, attr: str, error: str):
        if not error:
            return
        self.__attr_errors[attr].append(error)

    def to_json(self):
        errors = []
        for error in self.__error:
            errors.append({
                'type': error['code'],
                'loc': [],
                'msg': error['message']
            })

        for attr, attr_errors in self.__attr_errors.items():
            for error in attr_errors:
                errors.append({
                    'type': 'error',
                    'loc': [attr],
                    'msg': error
                })

        return {
            'errors': errors
        }

    @staticmethod
    def from_django_validation_error(dj_error: DjangoValidationError):
        error = ValidationError()
        for attr, msg in dj_error.message_dict.items():
            if attr == '__all__':
                for m in msg:
                    error.add_error(m)
            else:
                for m in msg:
                    error.add_attr_error(attr, m)

        return error

    @staticmethod
    def from_django_form_error(form: Form):
        error = ValidationError()
        for field, err in form.errors.items():
            for e in err:
                error.add_attr_error(field, e)
        return error


def endpoint(view_func):
    def wrapped_view(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except ValidationError as e:
            return JsonResponse(e.to_json(), status=409)
        except DomainError as e:
            return JsonResponse({
                'message': str(e)
            })
        except DjangoValidationError as e:
            return JsonResponse(ValidationError.from_django_validation_error(e).to_json(), status=409)
        # except ValueError as e:
        #     return JsonResponse({
        #         'message': str(e)
        #     }, status=500)

    return wraps(view_func)(wrapped_view)
