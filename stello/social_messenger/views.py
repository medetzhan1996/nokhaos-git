import base64
import json
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .tasks import sendMessageTask, sendPhotoTask,\
    sendMessageInstagramTask
from .forms import MessageForm
from datetime import datetime
from .utils import WhatsAppAPI
from .models import Message, ComplatedTask
from .forms import MessageForm
from crm.forms import OrderForm, СustomerForm
from crm.models import Сustomer, Lead,\
    CompanyLeadStatus, Integration, LeadStatus, Profile


@csrf_exempt
@require_POST
def webhookWhatsApp(request):
    now = datetime.now()
    data = json.loads(request.body)
    for value in data['messages']:
        id = value['id']
        type = value['type']
        complated_task = ComplatedTask.objects.filter(apiId=id).first()
        if not complated_task:
            fromMe = value['fromMe']
            login = value['chatName']
            social_id = value['chatId']
            body = value['body']
            type = value['type']
            caption = value['caption']
            integration = get_object_or_404(Integration,
                api_id=data['instanceId'])
            company = integration.company
            customer_obj, created = Сustomer.objects.get_or_create(
            social_id=social_id,
            defaults={'login': login, 'type': "whatsapp",
                      'social_id': social_id,
                      'company': company
                      })
            if created:
                dialog = WhatsAppAPI.getDialog(
                    integration.api_id, integration.api_token,
                    customer_obj.social_id)
                customer_obj.avatar = dialog.get('image')
                customer_obj.save()
            obj_lead, created_lead = Lead.objects.get_or_create(
            customer=customer_obj, company=company,
            defaults={
                'integration': integration, 'customer': customer_obj,
                'company': company
            })
            integration.customers.add(customer_obj)
            message_unread = obj_lead.message_unread + 1
            user = obj_lead.manager
            if not user:
                user = User.objects.filter(
                        profile__company=company, integration=integration,
                    ).order_by('profile__last_lead').first()
                Profile.objects.filter(
                    company=company, user=user).update(last_lead=now)
                obj_lead.manager = user
                obj_lead.message_unread = message_unread
            send_message = Message(lead=obj_lead, fromMe=fromMe)
            if not created_lead:
                obj_lead.updated_at = now
            obj_lead.save()
            if(type == 'chat'):
                send_message.message = body
            elif(type == 'ptt'):
                send_message.message = caption
                send_message.ptt_url = body
            else:
                send_message.photo_url = body
            send_message.save()
            channel_layer = get_channel_layer()
            data = {
                'id': send_message.id,
                'type': 'send_message',
                'lead': obj_lead.id,
                'fromMe': fromMe
            }
            group_manager = 'manager_%s' % user.id
            async_to_sync(channel_layer.group_send)(
                group_manager, data)
            group_leaders = 'leaders_%s' % user.profile.company.id
            async_to_sync(channel_layer.group_send)(
                group_leaders, data)
        return HttpResponse(status=200)

@csrf_exempt
@require_POST
def webhook(request):
    jsondata = request.body
    data = json.loads(jsondata)
    type = data['type']
    if type == 'message.incoming':
        lead_id = data['leadId']
        integration_id = data['message']['sa']['id']
        integration = get_object_or_404(Integration, id=integration_id)
        company = integration.company
        real_Id = data['message']['source']['realId']
        sender = data['message']['sender']
        customer_id = sender['customerId']
        login = sender['login']
        avatar = sender.get('avatar', None)
        type = sender['type']
        socialId = sender['socialId']
        obj, created = Сustomer.objects.get_or_create(
            customer_id=customer_id,
            defaults={'login': login, 'type': type,
                      'avatar': avatar, 'customer_id': customer_id,
                      'social_id': socialId, 'company': company
                      })
        obj_lead, created_lead = Lead.objects.get_or_create(
            lead_id=lead_id, company=company,
            defaults={
                'real_id': real_Id, 'integration': integration,
                'lead_id': lead_id, 'customer': obj
            })
        message = json.dumps(data['message']['message'])
        Message.objects.create(lead=obj_lead, message=message)
    return HttpResponse(status=200)


class LeadListView(ListView, LoginRequiredMixin):
    def get_queryset(self):
        self.user = self.request.user
        self.company = self.user.profile.company
        qs = super().get_queryset()
        qs = qs.filter(company=self.company)
        if self.user.profile.type == 3:
            qs = qs.filter(manager=self.user)
        return qs

    model = Lead
    paginate_by = 20
    ordering = ['-updated_at']
    template_name = 'social_messenger/main.html'
    context_object_name = 'leads'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['workers'] = User.objects.filter(
            profile__company=self.company).all()
        context['lead_statuses'] = CompanyLeadStatus.objects.filter(
            company=self.company).all()
        return context


