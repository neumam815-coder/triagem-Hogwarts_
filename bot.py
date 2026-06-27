import os
import json
from telegram import *
from telegram.ext import *

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1130170420

# IDs que podem refazer a triagem para testes
IDS_TESTE = [8672397104]

GRUPO_TRIAGEM_ID = -1003827066177
GRUPO_OFICIAL_ID = -1003553956365

BOT_USERNAME = "Expresso_Hogwarts_Bot"

NOME_GUARDIA = "🦉 Coruja da Biblioteca"

ARQUIVO_DADOS = "triagem_dados.json"

config_acesso = {
    "imagem_file_id": None,
    "mensagem": (
        "✨📜 Perfil verificado com sucesso!\n\n"
        "A Biblioteca de Hogwarts está pronta para receber você.\n\n"
        "Clique no botão abaixo para entrar.\n\n"
        "⚠️ Este acesso é único, não deve ser compartilhado e será removido após o uso."
    ),
    "texto_botao": "🏰 Entrar na Biblioteca de Hogwarts"
}

# ================= DADOS =================
usuarios = {}

# IMPORTANTE:
# fichas_alunos = SOMENTE fichas novas aguardando avaliação
fichas_alunos = {}

alunos_pendentes = {}
alunos_liberados = {}
alunos_reprovados = {}
alunos_entraram_triagem = {}
links_enviados = {}
historico_links = {}
alunos_no_oficial = {}

# ================= PERGUNTAS =================
perguntas = [
    "📚 Você gosta de romance?",
    "🖤 Você gosta de Dark Romance?",
    "✨ Você gosta de fantasia?",
    "📖 Você gosta de histórias de escola/adolescentes (Young Adult)?",
    "🌶️ Você gosta de livros hot/+18?",
    "👻 Você gosta de terror/horror?",
    "🔍 Você gosta de suspense/thriller?",
    "⚔️ Você gosta de Enemies to Lovers?",
    "💥 Você gosta de Rivals to Lovers?",
    "⏳ Você gosta de Age Gap/diferença de idade?",
    "🩶 Você gosta de personagens moralmente cinzentos?",
    "🖤 Você gosta de anti-heróis?",
    "💔 Você gosta de drama emocional forte?",
    "🔺 Você gosta de triângulo amoroso?",
    "🌑 Você gosta de temas sombrios?",
    "🔥 Você gosta de histórias intensas/pesadas?",
    "🎭 Você gosta de plot twist/reviravoltas?",
    "💍 Você gosta de final feliz?",
    "📚 Você gosta de séries/sagas longas?",
    "📘 Você prefere livros únicos?",
    "🔁 Você costuma reler livros favoritos?",
    "🆕 Você gosta de descobrir livros novos?",
    "⚡ Você prefere leitura rápida?",
    "📖 Você costuma ler com frequência?",
    "⏳ Você tem paciência para aguardar pedidos?",
    "📦 Você entende que nem todos os livros estarão disponíveis?",
]

# ================= SALVAR / CARREGAR =================
def salvar_dados():
    dados = {
        "usuarios": usuarios,
        "fichas_alunos": fichas_alunos,
        "alunos_pendentes": alunos_pendentes,
        "alunos_liberados": alunos_liberados,
        "alunos_reprovados": alunos_reprovados,
        "alunos_entraram_triagem": alunos_entraram_triagem,
        "links_enviados": links_enviados,
        "historico_links": historico_links,
        "alunos_no_oficial": alunos_no_oficial,
        "config_acesso": config_acesso,
    }

    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def carregar_dados():
    global usuarios, fichas_alunos, alunos_pendentes, alunos_liberados
    global alunos_reprovados, alunos_entraram_triagem, links_enviados
    global historico_links, alunos_no_oficial, config_acesso

    if not os.path.exists(ARQUIVO_DADOS):
        salvar_dados()
        return

    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except Exception:
        salvar_dados()
        return

    usuarios = dados.get("usuarios", {})
    fichas_alunos = dados.get("fichas_alunos", {})
    alunos_pendentes = dados.get("alunos_pendentes", {})
    alunos_liberados = dados.get("alunos_liberados", {})
    alunos_reprovados = dados.get("alunos_reprovados", {})
    alunos_entraram_triagem = dados.get("alunos_entraram_triagem", {})
    links_enviados = dados.get("links_enviados", {})
    historico_links = dados.get("historico_links", {})
    alunos_no_oficial = dados.get("alunos_no_oficial", {})

    config_salva = dados.get("config_acesso", {})
    config_acesso.update(config_salva)


def k(user_id):
    return str(user_id)


def ficha_do_aluno(user_key):
    if user_key in fichas_alunos:
        return fichas_alunos[user_key]
    if user_key in alunos_pendentes:
        return alunos_pendentes[user_key].get("ficha", "Ficha não encontrada.")
    if user_key in alunos_liberados:
        return alunos_liberados[user_key].get("ficha", "Ficha não encontrada.")
    if user_key in alunos_reprovados:
        return alunos_reprovados[user_key].get("ficha", "Ficha não encontrada.")
    return "Ficha não encontrada."


def tem_triagem_bloqueada(user_key):
    return (
        user_key in fichas_alunos
        or user_key in alunos_pendentes
        or user_key in alunos_liberados
        or user_key in alunos_reprovados
    )


