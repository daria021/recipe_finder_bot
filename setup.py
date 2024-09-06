import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler, ApplicationBuilder
from telegram.ext.filters import PHOTO, TEXT

from GPT.dependencies.services import get_gpt_service
from config import config
from food.dependencies.services import get_food_service
from keyboards import chunk
from qr.dependencies.services import get_qr_service
from recipe.dependencies.services import get_recipe_service
from recipe.schemas import RecipeResponse

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

PAGINATION_KEY = 'recipe_page'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="йоу, загрузить чек - /receipt,"
                                        "получить список возможных блюд - /menu,"
                                        "отменить все в мире - /cancel,"
                                        "удалить все из базы - /delete,"
                                        "сгенерировать рецепт с помощью gpt - /gpt, "
                                        "сгенерировать рецепт с определенными ингридиентами - /specific")


async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Отправьте фото чека")
    return "asked_receipt"


async def get_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE,
                      qr_service=get_qr_service()):
    photo_file = await update.effective_message.photo[-1].get_file()

    file_path = "bills/qr_code.jpeg"

    await photo_file.download_to_drive(file_path)

    await context.bot.send_message(chat_id=update.effective_chat.id, text="ща все будет")

    products = await qr_service.decode_qr_code(file_path)
    if not products:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="не нашел ничего")
        return ConversationHandler.END

    await context.bot.send_message(chat_id=update.effective_chat.id, text='\n'.join(products))
    return ConversationHandler.END


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE, recipe_service=get_recipe_service()):
    menu = await recipe_service.get_menu()

    if not menu:
        await update.effective_message.reply_text("Рецептов не найдено.")
        return ConversationHandler.END

    markup = await create_markup(update, context, menu)

    await update.effective_message.reply_text(text="Что будете заказывать?", reply_markup=markup)
    return "asked_food"


async def pagination(update: Update, context: ContextTypes.DEFAULT_TYPE, recipe_service=get_recipe_service()):
    query = update.callback_query
    await query.answer()
    menu = await recipe_service.get_menu()

    if query.data == "next_page":
        context.user_data[PAGINATION_KEY] = context.user_data.get(PAGINATION_KEY, 0) + 1

        markup = await create_markup(update, context, menu)

        await update.effective_message.edit_reply_markup(reply_markup=markup)
    elif query.data == "prev_page":
        context.user_data[PAGINATION_KEY] = max(0, context.user_data.get(PAGINATION_KEY, 0) - 1)
        markup = await create_markup(update, context, menu)
        await update.effective_message.edit_reply_markup(reply_markup=markup)
    elif query.data.startswith("recipe_"):
        recipe_id = int(query.data[len("recipe_"):])
        recipe = await recipe_service.get(recipe_id)
        if recipe:
            await update.effective_message.reply_text(f"Рецепт: {recipe.title}\n\n{recipe.description}")
        else:
            await update.effective_message.reply_text("Рецепт не найден.")


async def create_markup(update: Update, context: ContextTypes.DEFAULT_TYPE, menu: list[RecipeResponse]):
    page = context.user_data.get(PAGINATION_KEY, 0)
    start_index = page * config.RECIPES_PER_PAGE
    end_index = start_index + config.RECIPES_PER_PAGE

    if start_index >= len(menu):
        start_index = len(menu) - config.RECIPES_PER_PAGE
        end_index = start_index + config.RECIPES_PER_PAGE
        context.user_data[PAGINATION_KEY] = max(0, context.user_data.get(PAGINATION_KEY, 0) - 1)

    buttons = chunk(menu[start_index:end_index])
    kinds_menu = [[InlineKeyboardButton(x.title, callback_data=f"recipe_{x.id}") for x in row] for row in buttons]

    navigation_buttons = []
    if start_index > 0:
        navigation_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data="prev_page"))
    if end_index < len(menu):
        navigation_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data="next_page"))
    if navigation_buttons:
        kinds_menu.append(navigation_buttons)
    markup = InlineKeyboardMarkup(kinds_menu)
    return markup


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


async def delete_food(update: Update, context: ContextTypes.DEFAULT_TYPE,
                      food_service=get_food_service()):
    await food_service.delete_all_food()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="все удалил")
    return ConversationHandler.END


async def get_gpt_recipes(update: Update, context: ContextTypes.DEFAULT_TYPE,
                          gpt_service=get_gpt_service()):
    recipes = await gpt_service.get_gpt_recipes()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=recipes)


async def get_specific_recipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Какие ингредиенты вы хотите видеть в рецепте?")
    return "asked_ingredients"


async def ingredient_selection(update: Update, context: ContextTypes.DEFAULT_TYPE,
                               recipe_service=get_recipe_service(),
                               gpt_service=get_gpt_service()):
    ingredients = update.effective_message.text
    ingredients_list = [ingredient.strip() for ingredient in ingredients.split(',')]
    recipes = await recipe_service.get_recipes_by_ingredients(ingredients_list)
    gpt_recipes = await gpt_service.get_specific_recipes(ingredients=ingredients_list)
    if recipes:
        await update.effective_message.reply_text(
            "Вот рецепты, которые можно приготовить с выбранными ингредиентами:\n" +
            "\n".join([f"{recipe.title}: {recipe.description}" for recipe in recipes],
                      )
        )
    if gpt_recipes:
        await update.effective_message.reply_text(text=gpt_recipes)


def setup():
    TOKEN = os.environ.get("TOKEN")

    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    Receipt_handler = ConversationHandler(
        entry_points=[CommandHandler('receipt', receipt), ],
        states={
            "asked_receipt": [MessageHandler(filters=PHOTO, callback=get_receipt)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(Receipt_handler)

    Menu_handler = ConversationHandler(
        entry_points=[CommandHandler('menu', menu), ],
        states={
            "asked_food": [CallbackQueryHandler(callback=pagination)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(Menu_handler)

    Specific_receipt_handler = ConversationHandler(
        entry_points=[CommandHandler('specific', get_specific_recipes)],
        states={
            "asked_ingredients": [MessageHandler(filters=TEXT, callback=ingredient_selection)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(Specific_receipt_handler)

    pagination_handler = CallbackQueryHandler(callback=pagination, pattern='^(next_page|prev_page|recipe_)$')

    application.add_handler(pagination_handler)
    delete_handler = CommandHandler('delete', delete_food)
    application.add_handler(delete_handler)
    gpt_handler = CommandHandler('gpt', get_gpt_recipes)
    application.add_handler(gpt_handler)
    return application
