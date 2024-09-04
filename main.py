import logging
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update
from telegram.ext import CallbackContext

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Global Variables
ETHERSCAN_API_KEY = 'YourEtherscanAPIKey'
TELEGRAM_BOT_TOKEN = 'YourTelegramBotToken'
wallets = set()
whitelisted_tokens = set()

def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hello! Use /addwallet, /removewallet, /addtoken, /removetoken to manage the bot.')

def add_wallet(update: Update, context: CallbackContext):
    """Add a wallet address to the list."""
    wallet = ' '.join(context.args).strip().lower()
    if wallet:
        wallets.add(wallet)
        update.message.reply_text(f'Wallet {wallet} added.')
    else:
        update.message.reply_text('Usage: /addwallet <wallet_address>')

def remove_wallet(update: Update, context: CallbackContext):
    """Remove a wallet address from the list."""
    wallet = ' '.join(context.args).strip().lower()
    if wallet in wallets:
        wallets.remove(wallet)
        update.message.reply_text(f'Wallet {wallet} removed.')
    else:
        update.message.reply_text(f'Wallet {wallet} not found.')

def add_token(update: Update, context: CallbackContext):
    """Add a token contract address to the whitelist."""
    token = ' '.join(context.args).strip().lower()
    if token:
        whitelisted_tokens.add(token)
        update.message.reply_text(f'Token {token} added to whitelist.')
    else:
        update.message.reply_text('Usage: /addtoken <token_contract_address>')

def remove_token(update: Update, context: CallbackContext):
    """Remove a token contract address from the whitelist."""
    token = ' '.join(context.args).strip().lower()
    if token in whitelisted_tokens:
        whitelisted_tokens.remove(token)
        update.message.reply_text(f'Token {token} removed from whitelist.')
    else:
        update.message.reply_text(f'Token {token} not found in whitelist.')

def check_transactions(update: Update, context: CallbackContext):
    """Check for new transactions in the monitored wallets."""
    for wallet in wallets:
        url = f'https://api.etherscan.io/api?module=account&action=tokentx&address={wallet}&startblock=0&endblock=99999999&sort=asc&apikey={ETHERSCAN_API_KEY}'
        response = requests.get(url).json()
        if response['status'] == '1':
            for tx in response['result']:
                if tx['contractAddress'].lower() in whitelisted_tokens:
                    update.message.reply_text(
                        f"New Transaction:\n"
                        f"Wallet: {wallet}\n"
                        f"Token: {tx['tokenName']}\n"
                        f"Amount: {int(tx['value']) / (10 ** int(tx['tokenDecimal']))}\n"
                        f"From: {tx['from']}\n"
                        f"To: {tx['to']}\n"
                        f"TxHash: {tx['hash']}"
                    )
        else:
            update.message.reply_text(f"Error fetching transactions for wallet {wallet}.")

def main():
    """Start the bot."""
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Register command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("addwallet", add_wallet))
    dp.add_handler(CommandHandler("removewallet", remove_wallet))
    dp.add_handler(CommandHandler("addtoken", add_token))
    dp.add_handler(CommandHandler("removetoken", remove_token))
    dp.add_handler(CommandHandler("checktx", check_transactions))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
