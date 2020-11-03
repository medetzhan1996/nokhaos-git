from django import forms
from django.contrib.auth.models import User
from .models import Order, Сustomer, Profile, Integration


# Форма пользователя
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username', 'password', 'first_name', 'last_name', 'email'
        ]

        def __init__(self, request, *args, **kwargs):
            self.request = request
            super().__init__(*args, **kwargs)

        def save(self, commit=True):
            instance = super().save(commit=False)
            instance.company = self.request.user.profile.company
            if commit:
                instance.save()
            return instance


# Форма работника
class WorkerForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'phone_number', 'address', 'type', 'is_blocked'
        ]


# Форма заказа
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'product', 'count', 'payment', 'deadline_date', 'price'
        ]

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.seller = self.request.user
        instance.company = self.request.user.profile.company
        if commit:
            instance.save()
        return instance


# Форма клиента
class СustomerForm(forms.ModelForm):
    class Meta:
        model = Сustomer
        fields = [
            'login', 'phone_number', 'address', 'backup_phone_number'
        ]

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.company = self.request.user.profile.company
        if commit:
            instance.save()
        return instance


# Форма интеграции
class IntegrationForm(forms.ModelForm):
    class Meta:
        model = Integration
        fields = [
            'type', 'login', 'externalId',  'api_id', 'api_token'
        ]

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.company = self.request.user.profile.company
        if commit:
            instance.save()
        return instance