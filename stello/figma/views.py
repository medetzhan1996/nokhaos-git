import uuid
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.views.generic.base import TemplateResponseMixin, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Сategory, Product, ProductMaterial, Material
from .forms import CategoryForm, ProductForm
from crm.models import Сustomer
from social_messenger.models import Message
from crm.forms import OrderForm, СustomerForm


# List views
class IndexView(TemplateView):
    template_name = 'figma/client-site/index.html'

    def get(self, request, *args, **kwargs):
        seller = get_object_or_404(User, id=self.kwargs['seller'])
        Message.objects.create(lead_id=12,
                               message="{\"text\": \"\\u0425\\u043e\\u0440\\u043e\\u0448\\u043e \\u0436\\u0434\\u0451\\u043c\"}")
        kwargs.setdefault("seller", seller)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller = self.kwargs['seller']
        client_auth = self.request.session.get('client_auth')
        if not client_auth:
            client_auth = self.request.session['client_auth'] = str(
                uuid.uuid4())
        category = self.kwargs.get('category', None)
        context['categories'] = Сategory.objects.filter(
            seller=seller).all()
        context['client_auth'] = client_auth
        if not category:
            context['products'] = Product.objects.filter(
                is_top=True, seller=seller)[:12]
        else:
            context['category'] = get_object_or_404(Сategory, id=category)
            context['products'] = Product.objects.filter(
                category__id=category, seller=seller)[:12]
        return context


# Детальный просмотр продукта
class ProductDetailView(TemplateResponseMixin, View):
    template_name = 'figma/client-site/product_text_detail.html'
    order_form_class = OrderForm
    сustomer_form_class = СustomerForm
    context = {}

    def dispatch(self, *args, **kwargs):
        product_id = self.kwargs['id']
        self.context['seller'] = get_object_or_404(
            User, id=self.kwargs['seller'])
        client_auth = self.request.session.get('client_auth')
        if not client_auth:
            client_auth = self.request.session['client_auth'] = str(
                uuid.uuid4())
        self.context['client_auth'] = client_auth
        self.context['product'] = get_object_or_404(Product, id=product_id)
        self.context['product_materials'] = ProductMaterial.objects.filter(
            product__id=product_id).all()
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.context)

    def post(self, request, *args, **kwargs):
        order_form = self.order_form_class(request.POST)
        сustomer_form = self.сustomer_form_class(request.POST)
        if order_form.is_valid() and сustomer_form.is_valid():
            obj_customer, created = Сustomer.objects.get_or_create(
                account=self.context['client_auth'],
                defaults={
                    'phone_number': request.POST.get('phone_number')
                },
            )
            obj_order = order_form.save(commit=False)
            obj_order.customer = obj_customer
            obj_order.seller = self.context['seller']
            obj_order.save()
            return redirect('figma:index', self.kwargs['seller'])
        self.context['order_form'] = order_form
        self.context['сustomer_form'] = сustomer_form
        return self.render_to_response(self.context)


# Главная страница менеджера
class ConstructorIndexView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = 'figma/constructor-site/index.html'
    category_form_class = CategoryForm
    product_form_class = ProductForm
    auth_categories = None
    products = None
    product = None
    category = None

    def dispatch(self, *args, **kwargs):
        self.categories = Сategory.objects.filter(
            seller=self.request.user.id).all()
        self.products = Product.objects.filter(
            is_top=True, seller=self.request.user.id)[:12]
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            if request.GET.get('product_edit', None):
                self.product = get_object_or_404(
                    Product, id=request.GET.get('product_id'))
                return render(
                    request, 'figma/constructor-site/product_modal.html',
                    {'product_form': self.product_form_class(
                        request.user, instance=self.product),
                     'product': self.product})
            elif request.GET.get('category_edit', None):
                self.category = get_object_or_404(
                    Сategory, id=request.GET.get('category_id'))
                return render(
                    request, 'figma/constructor-site/category_modal.html',
                    {'category_form': self.category_form_class(
                        instance=self.category),
                     'category': self.category})
            elif request.GET.get('category_remove', None):
                self.category = get_object_or_404(
                    Сategory, id=request.GET.get('category_id'))
                return render(
                    request,
                    'figma/constructor-site/category_remove_modal.html',
                    {'category': self.category})
            elif request.GET.get('product_remove', None):
                self.product = get_object_or_404(
                    Product, id=request.GET.get('product_id'))
                return render(
                    request,
                    'figma/constructor-site/product_remove_modal.html',
                    {'product': self.product})
        return self.render_to_response(
            {
                'category_form': self.category_form_class(),
                'product_form': self.product_form_class(request.user),
                'categories': self.categories,
                'products': self.products,
                'product': self.product,
                'category': self.category
            })

    def post(self, request, *args, **kwargs):
        if request.POST.get('category-submit', None):
            category_id = request.POST.get('category_id', None)
            if category_id:
                category = get_object_or_404(Сategory, id=category_id)
                category_form = self.category_form_class(
                    request.POST, instance=category)
            else:
                category_form = self.category_form_class(request.POST)
            if category_form.is_valid():
                category_form.save()
        elif request.POST.get('product-submit', None):
            product_id = request.POST.get('product_id', None)
            if product_id:
                product = get_object_or_404(Product, id=product_id)
                product_form = self.product_form_class(
                    request.user, request.POST,
                    request.FILES, instance=product)
            else:
                product_form = self.product_form_class(
                    request.user, request.POST, request.FILES)
            if product_form.is_valid():
                product_form.save()
            else:
                print(product_form.errors)
        elif request.POST.get('category-remove-submit', None):
            Сategory.objects.filter(id=request.POST.get(
                'category_id'), seller=request.user.id).delete()
        elif request.POST.get('product-remove-submit', None):
            Product.objects.filter(id=request.POST.get(
                'product_id'), seller=request.user.id).delete()
        return redirect('figma:constructor_index')


# Mixin продукта
class ConstructorProductMixin(LoginRequiredMixin, TemplateResponseMixin, View):
    product_form_class = ProductForm
    product = None
    product_materials = None

    def dispatch(self, *args, **kwargs):
        self.product = get_object_or_404(
            Product, id=self.kwargs['id'])
        self.product_materials = ProductMaterial.objects.filter(
            product=self.kwargs['id']).all()
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        product_form = self.product_form_class(
            request.user, request.POST,
            request.FILES, instance=self.product)
        if product_form.is_valid():
            product_form.save()
            for material, price in zip(
                    request.POST.getlist('material_title'),
                    request.POST.getlist('material_price')):
                if material and price:
                    obj, created = Material.objects.get_or_create(
                        title=material)
                    q = ProductMaterial(material=obj, product=self.product,
                                        price=price)
                    q.save()
            if request.POST.get('send-material', None):
                return redirect('figma:constructor_product_detail',
                                self.kwargs['id'])
            return redirect('figma:constructor_index')
        return self.render_to_response({
            'product': self.product, 'product_form': product_form,
            'product_materials': self.product_materials})


# Детальная информация текстового продукта
class ConstructorProductDetailView(ConstructorProductMixin):
    template_name = 'figma/constructor-site/product_text_detail.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(
            {
                'product': self.product,
                'product_form': self.product_form_class(
                    request.user, instance=self.product),
                'product_materials': self.product_materials
            })


# Детальная информация продукта c выбором изображения
class ConstructorProductPhotoDetailView(ConstructorProductMixin):
    template_name = 'figma/constructor-site/product_photo_detail.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(
            {
                'product': self.product,
                'product_form': self.product_form_class(
                    request.user, instance=self.product),
                'product_materials': self.product_materials
            })
