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

# Dicionário de Categorias
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
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ Use o formato correto:\n/gasto <valor> <descrição>\nExemplo: /gasto 45.90 Almoço")
        return

    valor = args[0].replace(',', '.')
    descricao = " ".join(args[1:])
    user_email = f"telegram_{update.effective_user.id}@bot.com" 
    
    categoria = identificar_categoria(descricao)

    try:
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

# --- NOVO COMANDO PARA CONSULTAR O TOTAL ---
async def consultar_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Busca todos os registros da tabela expenses
        response = supabase.table("expenses").select("amount").execute()
        registros = response.data

        if not registros:
            await update.message.reply_text("📊 Você ainda não tem gastos registrados.")
            return

        # Soma todos os valores encontrados
        total = sum(float(item["amount"]) for item in registros if item.get("amount"))

        await update.message.reply_text(f"💰 **Gasto Total Acumulado:** R$ {total:.2f}")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao consultar o total: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Registra os comandos do bot
    app.add_handler(CommandHandler("gasto", registrar_gasto))
    app.add_handler(CommandHandler("total", consultar_total))
    
    print("🤖 Bot do Telegram rodando com categorização e consulta de total...")
    app.run_polling()
