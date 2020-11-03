import requests
from crm.models import Integration
API_URL = 'https://api.umnico.com/v1.3/auth/login'
WhatsApp_API_URL = 'https://eu125.chat-api.com/instance{0}/{1}?token={2}'


class WhatsAppAPI:

    @staticmethod
    def sendMessage(account_id, token, chat_id, message_text):
        sendMessage = requests.post(
            WhatsApp_API_URL.format(account_id, "sendMessage", token),
            json={'chatId': chat_id, 'body': message_text}).json()
        return sendMessage

    @staticmethod
    def sendPhoto(account_id, token, chat_id, fileurl, filename):
        sendPhoto = requests.post(
            WhatsApp_API_URL.format(account_id, "sendFile", token),
            json={'chatId': chat_id, 'body': fileurl,
                  'filename': filename}).json()
        return sendPhoto
    
    @staticmethod
    def getDialog(account_id, token, chatId):
        dialog = requests.get(
            WhatsApp_API_URL.format(account_id, "dialog", token),
            json={'chatId': chatId}).json()
        return dialog

class UmnicoWebAPI:

    # Получить токен
    @staticmethod
    def get_token(login, password):
        token = requests.post('https://api.umnico.com/v1.3/auth/login',
                              json={"login": login, "pass": password}).json()
        return token

    # Получить список аккаунтов
    @staticmethod
    def get_account(token):
        account = requests.get('https://api.umnico.com/v1.3/account/me',
                               headers={'Authorization': token}).json()
        return account

    # Получить список интеграции
    @staticmethod
    def get_integrations(token):
        integrations = requests.get('https://api.umnico.com/v1.3/integrations',
                                    headers={'Authorization': token}).json()
        return integrations

    # Отправить сообщение
    @staticmethod
    def send_message(lead_id, message, source, userId, customId, token):
        return requests.post(
            'https://api.umnico.com/v1.3/messaging/{0}/send'.format(lead_id),
            headers={'Authorization': token}, json={
                "message": message,
                "source": source,
                "userId": userId,
                "customId": customId
            }).status_code

    # Получить список новых сообщении
    @staticmethod
    def get_new_messages(token):
        messages = requests.get('https://api.umnico.com/v1.3/leads/inbox?\
            offset=0&limit=10&types=whatsapp&\
            types=instagramV2&source_types=message',
                                headers={'Authorization': token}).json()
        return messages

    # Получить данные канала
    @staticmethod
    def get_channel_data(lead_id, token):
        channel = requests.get(
            'https://api.umnico.com/v1.3/messaging/{0}/sources'.format(
                lead_id),
            headers={'Authorization': token}).json()
        return channel

    # Получить историю сообщений для каждого канала
    @staticmethod
    def get_channel_history(lead_id, source_real_id, token):
        channel_history = requests.post(
            'https://api.umnico.com/v1.3/messaging/{0}/history/{1}'.format(
                lead_id, source_real_id),
            headers={'Authorization': token}).json()
        return channel_history

    # Добавить адрес в webhook
    @staticmethod
    def add_webhook(id, url, token):
        webhook = requests.post(
            'https://api.umnico.com/v1.3/webhooks/',
            headers={'Authorization': token}, json={
                "id": id,
                "url": url
            }).json()
        return webhook

    # Удалить адрес в webhook
    @staticmethod
    def remove_webhook(id, token):
        webhook = requests.delete(
            'https://api.umnico.com/v1.3/webhooks/{0}'.format(id),
            headers={'Authorization': token})
        return webhook

    # Получить добавленные адресы webhook
    @staticmethod
    def get_webhook(token):
        webhook = requests.get(
            'https://api.umnico.com/v1.3/webhooks/',
            headers={'Authorization': token}).json()
        return webhook

    # Добавить новую интеграцию
    def add_integration(integrations):
        for integration in integrations:
            id = integration.get('id')
            type = integration.get('type')
            login = integration.get('login')
            avatar = integration.get('avatar')
            externalId = integration.get('externalId')
            status = integration.get('status')
            obj, created = Integration.objects.get_or_create(
                id=id, defaults={
                    'type': type, 'login': login, 'avatar': avatar,
                    'externalId': externalId, 'status': status,
                    'company_id': 1
                })
            return 'success'
