from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from helper_func import is_admin
from database.pics_db import pics_db

@Bot.on_message(filters.command('set_pic') & filters.private & is_admin)
async def set_pic(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply("<b><i>Please reply to a photo with /set_pic to set it as a start picture.</i></b>")

    file_id = message.reply_to_message.photo.file_id
    await pics_db.add_pic(file_id)
    await message.reply("<b><i>Start picture added successfully! ✅</i></b>")

@Bot.on_message(filters.command('view_pic') & filters.private & is_admin)
async def view_pic(client: Client, message: Message):
    pics_dict = await pics_db.get_all_pics_with_id()
    if not pics_dict:
        return await message.reply("<b><i>No start pictures saved in the database.</i></b>")

    for i, (object_id, file_id) in enumerate(pics_dict.items(), start=1):
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("⛓️‍💥 ʀᴇᴍᴏᴠᴇ", callback_data=f"rm_pic_{object_id}")]
        ])
        await message.reply_photo(
            photo=file_id,
            caption=f"<b><i>Pic #{i}</i></b>",
            reply_markup=reply_markup
        )

@Bot.on_callback_query(filters.regex(r'^rm_pic_'))
async def remove_pic_callback(client: Client, query: CallbackQuery):
    from helper_func import check_admin
    class DummyUpdate:
        def __init__(self, from_user):
            self.from_user = from_user

    is_authorized = await check_admin(None, client, DummyUpdate(query.from_user))
    if not is_authorized:
        return await query.answer("You are not authorized to do this.", show_alert=True)

    object_id = query.data.split('_', 2)[2]
    await pics_db.remove_pic_by_object_id(object_id)
    await query.message.delete()
    await query.answer("Picture removed successfully!", show_alert=True)

