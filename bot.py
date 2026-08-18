import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from supabase import create_client

# Suas credenciais
SUPABASE_URL = 'https://vrjqsjewututwtbqzxpx.supabase.co'
SUPABASE_KEY = 'sb_publishable_jUb90WHv_J6PRWv6S2H83g_-jTE_dhq'
TELEGRAM_TOKEN = '8862515812:AAGrSoltukHZ29qqDHrWgSA6eBL2jNJlhg0'

# Inicializa a conexão com o Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def registrar_gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # O comando no chat será: /gasto 45.90 Almoço
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ Use o formato correto:\n/gasto <valor> <descrição>\nExemplo: /gasto 45.90 Almoço")
        return

    valor = args[0].replace(',', '.') # Substitui vírgula por ponto se necessário
    descricao = " ".join(args[1:])
    user_email = f"telegram_{update.effective_user.id}@bot.com" # Identifica quem mandou

    try:
        # Insere na tabela 'expenses'
        data = {
            "user_email": user_email,
            "description": descricao,
            "amount": float(valor),
            "category": "Telegram"
        }
        
        supabase.table("expenses").insert(data).execute()
        await update.message.reply_text(f"✅ Gasto de R$ {valor} ('{descricao}') registrado com sucesso!")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao salvar no banco de dados: {str(e)}")

if __name__ == '__main__':
    # Inicializa o bot do Telegram
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("gasto", registrar_gasto))
    
    print("🤖 Bot do Telegram rodando...")
    app.run_polling()