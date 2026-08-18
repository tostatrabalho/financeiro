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

# Dicionário de Categorias (adicione novas palavras conforme necessário)
REGRAS_CATEGORIAS = {
    "Alimentação": ["cafe", "almoco", "jantar", "lanche", "restaurante", "padaria", "ifood", "mercado", "supermercado"],
    "Transporte": ["uber", "gasolina", "onibus", "combustivel", "pedagio", "taxi"],
    "Lazer": ["cinema", "netflix", "jogo", "bar", "show", "ingresso"],
    "Moradia": ["aluguel", "luz", "agua", "internet", "condominio"]
}

def identificar_categoria(descricao):
    desc_lower = descricao.lower()
    for categoria, palavras in REGRAS_CATEGORIAS.items():
        if any(palavra in desc_lower for palavra in palavras):
            return categoria
    return "Outros"

async def registrar_gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # O comando no chat será: /gasto 45.90 Almoço
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ Use o formato correto:\n/gasto <valor> <descrição>\nExemplo: /gasto 45.90 Almoço")
        return

    valor = args[0].replace(',', '.') # Substitui vírgula por ponto
    descricao = " ".join(args[1:])
    user_email = f"telegram_{update.effective_user.id}@bot.com" 
    
    # Identifica a categoria automaticamente
    categoria = identificar_categoria(descricao)

    try:
        # Insere na tabela 'expenses'
        data = {
            "user_email": user_email,
            "description": descricao,
            "amount": float(valor),
            "category": categoria
        }
        
        supabase.table("expenses").insert(data).execute()
        await update.message.reply_text(f"✅ Gasto registrado!\nDescrição: {descricao}\nValor: R$ {valor}\nCategoria: {categoria}")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao salvar no banco de dados: {str(e)}")

if __name__ == '__main__':
    # Inicializa o bot do Telegram
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("gasto", registrar_gasto))
    
    print("🤖 Bot do Telegram rodando com categorização automática...")
    app.run_polling()
