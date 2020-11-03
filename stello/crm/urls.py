from django.urls import path
from . import views
app_name = 'crm'
urlpatterns = [
    path('worker/', views.WorkerListView.as_view(), name="worker_list"),
    path('worker/<int:worker_id>', views.WorkerUpdateView.as_view(),
         name="worker_update"),
    path('worker/create/', views.WorkerCreateView.as_view(),
         name="worker_create"),
    path('order/', views.OrderListView.as_view(), name="order"),
    path('order/<int:customer_id>', views.OrderDetailView.as_view(),
         name="order_detail"),
    path('order/create/', views.OrderCreateView.as_view(),
         name="order_create"),
    path('integration/list/', views.IntegrationListView.as_view(),
         name="integration_list"),
    path('integration/create/', views.IntegrationCreateView.as_view(),
         name="integration_create"),
    path('integration/<int:id>', views.IntegrationDetailView.as_view(),
         name="integration_detail"),
    path('report/list/', views.ReportListView.as_view(),
         name="report_list"),
    path('report/manager/<int:manager>', views.ReportManagerView.as_view(),
         name="report_manager"),
]
