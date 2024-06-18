from aiogram import Router

from filters import IsAuthorized, IsRegistered
from .book import incident_book
from .incident_by_id import get_incident_by_id
from .update_incident import update_incident

router = Router()
router.message.filter(IsRegistered(), IsAuthorized())
router.callback_query.filter(IsRegistered(), IsAuthorized())
router.include_routers(incident_book.router, get_incident_by_id.router, update_incident.router)
