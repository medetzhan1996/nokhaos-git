from django.urls import path
from . import views
app_name = 'figma'
urlpatterns = [
    # Сайт клиента
    path('<int:seller>/', views.IndexView.as_view(), name='index'),
    path('<int:seller>/<int:category>', views.IndexView.as_view(),
         name='index'),
    path('product/<int:seller>/<id>', views.ProductDetailView.as_view(),
         name='product_detail'),
    # Сайт конструктор сайта
    path('constructor/', views.ConstructorIndexView.as_view(),
         name='constructor_index'),
    path('constructor/product/<int:id>',
         views.ConstructorProductDetailView.as_view(),
         name='constructor_product_detail'),
    path('constructor/product_photo/<int:id>',
         views.ConstructorProductPhotoDetailView.as_view(),
         name='constructor_product_photo_detail'),
]