def texto_perfil(context, user_id):
    try:
        tem_foto, tem_usuario, username = verificar_perfil(context, user_id)
    except Exception:
        tem_foto, tem_usuario, username = False, False, None

    username_txt = f"@{username}" if tem_usuario else "Sem usuário"
    perfil_link = f"tg://user?id={user_id}"
    foto_txt = "Sim" if tem_foto else "Não"

    return (
        f"🆔 ID Telegram: {user_id}\n"
        f"🔗 Usuário: {username_txt}\n"
        f"👁 Perfil: {perfil_link}\n"
        f"📸 Foto no perfil: {foto_txt}\n"
    )

# ================= TECLADO PROFESSORES =================
def teclado_professores():
    return ReplyKeyboardMarkup(
        [
            ["📜 Fichas Aguardando", "✅ Alunos Aprovados"],
            ["⚠️ Alunos Pendentes", "❌ Alunos Reprovados"],
            ["🧍 Entraram na Triagem", "🏰 Entraram no Oficial"],
            ["🔗 Links Enviados", "🎨 Personalizar Acesso"],
            ["🧪 Iniciar Teste"]
        ],
        resize_keyboard=True
    )


def teclado_personalizar():
    return ReplyKeyboardMarkup(
        [
            ["🖼 Alterar imagem do acesso"],
            ["✏️ Alterar mensagem do acesso"],
            ["🔘 Alterar texto do botão"],
            ["👁 Visualizar acesso"],
            ["🔙 Voltar"]
        ],
        resize_keyboard=True
    )


# ================= CONTROLE DE MODO ADMIN =================
def eh_botao_admin(texto):
    botoes = [
        "📜 Fichas Aguardando",
        "📜 Fichas dos Alunos",
        "✅ Alunos Aprovados",
        "🚪 Alunos Liberados",
        "⚠️ Alunos Pendentes",
        "❌ Alunos Reprovados",
        "🧍 Entraram na Triagem",
        "🧍 Alunos na Triagem",
        "🏰 Entraram no Oficial",
        "🔗 Links Enviados",
        "🎨 Personalizar Acesso",
        "🧪 Iniciar Teste",
        "🖼 Alterar imagem do acesso",
        "✏️ Alterar mensagem do acesso",
        "🔘 Alterar texto do botão",
        "👁 Visualizar acesso",
        "🔙 Voltar",
    ]
    return texto in botoes

# ================= START =================
def start(update, context):
    user_id = update.message.from_user.id

    if user_id == ADMIN_ID:
        context.user_data.clear()
        update.message.reply_text(
            f"🏰✨ Bem-vinda à Sala dos Professores!\n\n"
            f"{NOME_GUARDIA} está pronta para organizar as fichas dos alunos.",
            reply_markup=teclado_professores()
        )
        return

    user_key = k(user_id)

    if user_id not in IDS_TESTE and tem_triagem_bloqueada(user_key):
        if user_key in fichas_alunos:
            update.message.reply_text("📜 Sua triagem já foi finalizada e está aguardando avaliação dos professores.")
            return
        if user_key in alunos_pendentes:
            update.message.reply_text("⚠️ Sua ficha está pendente. Corrija foto/usuário e envie /verificar.")
            return
        if user_key in alunos_liberados:
            update.message.reply_text("✅ Você já foi aprovado e liberado para a Biblioteca de Hogwarts.")
            return
        if user_key in alunos_reprovados:
            update.message.reply_text("❌ Sua triagem já foi avaliada. Aguarde orientação dos professores.")
            return

    usuarios[user_key] = {"etapa": "nome"}

    # Se a pessoa começou a prova, ela fica como "em andamento"
    alunos_entraram_triagem.setdefault(user_key, {
        "nome": update.message.from_user.first_name,
        "username": update.message.from_user.username or "Sem usuário",
        "id": user_id,
        "status": "Começou a triagem"
    })
    alunos_entraram_triagem[user_key]["status"] = "Começou a triagem"
    salvar_dados()

    update.message.reply_text(
        f"{NOME_GUARDIA}\n\n"
        "🧪✨ Triagem Literária iniciada!\n\n"
        "Antes de receber o acesso ao grupo oficial Biblioteca de Hogwarts 🏰📖, "
        "responda sua avaliação.\n\n"
        "✨ Primeiro, diga seu nome:"
    )

