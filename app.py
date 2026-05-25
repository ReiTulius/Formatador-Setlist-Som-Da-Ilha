import streamlit as st
import pandas as pd
import re
from datetime import datetime

# Configuração da página do aplicativo
st.set_page_config(page_title="Formatador Som da Ilha", page_icon="📻", layout="centered")

st.title("📻 Formatador de Roteiro - Som da Ilha")
st.markdown("Instruções: Carregue a planilha de contatos, cole o texto do Sysrad e clique em formatar.")

# 1. Upload da Planilha do Excel ou CSV
uploaded_file = st.file_uploader("1. Carregue sua planilha de Instagrams (.xlsx ou .csv)", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("Planilha carregada com sucesso!")
        
        # Padronizando o nome das colunas para evitar erros de digitação
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        col_artista = df.columns[0]
        col_insta = df.columns[1]
        
        banco_instagram = {}
        for _, linha_planilha in df.iterrows():
            nome_artista = str(linha_planilha[col_artista]).strip().lower()
            insta = str(linha_planilha[col_insta]).strip() if pd.notna(linha_planilha[col_insta]) else ""
            
            if insta.lower() in ["nan", "null", "none", "0"]:
                insta = ""
                
            banco_instagram[nome_artista] = insta

        # 2. Área para colar o texto do Sysrad
        texto_bruto = st.text_area("2. Cole aqui o roteiro bruto copiado do Sysrad:", height=250)

        # 3. Botão de Ação
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
                        
                        # Busca o instagram pelo artista principal
                        instagram = banco_instagram.get(artista_busca, "")
                        
                        # Monta a linha final
                        linha_final = f"{artista_original} - {musica_limpa} {instagram}".strip()
                        resultado.append(linha_final)
                
                texto_formatado = "\n".join(resultado)
                
                st.subheader("📋 Roteiro Pronto para as Redes Sociais:")
                st.text_area("Selecione tudo e copie:", value=texto_formatado, height=350)
                st.balloons()
            else:
                st.warning("Por favor, cole o roteiro do Sysrad antes de formatar.")
                
    except Exception as e:
        st.error(f"Erro ao processar o app. Erro técnico: {e}")
else:
    st.info("Aguardando o upload da planilha para liberar as próximas etapas.")