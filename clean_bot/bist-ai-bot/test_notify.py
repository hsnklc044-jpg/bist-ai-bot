from tg.notifier import TelegramNotifier
from config import TOKEN, CHAT_ID


notifier = TelegramNotifier(
    TOKEN,
    CHAT_ID
)

notifier.notify(
    "🚀 Institutional Engine Active"
)