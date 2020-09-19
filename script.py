from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from collections import defaultdict, deque
import random
import boto3
import botocore
import os
import json
import requests


aws_key = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
telegram_token = os.environ['TELEGRAM_TOKEN']
server_url = os.environ['SERVER_URL']
users = json.loads(os.environ['CHAT_USERS'])
class GPTBot:
    def __init__(self, max_len = 5):
        self.updater = Updater(telegram_token, use_context = True)
        self.messages = defaultdict(lambda: deque(maxlen=max_len))
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler('start',self.start))
        dp.add_handler(CommandHandler('whatabout',self.whatabout))
        dp.add_handler(MessageHandler(Filters.text & (~Filters.command),self.on_message))
    def start(self, update, context):
        context.bot.send_message(update.message.chat_id, 'Usage: just write something then write /whatabout')

    def on_message(self, update, context):
        if not update or not update.message or not update.message.chat_id or not update.message.text or not update.message.from_user:
            return
        msg = self.messages[update.message.chat_id] 
        userm = update.message.from_user
        user = users.get(userm.first_name + ' ' + userm.last_name, None)
        if user and update.message.text:
            msg.append(user + ': "' + update.message.text + '"\n')
        else:
            print(userm)

    def whatabout(self, update, context):
        chat_id = update.message.chat_id
        msgs = self.messages[chat_id]
        ruser = random.choice(list(users.values()))
        if not msgs:
            text = '"Дом мой пуст"'
        else:
            cfg = botocore.config.Config(retries={'max_attempts': 0}, read_timeout=360, connect_timeout=360, region_name="eu-central-1" )
            client = boto3.client('lambda', config=cfg, region_name='eu-central-1', aws_access_key_id=aws_key, aws_secret_access_key=aws_secret_key)
            payload={"Prompt": ''.join(msgs) + ruser + ': "', "Temperature": 0.9, "NQuotes": 1}
            response = client.invoke(FunctionName = 'tabaqui_response', InvocationType = 'RequestResponse', LogType = 'Tail', Payload = json.dumps(payload))
            dictj = json.loads(response['Payload'].read().decode())
            text = dictj['Response']
        text = [s for s in text.split('"') if len(s) > 0][:1]
        context.bot.send_message(chat_id, text[0] if text and text[0] else 'Акела промахнулся')


def main():
    r = requests.get(url = 'https://api.telegram.org/bot%s/setWebHook'%(telegram_token))
    bot = GPTBot()
    bot.updater.start_polling()
    bot.updater.idle()
    r = requests.get(url = 'https://api.telegram.org/bot%s/setWebHook?url=%s'%(telegram_token, server_url))
    
if __name__ == '__main__':
    main()
