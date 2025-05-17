import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters as Filters, ConversationHandler
import io
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os

TOKEN = '7638975526:AAFFnc_NRVkSIlxBV51GKTjwIZ1jupgOxrE'
GOOGLE_API_KEY = 'AIzaSyCjKdV7uL_UO_Ba1WKsMDmSFWR8Ak7xu_4'

genai.configure(api_key=GOOGLE_API_KEY)

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

model = genai.GenerativeModel(
    'gemini-2.0-flash',
    safety_settings=safety_settings
)

OBJETIVO, FOTO, ANALISAR_NOVAMENTE = range(3)

async def analisar_rotulo_com_gemini(image_data, objetivo):
    try:
        image_part = {
            "mime_type": "image/jpeg",
            "data": image_data
        }

        prompt = f"""Analise esta imagem do rótulo de um alimento para o objetivo de '{objetivo}'. 
        Classifique o alimento em uma das seguintes categorias, para uma pessoa leiga:
        Evite usar formatação Markdown como asteriscos ou underscores em sua resposta.
        Comece sua resposta com uma das seguintes classificações EM MAIÚSCULAS e em uma linha separada:
        - RECOMENDADO: Se o alimento é adequado para o objetivo.
        - AS_VEZES: Se o alimento pode ser consumido ocasionalmente, mas não é a melhor opção.
        - NAO_INDICADO: Se o alimento não é adequado ou pode prejudicar o objetivo.
        - NÃO_ALIMENTO: Se a imagem não contém um rótulo de alimento ou é ilegível.
        - CLASSIFICACAO_ERRO: Se houver um erro na classificação ou se a imagem não puder ser analisada.
        Após a classificação, de forma bem sucinta forneça um pequeno resumo do motivo da sua avaliação, 
        separando por topicos e destacando os  principais nutrientes ou informações relevantes para este objetivo.
        Sugira também uma quantidade ideal de consumo diário, se aplicável.
        E uma opção de substituição saudável, se possível.  """

        response = await model.generate_content_async([prompt, image_part])
        return response.text
    except Exception as e:
        print(f"Erro na API Gemini: {e}")
        return f"CLASSIFICACAO_ERRO\nErro ao analisar o rótulo com o Gemini: {e}"

async def start(update, context):
    context.user_data.clear()
    await update.message.reply_text(
        'Olá! Bem-vindo ao seu analisador de rótulos inteligente, o SherlockFood 🕵️.\n' # Adicionado emoji aqui
        'Por favor, escolha seu objetivo:\n'
        '1 - Emagrecimento\n'
        '2 - Vida Saudável\n'
        '3 - Consumo de Proteína',
        reply_markup=ReplyKeyboardRemove()
    )
    return OBJETIVO

async def processar_objetivo(update, context):
    texto = update.message.text
    if texto in ['1', '2', '3']:
        context.user_data['objetivo_numero'] = texto
        objetivos = {'1': 'emagrecimento', '2': 'vida saudável', '3': 'consumo de proteína'}
        objetivo_selecionado_texto = objetivos[texto]
        context.user_data['objetivo_texto'] = objetivo_selecionado_texto
        await update.message.reply_text(
            f'Você escolheu o objetivo: {objetivo_selecionado_texto}. Agora, por favor, envie uma foto nítida do rótulo do alimento.',
            reply_markup=ReplyKeyboardRemove()
        )
        return FOTO
    else:
        await update.message.reply_text('Opção inválida. Por favor, escolha 1, 2 ou 3.')
        return OBJETIVO

async def processar_foto(update, context):
    if not update.message.photo:
        await update.message.reply_text('Por favor, envie uma foto.')
        return FOTO

    photo_file = await update.message.photo[-1].get_file()
    
    image_byte_array = io.BytesIO()
    await photo_file.download_to_memory(image_byte_array)
    image_data = image_byte_array.getvalue()

    try:
        objetivo_texto = context.user_data.get('objetivo_texto')

        if not objetivo_texto:
            await update.message.reply_text('Objetivo não definido. Vou te ajudar a começar de novo.', reply_markup=ReplyKeyboardRemove())
            return await start(update, context)

        await update.message.reply_text('Analisando a imagem, por favor aguarde...')

        resposta_gemini_completa = await analisar_rotulo_com_gemini(image_data, objetivo_texto)
        
        linhas_resposta = resposta_gemini_completa.split('\n', 1)
        classificacao_bruta = linhas_resposta[0].strip().upper()
        resumo_gemini = linhas_resposta[1] if len(linhas_resposta) > 1 else "Não foi possível obter detalhes adicionais."

        mensagem_formatada = ""
        if "RECOMENDADO" in classificacao_bruta:
            mensagem_formatada = f"Com Certeza ✅\n\n{resumo_gemini}"
        elif "AS_VEZES" in classificacao_bruta:
            mensagem_formatada = f"Às vezes 🟡\n\n{resumo_gemini}"
        elif "NAO_INDICADO" in classificacao_bruta:
            mensagem_formatada = f"Melhor Não 🔴\n\n{resumo_gemini}"
        elif "NÃO_ALIMENTO" in classificacao_bruta: 
            mensagem_formatada = f"Não Identificado ❓\n\n{resumo_gemini}"
        else:
            if "CLASSIFICACAO_ERRO" in classificacao_bruta:
                 mensagem_formatada = resumo_gemini
            else:
                mensagem_formatada = f"Análise recebida:\n\n{resposta_gemini_completa}"


        await update.message.reply_text(mensagem_formatada)

        reply_keyboard = [['Sim', 'Não']]
        await update.message.reply_text(
            'Gostaria de analisar outro Alimento?',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return ANALISAR_NOVAMENTE

    except Exception as e:
        print(f"Erro em processar_foto: {e}")
        await update.message.reply_text(f'Ocorreu um erro ao processar a imagem: {e}', reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return ConversationHandler.END
    
async def processar_analisar_novamente(update, context):
    resposta_usuario = update.message.text.strip().lower()
    if resposta_usuario == 'sim':
        return await start(update, context)
    elif resposta_usuario == 'não' or resposta_usuario == 'nao':
        await update.message.reply_text('Ok! Obrigado por usar o SherlockFood 🕵️. Até a próxima!', reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return ConversationHandler.END
    else:
        await update.message.reply_text('Resposta inválida. Por favor, digite "Sim" ou "Não".')
        reply_keyboard = [['Sim', 'Não']]
        await update.message.reply_text(
            'Gostaria de analisar outro Alimento?',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return ANALISAR_NOVAMENTE

async def cancelar(update, context):
    context.user_data.clear()
    await update.message.reply_text('Operação cancelada.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    if TOKEN == 'SEU_TOKEN_TELEGRAM' or GOOGLE_API_KEY == 'SUA_GOOGLE_API_KEY':
        print("ERRO: Configure seu TOKEN do Telegram e sua GOOGLE_API_KEY no início do script!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(Filters.TEXT & ~Filters.COMMAND, start) # <<< ADICIONADO AQUI
        ],
        states={
            OBJETIVO: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, processar_objetivo)],
            FOTO: [MessageHandler(Filters.PHOTO, processar_foto)],
            ANALISAR_NOVAMENTE: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, processar_analisar_novamente)],
        },
        fallbacks=[CommandHandler('cancelar', cancelar)],
        # allow_reentry=True # Pode ser útil se você tiver comandos que podem ser chamados a qualquer momento para reiniciar
    )
    application.add_handler(conv_handler)

    print("Bot SherlockFood iniciado. Pressione Ctrl+C para parar.")
    application.run_polling()

if __name__ == '__main__':
    main()