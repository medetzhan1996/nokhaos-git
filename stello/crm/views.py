from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateResponseMixin, View
from django.contrib.auth.models import User
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from .models import Profile, Integration, Order, Сustomer, Lead
from .forms import WorkerForm, UserForm, IntegrationForm,\
    OrderForm, СustomerForm


class WorkerMixin(LoginRequiredMixin, TemplateResponseMixin, View):
    worker_form_class = WorkerForm
    user_form_class = UserForm

    def get_workers(self, request, company):
        workers = User.objects.filter(profile__company=company).all()
        return workers

    def integ_account_save(self, request, user_save):
        accounts = request.POST.getlist('integration_account')
        user_save.integration_set.clear()
        for account in accounts:
            integration = Integration.objects.get(pk=account)
            integration.managers.add(user_save)
        return True


# Страница списка работников
class WorkerListView(WorkerMixin):
    template_name = 'crm/worker/list.html'

    def get(self, request, *args, **kwargs):
        company = self.request.user.profile.company
        workers = self.get_workers(request, company)
        return self.render_to_response({'workers': workers})


# Страница детальной информации работника
class WorkerUpdateView(WorkerMixin):
    template_name = 'crm/worker/form.html'

    def dispatch(self, *args, **kwargs):
        worker_id = self.kwargs.get('worker_id')
        company = self.request.user.profile.company
        self.workers = self.get_workers(self.request, company)
        self.worker = get_object_or_404(
            User, pk=worker_id)
        self.profile = get_object_or_404(Profile, user=self.worker)
        self.integrations = Integration.objects.filter(
            company=company).all()
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        worker_form = self.worker_form_class(instance=self.profile)
        user_form = self.user_form_class(instance=self.worker)
        return self.render_to_response({
            'workers': self.workers, 'worker': self.worker,
            'worker_form': worker_form, 'user_form': user_form,
            'integrations': self.integrations})

    def post(self, request, *args, **kwargs):
        worker_form = self.worker_form_class(
            request.POST, instance=self.profile)
        user_form = self.user_form_class(
            request.POST, instance=self.worker)
        if worker_form.is_valid() and user_form.is_valid():
            worker_form.save()
            user_save = user_form.save()
            self.integ_account_save(request, user_save)
            return redirect('crm:worker_update', user_save.id)
        return self.render_to_response({
            'workers': self.workers, 'worker': self.worker,
            'worker_form': worker_form, 'user_form': user_form,
            'integrations': self.integrations})


# Создать нового работника компании
class WorkerCreateView(WorkerMixin):
    template_name = 'crm/worker/form.html'

    def dispatch(self, *args, **kwargs):
        self.company = self.request.user.profile.company
        self.workers = self.get_workers(self.request, self.company)
        self.integrations = Integration.objects.filter(
            company=self.company).all()
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        worker_form = self.worker_form_class()
        user_form = self.user_form_class()
        return self.render_to_response({
            'workers': self.workers, 'integrations': self.integrations,
            'worker_form': worker_form, 'user_form': user_form
        })

    def post(self, request, *args, **kwargs):
        worker_form = self.worker_form_class(request.POST)
        user_form = self.user_form_class(request.POST)
        if worker_form.is_valid() and user_form.is_valid():
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            new_user = User.objects.create_user(
                username, email, password,
                first_name=first_name,
                last_name=last_name,
            )
            worker_form_save = worker_form.save(commit=False)
            worker_form_save.user = new_user
            worker_form_save.company = self.company
            worker_form_save.save()
            self.integ_account_save(request, new_user)
            return redirect('crm:worker_update', new_user.id)
        return self.render_to_response({
            'workers': self.workers, 'worker_form': worker_form,
            'user_form': user_form, 'integrations': self.integrations})


class OrderMixin(LoginRequiredMixin, TemplateResponseMixin, View):
    order_form_class = OrderForm
    customer_form_class = СustomerForm

    def get_customers(self, request, company):
        customers = Order.objects.filter(
            company=company).distinct('customer').all()
        return customers


# Страница списка работников
class OrderListView(OrderMixin):
    template_name = 'crm/order/list.html'

    def get(self, request, *args, **kwargs):
        company = self.request.user.profile.company
        self.customers = self.get_customers(request, company)
        return self.render_to_response({'customers': self.customers})


