from aiogram import Router, types, F
from aiogram.filters import Command
from commands.keyboards import admin_menu
from commands.admin_commands.user_card import router as user_card_router
from commands.admin_commands.admin_menu import router as admin_menu_router
from commands.admin_commands.user_requests import router as user_requests_router

router = Router()
router.include_router(admin_menu_router)
router.include_router(user_card_router)
router.include_router(user_requests_router)

@router.message(Command("admin"))
async def admin_command(message: types.Message) -> None:
    await message.answer("<b>Меню администратора:</b>", reply_markup=admin_menu(), parse_mode='HTML')

@router.callback_query(F.data == 'admin')
async def back_admin_menu(call: types.CallbackQuery) -> None:
    await call.message.edit_text("<b>Меню администратора:</b>", reply_markup=admin_menu(), parse_mode='HTML')