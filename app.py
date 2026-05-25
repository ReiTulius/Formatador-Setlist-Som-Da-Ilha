import streamlit as st
import pandas as pd
import re
from datetime import datetime

# Configuração da página do aplicativo
st.set_page_config(page_title="Formatador Som da Ilha", page_icon="📻", layout="centered")

st.title("📻 Formatador de Roteiro - Som da Ilha")
st.markdown("Instruções: Cole o texto do Sysrad e clique em formatar. A lista de Instagrams é atualizada automaticamente via Google Drive.")

# 🔗 COLE O LINK DA SUA PLANILHA DO GOOGLE AQUI ENTRE AS ASPAS:
URL_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1zkPm3F9W8QbOBhKvdV7jFCYqH-U8Qbru5w5TDyAHQLw/edit?usp=sharing"

# Função para converter o link normal do Google Sheets para o formato de exportação de dados (CSV)
def converter_link_google(url):
    if "docs.google.com/spreadsheets" in url:
        # Extrai o ID da planilha e força o formato de exportação
        id_planilha = url.split("/d/")[1].split("/")[0]
        return f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv"
    return url

# Carregamento dos dados em tempo real dos bastidores
@st.cache_data(ttl=300)  # Guarda na memória por 5 minutos para o site ficar super rápido
def carregar_banco_instagram(url):
    try:
        url_direta = converter_link_google(url)
        df = pd.read_csv(url_direta)
        
        # Padronizando o nome das colunas
        df.columns = [str(c).strip().lower() for c in df.columns]
        col_artista = df.columns[0]
        col_insta = df.columns[1]
        
        banco = {}
        for _, linha_planilha in df.iterrows():
            nome_artista = str(linha_planilha[col_artista]).strip().lower()
            insta = str(linha_planilha[col_insta]).strip() if pd.notna(linha_planilha[col_insta]) else ""
            
            if insta.lower() in ["nan", "null", "none", "0"]:
                insta = ""
                
            banco[nome_artista] = insta
        return banco, None
    except Exception as e:
        return {}, f"Erro ao conectar com o Google Drive: {e}"

# Tenta carregar o banco de dados automaticamente
if URL_GOOGLE_SHEETS == "SUA_URL_DO_GOOGLE_SHEETS_AQUI" or not URL_GOOGLE_SHEETS:
    st.error("⚠️ Configuração incompleta: O desenvolvedor precisa colocar o link do Google Sheets no código do app.py.")
else:
    banco_instagram, erro = carregar_banco_instagram(URL_GOOGLE_SHEETS)
    
    if erro:
        st.error(erro)
    else:
        # Se deu tudo certo, a interface fica limpa só com a área de texto!
        st.success("✅ Banco de dados dos artistas conectado e atualizado em tempo real!")

        # 1. Área para colar o texto do Sysrad
        texto_bruto = st.text_area("1. Cole aqui o roteiro bruto copiado do Sysrad:", height=250)

        # 2. Botão de Ação
        if st.button("Formatar Roteiro ✨", type="primary"):
            if texto_bruto:
                linhas = texto_bruto.split('\n')
                resultado = [datetime.now().strftime("%d/%m/%Y"), ""] 
                
                for linha in linhas:
                    linha = linha.strip()
                    if not linha or "Marcador" in linha or "Total:" in linha or "DescriçãoDuração" in linha:
                        continue
                    
                    # --- REMOÇÃO DE PARTICIPAÇÕES ---
                    linha = re.sub(r'\s*-\s*\(?part\.?[^)]+\)?\s*', ' ', linha, flags=re.IGNORECASE)
                    linha = re.sub(r'\s*\(?part\.?[^)]+\)?\s*', ' ', linha, flags=re.IGNORECASE)
                    
                    if " - " in linha:
                        partes = linha.split(" - ", 1)
                        artista_original = partes[0].strip()
                        artista_busca = artista_original.lower()
                        resto = partes[1]
                        
                        # --- LÓGICA DE LIMPEZA DA MÚSICA ---
                        padrao_corte = r'(\(comp|\(compa|Álbum|EP|Single|\d{4}|\d{2}:\d{2})'
                        musica_limpa = re.split(padrao_corte, resto, flags=re.IGNORECASE)[0].strip()
                        
                        musica_limpa = musica_limpa.rstrip('-').strip()
                        
                        # Busca o instagram
                        instagram = banco_instagram.get(artista_busca, "")
                        
                        linha_final = f"{artista_original} - {musica_limpa} {instagram}".strip()
                        resultado.append(linha_final)
                
                texto_formatado = "\n".join(resultado)
                
                st.subheader("📋 Roteiro Pronto para as Redes Sociais:")
                st.text_area("Selecione tudo e copie:", value=texto_formatado, height=350)
                st.balloons()
            else:
                st.warning("Por favor, cole o roteiro do Sysrad antes de formatar.")