# ================= NOVO MEMBRO NA TRIAGEM / OFICIAL =================
def novo_membro(update, context):
    chat_id = update.message.chat_id

    if chat_id == GRUPO_TRIAGEM_ID:
        for membro in update.message.new_chat_members:
            if membro.is_bot:
                continue

            user_id = membro.id
            user_key = k(user_id)
            nome = membro.first_name

            alunos_entraram_triagem[user_key] = {
                "nome": nome,
                "username": membro.username or "Sem usuário",
                "id": user_id,
                "status": "Entrou na triagem, mas ainda não finalizou"
            }
            salvar_dados()

            keyboard = [[
                InlineKeyboardButton(
                    "🧪 Fazer Triagem Literária",
                    url=f"https://t.me/{BOT_USERNAME}?start=triagem"
                )
            ]]

            context.bot.send_message(
                chat_id=GRUPO_TRIAGEM_ID,
                text=(
                    f"🦉✨ Seja bem-vindo(a), {nome}!\n\n"
                    "Você chegou à Plataforma 9¾ 🚂✨📖\n\n"
                    "Este é o grupo de entrada para quem deseja fazer parte do nosso grupo oficial:\n\n"
                    "🏰📖 Biblioteca de Hogwarts\n\n"
                    "📌 Requisitos obrigatórios:\n"
                    "• Ter uma imagem/foto no perfil\n"
                    "• Ter um usuário visível no Telegram, exemplo: @seunome\n\n"
                    "Clique no botão abaixo para fazer sua Triagem Literária:"
                ),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    elif chat_id == GRUPO_OFICIAL_ID:
        for membro in update.message.new_chat_members:
            user_id = membro.id
            user_key = k(user_id)

            passou_pela_triagem = (
                user_key in alunos_liberados
                or user_key in alunos_pendentes
                or user_key in alunos_reprovados
                or user_key in fichas_alunos
                or user_key in historico_links
            )

            alunos_no_oficial[user_key] = {
                "nome": membro.first_name,
                "username": membro.username or "Sem usuário",
                "id": user_id,
                "status": "Entrou após triagem" if passou_pela_triagem else "Entrou sem passar pela triagem"
            }

            if user_key in historico_links:
                historico_links[user_key]["status"] = "Entrou no grupo oficial"

            if user_key in alunos_liberados:
                alunos_liberados[user_key]["status"] = "Entrou no grupo oficial"

            if user_key in links_enviados:
                try:
                    context.bot.delete_message(
                        chat_id=user_id,
                        message_id=links_enviados[user_key]
                    )
                except Exception as erro:
                    print("Erro ao apagar link do PV:", erro)

                links_enviados.pop(user_key, None)

            salvar_dados()

# ================= MENU PROFESSORES =================
def menu_professores_texto(update, context):
    user_id = update.message.from_user.id
    texto = update.message.text

    if user_id != ADMIN_ID:
        return False

    if texto in ["📜 Fichas dos Alunos", "📜 Fichas Aguardando"]:
        mostrar_lista_fichas(update, context)
        return True

    if texto in ["✅ Alunos Aprovados", "🚪 Alunos Liberados"]:
        mostrar_liberados(update, context)
        return True

    if texto == "❌ Alunos Reprovados":
        mostrar_reprovados(update, context)
        return True

    if texto == "🏰 Entraram no Oficial":
        mostrar_entraram_oficial(update, context)
        return True

    if texto == "🔗 Links Enviados":
        mostrar_links_enviados(update, context)
        return True

    if texto == "⚠️ Alunos Pendentes":
        mostrar_pendentes(update, context)
        return True

    if texto in ["🧍 Entraram na Triagem", "🧍 Alunos na Triagem"]:
        mostrar_entradas_triagem(update, context)
        return True

    if texto == "🎨 Personalizar Acesso":
        update.message.reply_text(
            "🎨 Personalizar Acesso\n\nEscolha o que deseja alterar:",
            reply_markup=teclado_personalizar()
        )
        return True

    if texto == "🔙 Voltar":
        context.user_data.clear()
        update.message.reply_text("🏰 Sala dos Professores", reply_markup=teclado_professores())
        return True

    if texto == "🖼 Alterar imagem do acesso":
        context.user_data["modo_admin"] = "alterar_imagem_acesso"
        update.message.reply_text(
            "🖼 Envie agora a imagem/banner do acesso.\n\nPara remover a imagem, digite: remover",
            reply_markup=teclado_personalizar()
        )
        return True

    if texto == "✏️ Alterar mensagem do acesso":
        context.user_data["modo_admin"] = "alterar_mensagem_acesso"
        update.message.reply_text(
            "✏️ Envie agora a nova mensagem do acesso.\n\nEla aparecerá acima do botão de entrada.",
            reply_markup=teclado_personalizar()
        )
        return True

    if texto == "🔘 Alterar texto do botão":
        context.user_data["modo_admin"] = "alterar_botao_acesso"
        update.message.reply_text(
            "🔘 Envie agora o novo texto do botão.\n\nExemplo: 🏰 Entrar na Biblioteca",
            reply_markup=teclado_personalizar()
        )
        return True

    if texto == "👁 Visualizar acesso":
        enviar_preview_acesso(update, context)
        return True

    if texto == "🧪 Iniciar Teste":
        usuarios[k(user_id)] = {"etapa": "nome"}
        salvar_dados()
        update.message.reply_text("🧪 Teste iniciado.\n\n✨ Diga seu nome:")
        return True

    return False


# ================= PERSONALIZAÇÃO DO ACESSO =================
def processar_personalizacao_admin(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return False

    modo = context.user_data.get("modo_admin")
    if not modo:
        return False

    texto = update.message.text.strip() if update.message.text else ""

    if modo == "alterar_imagem_acesso":
        if update.message.photo:
            config_acesso["imagem_file_id"] = update.message.photo[-1].file_id
            salvar_dados()
            context.user_data.pop("modo_admin", None)
            update.message.reply_text("✅ Imagem do acesso atualizada.", reply_markup=teclado_personalizar())
            return True

        if texto.lower() == "remover":
            config_acesso["imagem_file_id"] = None
            salvar_dados()
            context.user_data.pop("modo_admin", None)
            update.message.reply_text("✅ Imagem removida do acesso.", reply_markup=teclado_personalizar())
            return True

        update.message.reply_text("⚠️ Envie uma imagem ou digite remover.")
        return True

    if modo == "alterar_mensagem_acesso":
        if not texto:
            update.message.reply_text("⚠️ Envie uma mensagem em texto.")
            return True
        config_acesso["mensagem"] = texto
        salvar_dados()
        context.user_data.pop("modo_admin", None)
        update.message.reply_text("✅ Mensagem do acesso atualizada.", reply_markup=teclado_personalizar())
        return True

    if modo == "alterar_botao_acesso":
        if not texto:
            update.message.reply_text("⚠️ Envie o texto do botão.")
            return True
        config_acesso["texto_botao"] = texto
        salvar_dados()
        context.user_data.pop("modo_admin", None)
        update.message.reply_text("✅ Texto do botão atualizado.", reply_markup=teclado_personalizar())
        return True

    return False


def enviar_preview_acesso(update, context):
    keyboard = [[InlineKeyboardButton(config_acesso["texto_botao"], url="https://t.me/preview")]]
    caption = f"{NOME_GUARDIA}\n\n{config_acesso['mensagem']}"

    if config_acesso.get("imagem_file_id"):
        update.message.reply_photo(
            photo=config_acesso["imagem_file_id"],
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
            protect_content=True
        )
    else:
        update.message.reply_text(
            caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
            protect_content=True
        )

# ================= LISTAS =================
def mostrar_lista_fichas(update, context):
    if not fichas_alunos:
        update.message.reply_text(
            "📜 Nenhuma ficha aguardando avaliação.\n\n"
            "Aqui só aparecem alunos que finalizaram a triagem e ainda não foram aprovados/reprovados.",
            reply_markup=teclado_professores()
        )
        return

    keyboard = []
    for uid in fichas_alunos:
        nome = usuarios.get(uid, {}).get("nome", str(uid))
        keyboard.append([InlineKeyboardButton(f"👤 {nome}", callback_data=f"ver_ficha_{uid}")])

    update.message.reply_text(
        "📜 Fichas Aguardando Avaliação\n\nEscolha uma ficha:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def mostrar_pendentes(update, context):
    if not alunos_pendentes:
        update.message.reply_text("⚠️ Nenhum aluno pendente no momento.", reply_markup=teclado_professores())
        return

    keyboard = []
    for uid in alunos_pendentes:
        nome = alunos_pendentes[uid].get("nome", str(uid))
        keyboard.append([InlineKeyboardButton(f"⚠️ {nome}", callback_data=f"ver_pendente_{uid}")])

    update.message.reply_text(
        "⚠️ Alunos Pendentes\n\nAqui ficam alunos que precisam corrigir foto/usuário. Você também pode liberar manualmente se conhecer a pessoa.\n\nEscolha um aluno:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def mostrar_liberados(update, context):
    if not alunos_liberados:
        update.message.reply_text("✅ Nenhum aluno aprovado/liberado ainda.", reply_markup=teclado_professores())
        return

    keyboard = []
    for uid, info in alunos_liberados.items():
        nome = info.get("nome", str(uid))
        keyboard.append([InlineKeyboardButton(f"✅ {nome}", callback_data=f"ver_aprovado_{uid}")])

    update.message.reply_text(
        "✅ Alunos Aprovados / Liberados\n\nAqui ficam somente alunos aprovados.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def mostrar_entradas_triagem(update, context):
    nao_finalizaram = {
        uid: info for uid, info in alunos_entraram_triagem.items()
        if uid not in fichas_alunos
        and uid not in alunos_pendentes
        and uid not in alunos_liberados
        and uid not in alunos_reprovados
    }

    if not nao_finalizaram:
        update.message.reply_text(
            "🧍 Nenhum aluno parado na triagem.\n\n"
            "Aqui só aparecem pessoas que entraram na triagem, mas ainda não finalizaram a prova.",
            reply_markup=teclado_professores()
        )
        return

    texto = "🧍 Entraram na Triagem e Ainda Não Finalizaram\n\n"
    for uid, info in nao_finalizaram.items():
        username = info.get("username", "Sem usuário")
        texto += f"👤 {info.get('nome', 'Sem nome')}\n🆔 ID: {uid}\n🔗 Usuário: {username}\n📌 Status: {info.get('status', 'Ainda não finalizou')}\n\n"

    update.message.reply_text(texto, reply_markup=teclado_professores())


def mostrar_reprovados(update, context):
    if not alunos_reprovados:
        update.message.reply_text("❌ Nenhum aluno reprovado ainda.", reply_markup=teclado_professores())
        return

    keyboard = []
    for uid, info in alunos_reprovados.items():
        nome = info.get("nome", str(uid))
        keyboard.append([InlineKeyboardButton(f"❌ {nome}", callback_data=f"ver_reprovado_{uid}")])

    update.message.reply_text(
        "❌ Alunos Reprovados\n\nAqui ficam somente alunos reprovados.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def mostrar_entraram_oficial(update, context):
    if not alunos_no_oficial:
        update.message.reply_text("🏰 Nenhum aluno entrou no grupo oficial ainda.", reply_markup=teclado_professores())
        return

    texto = "🏰 Alunos que Entraram na Biblioteca de Hogwarts\n\n"

    for uid, info in alunos_no_oficial.items():
        username = info.get("username", "Sem usuário")
        texto += (
            f"👤 Nome: {info.get('nome', 'Sem nome')}\n"
            f"🆔 ID: {uid}\n"
            f"🔗 Usuário: {username}\n"
            f"📌 Status: {info.get('status', 'Sem status')}\n\n"
        )

    update.message.reply_text(texto, reply_markup=teclado_professores())


def mostrar_links_enviados(update, context):
    if not historico_links:
        update.message.reply_text("🔗 Nenhum link enviado ainda.", reply_markup=teclado_professores())
        return

    texto = f"🔗 Links Enviados\n\nTotal: {len(historico_links)}\n\n"

    for uid, info in historico_links.items():
        texto += (
            f"👤 Nome: {info.get('nome', 'Sem nome')}\n"
            f"🆔 ID: {uid}\n"
            f"🔗 Usuário: @{info.get('username', 'Sem usuário')}\n"
            f"📌 Status: {info.get('status', 'Enviado')}\n\n"
        )

    update.message.reply_text(texto, reply_markup=teclado_professores())

# ================= TEXTO =================
def receber_texto(update, context):
    texto = update.message.text.strip() if update.message.text else ""

    # Se clicar em qualquer botão do painel, sai do modo de personalização.
    if update.message.from_user.id == ADMIN_ID and eh_botao_admin(texto):
        context.user_data.pop("modo_admin", None)

    # Botões do painel primeiro.
    if menu_professores_texto(update, context):
        return

    # Depois edição em andamento.
    if processar_personalizacao_admin(update, context):
        return

    if texto.lower() in ["verificar", "/verificar"]:
        verificar_usuario(update, context)
        return

    user_id = update.message.from_user.id
    user_key = k(user_id)

    if user_key not in usuarios:
        return

    etapa = usuarios[user_key]["etapa"]

    if etapa == "nome":
        usuarios[user_key]["nome"] = texto
        usuarios[user_key]["etapa"] = "idade"

        alunos_entraram_triagem.setdefault(user_key, {
            "nome": texto,
            "username": update.message.from_user.username or "Sem usuário",
            "id": user_id,
            "status": "Respondendo triagem"
        })
        alunos_entraram_triagem[user_key]["nome"] = texto
        alunos_entraram_triagem[user_key]["status"] = "Respondendo triagem"

        salvar_dados()
        update.message.reply_text("🎂 Agora diga sua idade:")

    elif etapa == "idade":
        usuarios[user_key]["idade"] = texto
        usuarios[user_key]["etapa"] = "q1"
        alunos_entraram_triagem.setdefault(user_key, {
            "nome": usuarios[user_key].get("nome", update.message.from_user.first_name),
            "username": update.message.from_user.username or "Sem usuário",
            "id": user_id,
            "status": "Respondendo triagem"
        })
        alunos_entraram_triagem[user_key]["status"] = "Respondendo triagem"
        salvar_dados()
        perguntar(context, user_id, 1)


def receber_midia(update, context):
    # Recebe imagem/banner da personalização.
    if processar_personalizacao_admin(update, context):
        return

# ================= PERGUNTAR =================
def perguntar(context, user_id, num):
    keyboard = [
        [
            InlineKeyboardButton("✅ Sim", callback_data=f"{num}_sim"),
            InlineKeyboardButton("❌ Não", callback_data=f"{num}_nao")
        ]
    ]

    context.bot.send_message(
        chat_id=user_id,
        text=f"{num}/{len(perguntas)}\n\n{perguntas[num-1]}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= RESPOSTAS =================
def responder(update, context):
    query = update.callback_query
    query.answer()

    user_id = query.from_user.id
    user_key = k(user_id)
    data = query.data

    if user_key not in usuarios:
        usuarios[user_key] = {"etapa": "nome"}
        salvar_dados()
        context.bot.send_message(
            chat_id=user_id,
            text="⚠️ Sua triagem foi reiniciada.\n\n✨ Diga seu nome:"
        )
        return

    num, resp = data.split("_")
    usuarios[user_key][f"q{num}"] = "Sim" if resp == "sim" else "Não"
    usuarios[user_key]["etapa"] = f"q{num}"

    if user_key in alunos_entraram_triagem:
        alunos_entraram_triagem[user_key]["status"] = f"Respondendo triagem ({num}/{len(perguntas)})"

    salvar_dados()

    proxima = int(num) + 1

    if proxima <= len(perguntas):
        perguntar(context, user_id, proxima)
    else:
        finalizar(context, user_id)

# ================= FICHA =================
def montar_ficha(user_id, context=None):
    user_key = k(user_id)
    dados = usuarios.get(user_key, {})
    nome = dados.get("nome", "Não informado")
    idade = dados.get("idade", "Não informado")

    perfil_extra = texto_perfil(context, user_id) if context else f"🆔 ID Telegram: {user_id}\n"

    texto = (
        f"{NOME_GUARDIA}\n\n"
        "🧪 FICHA DE ALUNO\n\n"
        f"👤 Nome: {nome}\n"
        f"🎂 Idade: {idade}\n"
        f"{perfil_extra}"
        "📌 Status: aguardando avaliação\n"
    )

    for i in range(1, len(perguntas) + 1):
        texto += f"\n{i}. {perguntas[i-1]}\nResposta: {dados.get(f'q{i}', 'Não respondeu')}\n"

    return texto


def finalizar(context, user_id):
    user_key = k(user_id)
    texto = montar_ficha(user_id, context)

    tem_foto, tem_usuario, username = verificar_perfil(context, user_id)

    if not tem_foto or not tem_usuario:
        motivos = []
        if not tem_foto:
            motivos.append("• Colocar uma imagem/foto no perfil")
        if not tem_usuario:
            motivos.append("• Criar ou atualizar seu usuário do Telegram, exemplo: @seunome")

        nome = usuarios.get(user_key, {}).get("nome", str(user_id))

        alunos_pendentes[user_key] = {
            "nome": nome,
            "motivos": motivos,
            "ficha": texto,
            "status": "Finalizou a triagem, mas precisa corrigir perfil antes da avaliação"
        }

        fichas_alunos.pop(user_key, None)

        if user_key in alunos_entraram_triagem:
            alunos_entraram_triagem[user_key]["status"] = "Finalizou triagem, mas ficou pendente de perfil"

        salvar_dados()

        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"{NOME_GUARDIA}\n\n"
                "⚠️ Uma ficha foi finalizada, mas o aluno ficou em Pendentes por falta de foto/usuário.\n\n"
                f"👤 Nome: {nome}\n"
                f"🆔 ID: {user_id}\n\n"
                "Pendências:\n" + "\n".join(motivos)
            )
        )

        context.bot.send_message(
            chat_id=user_id,
            text=(
                f"{NOME_GUARDIA}\n\n"
                "⚠️ Sua Triagem Literária foi finalizada, mas antes da avaliação você precisa organizar seu perfil:\n\n"
                + "\n".join(motivos) +
                "\n\nAssim que atualizar, volte aqui no PV da Coruja da Biblioteca e envie:\n\n"
                "/verificar\n\n"
                "Se não conseguir alterar esses detalhes, mande mensagem no grupo de triagem para que um dos professores/administradores possa te ajudar. ✨"
            )
        )
        return

    # Fichas dos alunos = somente aguardando aprovação
    fichas_alunos[user_key] = texto

    if user_key in alunos_entraram_triagem:
        alunos_entraram_triagem[user_key]["status"] = "Finalizou triagem, aguardando avaliação"

    salvar_dados()

    keyboard = [[
        InlineKeyboardButton("📜 Abrir Fichas Aguardando", callback_data="menu_fichas")
    ]]

    context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"{NOME_GUARDIA}\n\n"
            "📜 Uma nova ficha de aluno foi registrada.\n\n"
            "Ela está em: 📜 Fichas Aguardando."
        ),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.bot.send_message(
        chat_id=user_id,
        text=(
            "🔮✨ Sua Triagem Literária foi enviada para análise.\n\n"
            "Aguarde a resposta dos professores."
        )
    )

# ================= PERFIL / LINK =================
def verificar_perfil(context, user_id):
    chat = context.bot.get_chat(user_id)
    username = chat.username

    fotos = context.bot.get_user_profile_photos(user_id, limit=1)
    tem_foto = fotos.total_count > 0
    tem_usuario = username is not None and username.strip() != ""

    return tem_foto, tem_usuario, username


def criar_link_unico(context):
    link = context.bot.create_chat_invite_link(
        chat_id=GRUPO_OFICIAL_ID,
        member_limit=1
    )
    return link.invite_link


def enviar_link_unico(context, user_id, nome, username):
    user_key = k(user_id)
    link = criar_link_unico(context)

    keyboard = [[InlineKeyboardButton(config_acesso["texto_botao"], url=link)]]
    texto = f"{NOME_GUARDIA}\n\n{config_acesso['mensagem']}"

    if config_acesso.get("imagem_file_id"):
        msg = context.bot.send_photo(
            chat_id=user_id,
            photo=config_acesso["imagem_file_id"],
            caption=texto,
            reply_markup=InlineKeyboardMarkup(keyboard),
            protect_content=True
        )
    else:
        msg = context.bot.send_message(
            chat_id=user_id,
            text=texto,
            reply_markup=InlineKeyboardMarkup(keyboard),
            protect_content=True
        )

    links_enviados[user_key] = msg.message_id

    historico_links[user_key] = {
        "nome": nome,
        "username": username,
        "status": "Convite enviado em botão"
    }

    salvar_dados()

# ================= COMANDO VERIFICAR =================
def verificar_usuario(update, context):
    user_id = update.message.from_user.id
    user_key = k(user_id)
    nome = usuarios.get(user_key, {}).get("nome", update.message.from_user.first_name)

    if user_key not in alunos_pendentes and user_key not in alunos_liberados:
        update.message.reply_text(
            f"{NOME_GUARDIA}\n\n"
            "📜 Ainda não encontrei uma aprovação para você.\n\n"
            "Primeiro faça a Triagem Literária e aguarde a avaliação dos professores."
        )
        return

    tem_foto, tem_usuario, username = verificar_perfil(context, user_id)

    if tem_foto and tem_usuario:
        enviar_link_unico(context, user_id, nome, username)

        if user_key in alunos_pendentes:
            ficha = alunos_pendentes[user_key].get("ficha", ficha_do_aluno(user_key))
            alunos_pendentes.pop(user_key, None)
            alunos_liberados[user_key] = {
                "nome": nome,
                "username": username,
                "status": "Perfil corrigido, link enviado",
                "ficha": ficha
            }
            salvar_dados()

        context.bot.send_message(
            chat_id=GRUPO_TRIAGEM_ID,
            text=(
                "✨📜 Um aluno organizou seu perfil e foi liberado para a Biblioteca de Hogwarts! 🏰📖"
            )
        )
    else:
        pendencias = []

        if not tem_foto:
            pendencias.append("• Colocar uma imagem/foto no perfil")

        if not tem_usuario:
            pendencias.append("• Criar ou atualizar seu usuário do Telegram, exemplo: @seunome")

        alunos_pendentes[user_key] = {
            "nome": nome,
            "username": username or "Sem usuário",
            "motivos": pendencias,
            "ficha": ficha_do_aluno(user_key),
            "status": "Ainda precisa corrigir perfil"
        }
        salvar_dados()

        update.message.reply_text(
            f"{NOME_GUARDIA}\n\n"
            "⚠️ Ainda não conseguimos finalizar sua inscrição.\n\n"
            "Para entrar no grupo oficial Biblioteca de Hogwarts 🏰📖, organize estes detalhes:\n\n"
            + "\n".join(pendencias) +
            "\n\nAssim que atualizar, volte aqui no PV da Coruja da Biblioteca e envie:\n\n"
            "/verificar\n\n"
            "Se não conseguir alterar esses detalhes, mande mensagem no grupo de triagem "
            "para que um dos professores/administradores possa te ajudar. ✨"
        )

# ================= DECISÃO =================
def decisao(update, context):
    query = update.callback_query
    query.answer()

    acao, user_id = query.data.split("_")
    user_id = int(user_id)
    user_key = k(user_id)

    nome = usuarios.get(user_key, {}).get("nome", str(user_id))
    ficha = ficha_do_aluno(user_key)

    if acao == "aprovar":
        tem_foto, tem_usuario, username = verificar_perfil(context, user_id)

        # Sai de Fichas Aguardando
        fichas_alunos.pop(user_key, None)

        if not tem_foto or not tem_usuario:
            motivos = []

            if not tem_foto:
                motivos.append("• Colocar uma imagem/foto no perfil")

            if not tem_usuario:
                motivos.append("• Criar ou atualizar seu usuário do Telegram, exemplo: @seunome")

            alunos_pendentes[user_key] = {
                "nome": nome,
                "username": username or "Sem usuário",
                "motivos": motivos,
                "ficha": ficha,
                "status": "Aprovado, mas pendente de perfil"
            }

            salvar_dados()

            context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"{NOME_GUARDIA}\n\n"
                    "🦉📜 Sua ficha foi aprovada pelos professores!\n\n"
                    "Mas para finalizar sua inscrição e receber o acesso à Biblioteca de Hogwarts 🏰📖, "
                    "você precisa atualizar seu perfil:\n\n"
                    + "\n".join(motivos) +
                    "\n\nAssim que atualizar esses detalhes, volte aqui no PV da Coruja da Biblioteca e envie:\n\n"
                    "/verificar\n\n"
                    "A Coruja vai conferir novamente e, se estiver tudo certo, enviará o convite único do grupo oficial.\n\n"
                    "Se você não conseguir trocar esses detalhes, mande mensagem no grupo de triagem "
                    "para que um dos professores/administradores possa te ajudar. ✨"
                )
            )

            query.edit_message_reply_markup(reply_markup=None)
            query.message.reply_text("⚠️ Aluno movido para Alunos Pendentes.")
            return

        alunos_liberados[user_key] = {
            "nome": nome,
            "username": username,
            "status": "Aprovado, link enviado",
            "ficha": ficha
        }

        salvar_dados()
        enviar_link_unico(context, user_id, nome, username)

        context.bot.send_message(
            chat_id=GRUPO_TRIAGEM_ID,
            text=(
                "✨📜 Um novo aluno foi aprovado pelos professores!\n\n"
                "🏰📖 A Biblioteca de Hogwarts acaba de receber mais um membro."
            )
        )

        query.edit_message_reply_markup(reply_markup=None)
        query.message.reply_text("✅ Aluno movido para Aprovados e convite único enviado.")

    else:
        # Sai de Fichas Aguardando
        fichas_alunos.pop(user_key, None)

        alunos_reprovados[user_key] = {
            "nome": nome,
            "status": "Reprovado",
            "ficha": ficha
        }

        salvar_dados()

        context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ Sua entrada não foi aprovada no momento.\n\n"
                "Agradecemos por responder a Triagem Literária."
            )
        )

        query.edit_message_reply_markup(reply_markup=None)
        query.message.reply_text("❌ Aluno movido para Reprovados.")