# Страница списка работников
class OrderDetailView(OrderMixin):
    template_name = 'crm/order/detail.html'

    def dispatch(self, *args, **kwargs):
        customer_id = self.kwargs.get('customer_id')
        self.company = self.request.user.profile.company
        self.customers = self.get_customers(self.request, self.company)
        self.customer = get_object_or_404(
            Сustomer, pk=customer_id, company=self.company)
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        orders = Order.objects.filter(customer=self.customer).all()
        customer_form = self.customer_form_class(
            request, instance=self.customer)
        order_form = self.order_form_class(request)
        return self.render_to_response({
            'customer': self.customer, 'customers': self.customers,
            'orders': orders, 'customer_form': customer_form,
            'order_form': order_form})

    def post(self, request, *args, **kwargs):
        order_form = self.order_form_class(request, data=request.POST)
        if order_form.is_valid():
            instance = order_form.save(commit=False)
            instance.customer = self.customer
            instance.seller = self.request.user
            instance.company = self.company
            instance.save()
            return redirect('crm:order_detail', self.customer.id)
        return self.render_to_response({'order_form': order_form})


# Страница списка работников
class OrderCreateView(OrderMixin):
    template_name = 'crm/order/create.html'

    def dispatch(self, *args, **kwargs):
        self.company = self.request.user.profile.company
        self.customers = self.get_customers(self.request, self.company)
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        customer_form = self.customer_form_class(request)
        order_form = self.order_form_class(request)
        return self.render_to_response({
            'customers': self.customers, 'customer_form': customer_form,
            'order_form': order_form})

    def post(self, request, *args, **kwargs):
        customer_form = self.customer_form_class(request, data=request.POST)
        order_form = self.order_form_class(request, data=request.POST)
        if customer_form.is_valid() and order_form.is_valid():
            customer = customer_form.save()
            order = order_form.save(commit=False)
            order.customer = customer
            order.save()
            return redirect('crm:order_detail', customer.id)
        return self.render_to_response({
            'customers': self.customers, 'customer_form': customer_form,
            'order_form': order_form})

class IntegrationMixin(View, TemplateResponseMixin, LoginRequiredMixin):
    form_class = IntegrationForm

    def get_integrations(self, request, company):
        customers = Integration.objects.filter(
            company=company).all()
        return customers

# Страница списка работников
class IntegrationListView(ListView, LoginRequiredMixin):
    template_name = 'crm/integration/list.html'
    model = Integration
    context_object_name = 'integrations'
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(company=self.request.user.profile.company)

class IntegrationCreateView(IntegrationMixin):
    template_name = 'crm/integration/form.html'

    def dispatch(self, *args, **kwargs):
        self.company = self.request.user.profile.company
        self.integrations = self.get_integrations(
            self.request, self.company)
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(request)
        return self.render_to_response({
            'integrations': self.integrations, 'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            integration = form.save()
            return redirect('crm:integration_detail', integration.id)
        return self.render_to_response({
            'integrations': self.integrations, 'form': form})

# Страница списка работников
class IntegrationDetailView(IntegrationMixin):
    template_name = 'crm/integration/form.html'

    def dispatch(self, *args, **kwargs):
        id = self.kwargs.get('id')
        self.company = self.request.user.profile.company
        self.integrations = self.get_integrations(
            self.request, self.company)
        self.integration = get_object_or_404(
            Integration, pk=id, company=self.company)
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(request, instance=self.integration)
        return self.render_to_response({
            'integrations': self.integrations, 'form': form,
            'integration': self.integration})

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            request, data=request.POST, instance=self.integration)
        if form.is_valid():
            integration = form.save()
            return redirect('crm:integration_detail', integration.id)
        return self.render_to_response({
            'integrations': self.integrations, 'form': form,
            'integration': self.integration})



class ReportMixin(WorkerMixin):

    def dispatch(self, *args, **kwargs):
        self.company = self.request.user.profile.company
        self.workers = self.get_workers(
            self.request, self.company)
        return super().dispatch(*args, **kwargs)


# Страница отчета
class ReportListView(ReportMixin):
    template_name = 'crm/report/list.html'

    def get(self, request, *args, **kwargs):
        lead = Lead.objects.filter(
            company=self.company)
        return self.render_to_response({
            'workers': self.workers, 'lead': lead})


# Детальная информация отчета
class ReportManagerView(ReportMixin):
    template_name = 'crm/report/manager.html'

    def get(self, request, *args, **kwargs):
        manager = get_object_or_404(
            User, pk=self.kwargs.get('manager'))
        lead = Lead.objects.filter(
            company=self.company, manager=manager)
        return self.render_to_response({
            'workers': self.workers, 'lead': lead})