class LeadSearchView(View, LoginRequiredMixin):

    def get(self, request, *args, **kwargs):
        company = self.request.user.profile.company
        lead = request.GET.get('lead', None)
        search = request.GET.get('search', None)
        worker = request.GET.get('worker', None)
        status = request.GET.get('status', None)
        if worker:
            worker = get_object_or_404(User, pk=worker)
        if request.user.profile.type == 3:
            worker = request.user
        leads = self.get_leads(request, company, worker, status, lead, search)
        return render(request, 'social_messenger/lead_list.html',
                      {'leads': leads})

    def get_leads(self, request, company, user, status, lead, search):
        leads = Lead.objects.filter(company=company)
        if user:
            leads = leads.filter(manager=user)
        if search:
            leads = leads.filter(customer__login__icontains=search)
        if status:
            leads = leads.filter(status=status)
        if lead:
            leads = leads.filter(id=lead)
        return leads.all()


class LeadStatusChangeView(View, LoginRequiredMixin):
    def post(self, request, *args, **kwargs):
        company = self.request.user.profile.company
        lead = request.POST.get('lead', None)
        status_id = request.POST.get('status_id', None)
        lead = Lead.objects.filter(
            company=company, id=lead)
        if lead.exists():
            lead.update(status_id=status_id)
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False})


class MessageListView(View, LoginRequiredMixin):

    def get(self, request, *args, **kwargs):
        message = request.GET.get('message', None)
        lead = get_object_or_404(Lead, pk=request.GET.get('lead'))
        lead.message_unread = 0
        lead.save()
        messages = Message.objects.filter(
            lead=lead).order_by('created_at')
        if message:
            messages = messages.filter(id=message)
        return render(request, 'social_messenger/messages.html',
                      {'messages': messages, 'lead': lead})


class MessageCreateView(View, LoginRequiredMixin):
    message_form_class = MessageForm

    def post(self, request, *args, **kwargs):
        photoBase64 = request.POST.get('photoBase64', None)
        message_form = self.message_form_class(request.POST, request.FILES)
        if message_form.is_valid():
            message = message_form.save(commit=False)
            if photoBase64:
                format, imgstr = photoBase64.split(';base64,')
                ext = format.split('/')[-1]
                photo_name = 'image.' + ext
                photo = ContentFile(base64.b64decode(imgstr), name=photo_name)
                message.photo = photo
            message.save()
            messages = Message.objects.filter(id=message.id)[:1]
            lead = message.lead
            integration = lead.integration
            message_text = message.message
            if integration.type == 'whatsapp':         
                data = {
                    'message_id': message.id,
                    'token': integration.api_token,
                    'account_id': integration.api_id,
                    'chat_id': lead.customer.social_id,
                    'message_text': message.message

                }
                if message_text:
                    sendMessageTask.delay(data)
            elif integration.type == 'instagramV2':
                data = {
                    'lead_id': lead.lead_id, 'source': lead.real_id,
                    'userId': 12502, 'customId': message.id

                }
                data['message'] = {'text': message_text}
                sendMessageInstagramTask.delay(data)
            return render(request,
                          'social_messenger/messages.html',
                          {'messages': messages})


class OrderCreateView(View, LoginRequiredMixin):
    customer_form_class = СustomerForm
    order_form_class = OrderForm

    def get(self, request, *args, **kwargs):
        lead = get_object_or_404(Lead, pk=request.GET.get('lead'))
        customer_form = self.customer_form_class(
            request, instance=lead.customer)
        order_form = self.order_form_class(request)
        return render(request, 'social_messenger/order_create.html',
                      {'order_form': order_form,
                       'customer_form': customer_form})

    def post(self, request, *args, **kwargs):
        customer = get_object_or_404(
            Сustomer, pk=request.POST.get('customer'))
        customer_form = self.customer_form_class(
            request, data=request.POST, instance=customer)
        order_form = self.order_form_class(request, data=request.POST)
        if customer_form.is_valid() and order_form.is_valid():
            customer_save = customer_form.save()
            order_save = order_form.save(commit=False)
            order_save.customer = customer_save
            order_save.save()
            return JsonResponse({"success": True})
        return JsonResponse({
            "success": False, 'order_errors': order_form.errors.as_json(),
            'customer_errors': customer_form.errors.as_json()})
