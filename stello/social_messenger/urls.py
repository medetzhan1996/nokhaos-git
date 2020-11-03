from django.urls import path
from . import views
app_name = 'social_messenger'
urlpatterns = [
    # Сайт клиента
    path('webhook/', views.webhook, name='webhook'),
    path('webhookWhatsApp/', views.webhookWhatsApp, name='webhookWhatsApp'),
    path('lead/', views.LeadListView.as_view(), name='lead_list'),
    path('lead/search/', views.LeadSearchView.as_view(), name='lead_search'),
    path('message/list/', views.MessageListView.as_view(),
         name='message_list'),
    path('message/create/', views.MessageCreateView.as_view(),
         name='message_create'),
    path('order/create/', views.OrderCreateView.as_view(),
         name='order_create'),
    path('lead/status/change/', views.LeadStatusChangeView.as_view(),
         name='lead_status_change'),
]
