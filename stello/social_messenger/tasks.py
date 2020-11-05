from celery import task
from .models import ComplatedTask
from .utils import WhatsAppAPI, UmnicoWebAPI

@task
def sendMessageTask(data):
    message_id = data.get('message_id')
    token = data.get('token')
    account_id = data.get('account_id')
    chat_id = data.get('chat_id')
    message_text = data.get('message_text')
    send_message = WhatsAppAPI.sendMessage(
        account_id, token, chat_id, message_text)
    return send_message
    apiId = send_message.get('id')
    ComplatedTask.objects.create(message_id=message_id, apiId=apiId)
    return send_message.get('sent')

@task
def sendPhotoTask(data):
    token = data.get('token')
    account_id = data.get('account_id')
    chat_id = data.get('chat_id')
    fileurl = data.get('fileurl')
    filename = data.get('filename')
    message_id = data.get('message_id')
    send_photo = WhatsAppAPI.sendPhoto(
    	account_id, token, chat_id, fileurl, filename)
    apiId = send_photo.get('id')
    ComplatedTask.objects.create(message_id=message_id, apiId=apiId)
    return send_photo.get('sent')

@task
def sendMessageInstagramTask(data):
    lead_id = data.get('lead_id')
    message = data.get('message')
    source = data.get('source')
    userId = data.get('userId')
    customId = data.get('customId')
    accessToken = UmnicoWebAPI.get_token(
        'gulim.zhangazy@bk.ru', 'dostar1996')
    token = accessToken['accessToken']['token']
    return UmnicoWebAPI.send_message(
        lead_id, message, source,
        userId, str(customId), token)