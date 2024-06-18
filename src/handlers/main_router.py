from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from handlers import auth_router, admin_router, users_router, incidents_router, other_router
from lexicons import COMMON_LEXICON
from database.query_service import get_user

router = Router()
router.include_routers(
    auth_router,
    admin_router,
    users_router,
    incidents_router,
    other_router
)


@router.message(CommandStart())
async def start_command(message: Message, session: AsyncSession):
    user = await get_user(user_id=message.from_user.id, session=session)
    if user:
        return await message.answer(text=COMMON_LEXICON['start_command']['welcome_registered'])
    else:
        return await message.answer(text=COMMON_LEXICON['start_command']['welcome_unregistered'])


@router.message(Command(commands='cancel'))
async def cancel_command(message: Message, state: FSMContext):
    await state.clear()
    return await message.answer(
        text=COMMON_LEXICON['cancel_command']['return_to_main_menu']
    )
