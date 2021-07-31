from typing import DefaultDict, Optional, Tuple
import json
from collections import defaultdict

from telegram.ext import BasePersistence
from telegram.ext.utils.types import UD, CD, BD, CDCData, ConversationDict
from telegram.utils.helpers import (
    decode_user_chat_data_from_json, decode_conversations_from_json, encode_conversations_to_json
)
from redis import Redis


class RedisPersistence(BasePersistence):
    def __init__(self, host: str, port: int, db: int = 0, password: str = None, *args, **kwargs) -> None:
        self.r_conn = Redis(host=host, port=port, db=db, password=password, decode_responses=True)
        super().__init__(*args, **kwargs)

    # Methods for db
    def get_redis_connection(self) -> Redis:
        return self.r_conn

    # Methods for bot data
    def get_bot_data(self) -> BD:
        r_conn = self.get_redis_connection()
        bot_data = r_conn.get('_bot_data')
        if not bot_data:
            return {}
        return json.loads(bot_data)

    def update_bot_data(self, data: BD) -> None:
        r_conn = self.get_redis_connection()
        bot_data = r_conn.get('_bot_data')
        if bot_data and json.loads(bot_data) == data:
            return
        r_conn.set('_bot_data', json.dumps(data))
    
    # Methods for chat data
    def get_chat_data(self) -> DefaultDict[int, CD]:
        r_conn = self.get_redis_connection()
        chat_data = r_conn.get('_chat_data')
        if chat_data is None:
            return defaultdict(dict)
        return defaultdict(dict, decode_user_chat_data_from_json(chat_data))
        
    def update_chat_data(self, chat_id: int, data: CD) -> None:
        r_conn = self.get_redis_connection()
        chat_data = r_conn.get('_chat_data')
        if chat_data is None:
            chat_data = defaultdict(dict)
        else:
            chat_data = defaultdict(dict, decode_user_chat_data_from_json(chat_data))
            if chat_data[chat_id] == data:
                return
        chat_data[chat_id] = data
        r_conn.set('_chat_data', json.dumps(chat_data))

    # Methods fot user data
    def get_user_data(self) -> DefaultDict[int, UD]:
        r_conn = self.get_redis_connection()
        user_data = r_conn.get('_user_data')
        if user_data is None:
            return defaultdict(dict)
        return defaultdict(dict, decode_user_chat_data_from_json(user_data))

    def update_user_data(self, user_id: int, data: UD) -> None:
        r_conn = self.get_redis_connection()
        user_data = r_conn.get('_user_data')
        if user_data is None:
            user_data = defaultdict(dict)
        else:
            user_data = defaultdict(dict, decode_user_chat_data_from_json(user_data))
            if user_data[user_id] == data:
                return
        user_data[user_id] = data
        r_conn.set('_user_data', json.dumps(user_data))

    # Methods for callback data
    def get_callback_data(self) -> Optional[CDCData]:
        r_conn = self.get_redis_connection()
        callback_data = r_conn.get('_callback_data')
        if callback_data is None:
            return None
        callback_data = json.loads(callback_data)
        return callback_data[0], callback_data[1].copy()

    def update_callback_data(self, data: CDCData) -> None:
        r_conn = self.get_redis_connection()
        callback_data = r_conn.get('_callback_data')
        if callback_data and json.loads(callback_data) == data:
            return
        r_conn.set('_callback_data', json.dumps([data[0], data[1].copy()]))

    # Methods for conversations
    def get_conversations(self, name: str) -> ConversationDict:
        r_conn = self.get_redis_connection()
        conversations = r_conn.get('_conversations')
        if conversations is None:
            return {}
        conversations = decode_conversations_from_json(conversations)
        return conversations.get(name, {}).copy()

    def update_conversation(
        self,
        name: str,
        key: Tuple[int, ...],
        new_state: Optional[object]
    ) -> None:
        r_conn = self.get_redis_connection()
        conversations = r_conn.get('_conversations')
        if conversations is None:
            conversations = {}
        else:
            conversations = decode_conversations_from_json(conversations)
        if conversations.setdefault(name, {}).get(key) == new_state:
            return
        conversations[name][key] = new_state
        r_conn.set('_conversations', encode_conversations_to_json(conversations))
