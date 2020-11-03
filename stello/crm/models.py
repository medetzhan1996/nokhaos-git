from django.db import models
from django.conf import settings


# Базовый абстрактный класс
class ItemBase(models.Model):
    title = models.CharField(max_length=180)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


# Список компании
class Сompany(ItemBase):
    pass

    class Meta:
        db_table = "companies"


# Расширенный модель пользователя
class Profile(models.Model):
    TYPE_CHOICES = (
        (1, "Управляющий компанией"),
        (2, "Главный менеджер"),
        (3, "Менеджер"),
        (4, "Бухгалтер"),
        (5, "Курьер"),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                primary_key=True)
    company = models.ForeignKey(
        Сompany, related_name='profiles_company',
        on_delete=models.CASCADE)
    type = models.IntegerField(default=1, choices=TYPE_CHOICES, null=True)
    phone_number = models.CharField(max_length=18, blank=True)
    address = models.CharField(max_length=280, blank=True)
    is_blocked = models.BooleanField(default=False)
    last_lead = models.DateTimeField(auto_now_add=True)


# Список клиентов
class Сustomer(models.Model):
    TYPE_CHOICES = (
        ("instagramV2", "Instagram direct"),
        ("instagramVOff", "комментарии Instagram"),
        ("whatsapp", "Whatsapp"),
        ("whatsapp2", "Whatsapp Enterprise"),
    )
    company = models.ForeignKey(
        Сompany, related_name='customers_company',
        on_delete=models.CASCADE)
    address = models.CharField(max_length=180, blank=True)
    login = models.CharField(max_length=180)
    type = models.CharField(max_length=80, choices=TYPE_CHOICES, null=True)
    avatar = models.URLField(max_length=380, null=True)
    phone_number = models.CharField(max_length=18, blank=True)
    backup_phone_number = models.CharField(max_length=18, blank=True)
    customer_id = models.IntegerField(null=True)
    social_id = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "customers"

    def __str__(self):
        return self.login


# Список заказов
class Order(models.Model):
    PAYMENT_CHOICES = (
        (1, "Полная оплата"),
        (2, "Предварительная оплата"),
        (3, "Оплата при доставке")
    )
    company = models.ForeignKey(
        Сompany, related_name='orders_company',
        on_delete=models.CASCADE)
    customer = models.ForeignKey(
        Сustomer, related_name='order_customers',
        on_delete=models.CASCADE)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(max_digits=19, decimal_places=0)
    product = models.CharField(max_length=180)
    count = models.IntegerField(default=1)
    deadline_date = models.DateField(null=True)
    payment = models.IntegerField(choices=PAYMENT_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"


# Список интеграции с соц. мессен.
class Integration(ItemBase):
    TYPE_CHOICES = (
        ("instagramV2", "Instagram direct"),
        ("instagramVOff", "комментарии Instagram"),
        ("whatsapp", "Whatsapp"),
        ("whatsapp2", "Whatsapp Enterprise"),
    )
    TYPE_STATUS = (
        ("active", "Активный"),
        ("blocked", "Блокированный")
    )
    type = models.CharField(max_length=80, choices=TYPE_CHOICES)
    login = models.CharField(max_length=180)
    avatar = models.URLField(max_length=380, null=True, blank=True)
    externalId = models.CharField(max_length=180, null=True)
    api_id = models.IntegerField(blank=True, null=True)
    api_token = models.CharField(max_length=180, null=True)
    status = models.CharField(max_length=12, choices=TYPE_STATUS,
        default="active")
    managers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    company = models.ForeignKey(
        Сompany, related_name='integration_companies',
        on_delete=models.CASCADE, blank=True, null=True)
    customers = models.ManyToManyField(
        Сustomer, related_name='integrations_customers',
        blank=True, null=True)

    class Meta:
        db_table = "integrations"

    def __str__(self):
        return self.login


# Статус заказа
class LeadStatus(models.Model):
    title = models.CharField(max_length=180)
    companies = models.ManyToManyField(
        Сompany, through='CompanyLeadStatus', symmetrical=False)

    class Meta:
        db_table = "lead_status"

    def __str__(self):
        return self.title


# Воронка компании
class CompanyLeadStatus(models.Model):
    lead_status = models.ForeignKey(LeadStatus, related_name='lead_status_rel',
                                    on_delete=models.CASCADE)
    company = models.ForeignKey(Сompany, related_name='company_rel',
                                on_delete=models.CASCADE)


# Список обращении
class Lead(models.Model):
    lead_id = models.IntegerField(null=True)
    read = models.BooleanField(default=False)
    company = models.ForeignKey(
        Сompany, related_name='leads_company',
        on_delete=models.CASCADE)
    integration = models.ForeignKey(
        Integration, related_name='leads_integration',
        on_delete=models.CASCADE)
    customer = models.ForeignKey(
        Сustomer, related_name='leads_customer',
        on_delete=models.CASCADE)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True
    )
    status = models.ForeignKey(LeadStatus, related_name='leads_status',
                               on_delete=models.CASCADE, null=True, blank=True)
    message_unread = models.IntegerField(default=0)
    real_id = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "leads"
