import random
import uuid
from datetime import datetime
from typing import Optional

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message, Chat, CallbackQuery, Update
from aiogram.types import User as UserType
from factory import LazyAttribute, Sequence
from factory_boy_extra.async_sqlalchemy_factory import AsyncSQLAlchemyModelFactory

from database import Settings, User, OnlineSession, Event, Incident, IncidentStatus, IncidentSeverity, get_redis_storage


def get_state(bot_id: Optional[int] = None, user_id: Optional[int] = None) -> FSMContext:
    return FSMContext(storage=get_redis_storage(), key=StorageKey(bot_id=bot_id, chat_id=user_id, user_id=user_id))


def get_message(text: str, user_id: Optional[int] = None) -> Message:
    user = UserFactory.build(user_id=user_id) if user_id else UserFactory.build()
    return Message(
        chat=Chat(
            id=user.user_id,
            type='private'
        ),
        date=datetime.now(),
        message_id=123,
        from_user=UserType(
            id=user.user_id,
            is_bot=False,
            first_name="Test",
            last_name="Test",
            username=user.username,
        ),
        text=text,
        reply_markup=None
    )


def get_callback_query(data: str, user_id: Optional[int] = None, message: Optional[Message] = None) -> CallbackQuery:
    user = UserFactory.build(user_id=user_id) if user_id else UserFactory.build()
    return CallbackQuery(
        id="test",
        from_user=UserType(
            id=user.user_id,
            is_bot=False,
            first_name="Test",
            last_name="Test",
            username=user.username,
        ),
        chat_instance="test",
        message=message or get_message(
            text='test',
            user_id=user.user_id
        ),
        inline_message_id=None,
        data=data,
        game_short_name=None
    )


def get_update(message: Message = None, callback: CallbackQuery = None) -> Update:
    return Update(
        update_id=123,
        message=message,
        callback_query=callback)


class UserFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = User

    user_id = Sequence(lambda n: n)
    username = LazyAttribute(lambda o: f'user_{o.user_id}')
    created_at = datetime.now()


class OnlineSessionFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = OnlineSession

    user_id = Sequence(lambda n: n)
    online = False
    scheduler_id = 'Test_scheduler_id'


class SettingsFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = Settings

    id = 1234
    pause_time = 3
    time_zone = 3
    reg_pass = 'example_password'
    last_incident_time = datetime.now()


class IncidentFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = Incident

    incident_id = LazyAttribute(lambda o: str(uuid.uuid4()))
    key = LazyAttribute(lambda o: f'INC_{o.incident_id}')
    name = 'test_incident'
    status = LazyAttribute(
        lambda o: random.choice([IncidentStatus.New, IncidentStatus.Approved, IncidentStatus.InProgress,
                                 IncidentStatus.Resolved, IncidentStatus.Closed]))
    type = 'test_type'
    created_at = datetime.now()
    severity = LazyAttribute(
        lambda o: random.choice([IncidentSeverity.High, IncidentSeverity.Medium, IncidentSeverity.Low]))


class EventFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = Event

    incident_id = LazyAttribute(lambda o: str(uuid.uuid4()))
    event_id = LazyAttribute(lambda o: str(uuid.uuid4()))
    created_at = datetime.now()
    description = 'test_description'

