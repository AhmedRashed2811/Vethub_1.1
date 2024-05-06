# chat/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.core.serializers import serialize
from django.utils import timezone
from django.db.models import Subquery

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = await self.get_user()
        self.chat_id = f"{self.scope['url_route']['kwargs']['chat_id']}"
        self.seen = False
        await self.channel_layer.group_add(self.chat_id, self.channel_name)
        if "user" in self.scope and self.scope["user"].is_authenticated:
            self.user = await self.get_user()
            # Any other connection logic
            await self.accept()
        else:
            # Handle unauthenticated connection
            await self.close()

    @database_sync_to_async
    def get_user(self):
        # Retrieve user associated with the WebSocket connection
        user = None
        if self.scope["user"].is_authenticated:
            user = self.scope["user"]
        return user
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.chat_id, self.channel_name)
        

    # Receive message from WebSocket
    async def receive(self, text_data):
        data_json = json.loads(text_data)
        message = data_json
        task = data_json.get("task")
        
        if task == "perform_task":
            # Perform the desired task using additional_info
            # For example:
            message_id = data_json.get("message_id")
            chat_message = await self.get_chat_message(message_id)
            await self.save_chat_message(chat_message)
            message['seen'] = True

            
        else:
            message_id = await self.create_message(data = message)
            message["id"] = message_id
            if not message.get('processed', False):
                # Mark the message as processed to avoid duplicates
                message['processed'] = True
                
                # Send message to room group
                await self.channel_layer.group_send(
                    self.chat_id,
                    {
                        'type': 'send_message',
                        'message': message
                    }
                )

    async def send_message(self, event):
        data = event['message']
        await self.send(text_data=json.dumps({'message': data}))
        
    
    
    @database_sync_to_async
    def create_message(self, data):

        new_message = data["message"]
        sender_id = data["sender_id"]
        receiver_id = data["receiver_id"]
        user_id = data["user_id"]
        #user = get_object_or_404(User, pk=sender_id)
        user_model = get_user_model()
        
        
        
        user = user_model.objects.get(pk=user_id)
        
        if user.groups.filter(name='Customers').exists():
            customer = user.customer
            doctor = get_object_or_404(User, pk=receiver_id)
            chat = Chat.objects.filter(customer = customer, doctor = doctor.doctor).first()
            chat.last_msg_sender = "Customer"
            chat.last_msg = new_message
            chat.last_msg_seen = False 
            chat.last_msg_time = timezone.now()
            chat.save()
            chat_message = ChatMessage.objects.create(content = new_message,
                                                    msg_sender = user,
                                                    msg_receiver = doctor,
                                                    chat = chat,seen=True if doctor == user else False)
            return chat_message.id
        
        elif user.groups.filter(name='Doctors').exists():
            doctor = user.doctor
            customer = get_object_or_404(User, pk=receiver_id)
            chat = Chat.objects.filter(customer = customer.customer, doctor = doctor).first()
            chat.last_msg = new_message
            chat.last_msg_sender = "Doctor"
            chat.last_msg_seen = False 
            chat.last_msg_time = timezone.now()
            chat.save()
            chat_message = ChatMessage.objects.create(content = new_message,
                                                    msg_sender = user,
                                                    msg_receiver = customer,
                                                    chat = chat,seen=True if customer == user else False)
            
            # Update seen status for messages received by the receiver
            return chat_message.id

    
    
    @database_sync_to_async
    def get_chat_message(self, message_id):
        return ChatMessage.objects.filter(id=message_id).first()  

    @database_sync_to_async
    def save_chat_message(self, chat_message):
        chat_message.seen = True
        chat_message.save()











class ChatsConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.user_id = f"{self.scope['url_route']['kwargs']['user_id']}"
        await self.channel_layer.group_add(self.user_id, self.channel_name)
        await self.accept()
        await self.send_initial_chats()


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.user_id, self.channel_name)
        
    
    async def send_initial_chats(self):
        chats = await self.get_user_chats()
        await self.send(text_data=json.dumps({'chats': chats}))

    @database_sync_to_async
    def get_user_chats(self):
        # Fetch chats for the user and serialize them
        user_id = self.user_id
        user_model = get_user_model()
        
        user = user_model.objects.get(pk=user_id)
        
        if user.groups.filter(name='Customers').exists():
            customer = user.customer
            chats = Chat.objects.filter(customer = customer)
            last_msgs = []
            returned_chats = []
            ids = []
            names= []
            images = []
            for chat in chats:
                # if chat.last_msg == "":
                #     chat.delete()
                #     continue
                returned_chats.append(chat)
                ids.append(chat.doctor.user.id)
                names.append(chat.doctor.user.name)
                images.append(chat.doctor.profile_photo.url)
                last_msgs.append(chat.last_msg)
            
            serialized_chats = serialize('json', returned_chats)
            serialized_user = {"id": customer.user.id, "name": customer.user.name, "type": "Customer"}
            
            context = {
                "user": serialized_user,
                "chats": serialized_chats,
                "ids" :ids,
                "names":names,
                "images": images,
                "last_msgs": last_msgs}
            return context
        
        if user.groups.filter(name='Doctors').exists():
            doctor = user.doctor
            chats = Chat.objects.filter(doctor = doctor)
            returned_chats = []
            for chat in chats:
                # if chat.last_msg == "":
                #     chat.delete()
                #     continue
                
                returned_chats.append(chat)
                
            serialized_chats = serialize('json', chats)
            serialized_user ={"id": doctor.user.id, "name": doctor.user.name, "type": "Doctor"}
            
            context = {"user": serialized_user, "chats": serialized_chats}
            return context
        
            user_chats = Chat.objects.filter(user_id=self.user_id).values('id', 'name')  # Modify this query according to your model
            return list(user_chats)
        