# ================= CALLBACK MENUS =================
def menu_callback(update, context):
    query = update.callback_query
    query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    data = query.data

    if data == "menu_fichas":
        if not fichas_alunos:
            query.message.reply_text("📜 Nenhuma ficha aguardando avaliação.")
            return

        keyboard = []
        for uid in fichas_alunos:
            nome = usuarios.get(uid, {}).get("nome", str(uid))
            keyboard.append([InlineKeyboardButton(f"👤 {nome}", callback_data=f"ver_ficha_{uid}")])

        query.message.reply_text("📜 Fichas Aguardando:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("ver_ficha_"):
        uid = data.replace("ver_ficha_", "")
        ficha = fichas_alunos.get(uid, "Ficha não encontrada.")

        keyboard = [[
            InlineKeyboardButton("✅ Aprovar", callback_data=f"aprovar_{uid}"),
            InlineKeyboardButton("❌ Reprovar", callback_data=f"reprovar_{uid}")
        ]]

        query.message.reply_text(ficha, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("ver_aprovado_"):
        uid = data.replace("ver_aprovado_", "")
        query.message.reply_text(alunos_liberados.get(uid, {}).get("ficha", "Ficha não encontrada."))

    elif data.startswith("ver_reprovado_"):
        uid = data.replace("ver_reprovado_", "")
        query.message.reply_text(alunos_reprovados.get(uid, {}).get("ficha", "Ficha não encontrada."))

    elif data.startswith("ver_pendente_"):
        uid = data.replace("ver_pendente_", "")
        item = alunos_pendentes.get(uid)

        if not item:
            query.message.reply_text("Esse aluno não está mais pendente.")
            return

        motivos = "\n".join(item["motivos"])

        username = item.get("username") or usuarios.get(uid, {}).get("username") or "Sem usuário"
        if username != "Sem usuário" and not str(username).startswith("@"):
            username = "@" + str(username)

        perfil = f"tg://user?id={uid}"

        keyboard = [
            [InlineKeyboardButton("🔄 Verificar novamente", callback_data=f"reverificar_{uid}")],
            [InlineKeyboardButton("✅ Liberar mesmo com pendência", callback_data=f"liberar_forcado_{uid}")]
        ]

        query.message.reply_text(
            f"⚠️ Aluno Pendente\n\n"
            f"👤 {item.get('nome', uid)}\n"
            f"🆔 ID: {uid}\n"
            f"🔗 Usuário: {username}\n"
            f"👁 Perfil: {perfil}\n\n"
            f"Pendências:\n{motivos}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("liberar_forcado_"):
        uid = data.replace("liberar_forcado_", "")
        nome = usuarios.get(uid, {}).get("nome", alunos_pendentes.get(uid, {}).get("nome", str(uid)))

        try:
            chat = context.bot.get_chat(int(uid))
            username = chat.username or "Sem usuário"
        except Exception:
            username = "Sem usuário"

        ficha = alunos_pendentes.get(uid, {}).get("ficha", ficha_do_aluno(uid))

        alunos_pendentes.pop(uid, None)
        alunos_liberados[uid] = {
            "nome": nome,
            "username": username,
            "status": "Liberado manualmente pela professora, mesmo com pendência",
            "ficha": ficha
        }
        salvar_dados()

        enviar_link_unico(context, int(uid), nome, username)

        query.message.reply_text(
            "✅ Aluno liberado manualmente.\n\n"
            "A Coruja enviou o convite único no PV do aluno."
        )

    elif data.startswith("reverificar_"):
        uid = data.replace("reverificar_", "")
        nome = usuarios.get(uid, {}).get("nome", str(uid))

        tem_foto, tem_usuario, username = verificar_perfil(context, int(uid))

        if tem_foto and tem_usuario:
            ficha = alunos_pendentes.get(uid, {}).get("ficha", ficha_do_aluno(uid))
            alunos_pendentes.pop(uid, None)
            alunos_liberados[uid] = {
                "nome": nome,
                "username": username,
                "status": "Perfil corrigido, link enviado",
                "ficha": ficha
            }
            salvar_dados()
            enviar_link_unico(context, int(uid), nome, username)
            query.message.reply_text("✅ Perfil corrigido. Aluno movido para Aprovados e convite único enviado.")
        else:
            motivos = []

            if not tem_foto:
                motivos.append("• Ainda falta foto/imagem no perfil")

            if not tem_usuario:
                motivos.append("• Ainda falta usuário @ no Telegram")

            alunos_pendentes[uid]["motivos"] = motivos
            salvar_dados()

            query.message.reply_text("⚠️ O perfil ainda não está completo:\n\n" + "\n".join(motivos))

# ================= MAIN =================
def main():
    carregar_dados()

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("verificar", verificar_usuario))

    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, novo_membro))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, receber_texto))
    dp.add_handler(MessageHandler(Filters.photo, receber_midia))

    dp.add_handler(CallbackQueryHandler(menu_callback, pattern=r"menu_|ver_ficha_|ver_pendente_|reverificar_|liberar_forcado_|ver_aprovado_|ver_reprovado_"))
    dp.add_handler(CallbackQueryHandler(responder, pattern=r"\d+_(sim|nao)"))
    dp.add_handler(CallbackQueryHandler(decisao, pattern=r"(aprovar|reprovar)_"))

    print("🦉 Coruja da Biblioteca rodando com fichas organizadas por setor...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
