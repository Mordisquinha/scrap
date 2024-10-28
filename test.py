# app.py

import streamlit as st
from main import scrape_site
import zipfile
import os

def main():
    st.title("Scraper de Links Quebrados")
    domain_to_scrape = st.text_input("Digite a URL do domínio que deseja verificar:")
    start_button = st.button("Iniciar Scraping")

    # Inicializando variáveis de logs
    log_text = ""
    broken_links_text = ""

    # Containers para logs e links quebrados
    log_container = st.empty()
    broken_links_container = st.empty()

    # Função de callback para atualizar os logs
    def update_log(log_message):
        nonlocal log_text
        log_text += log_message + "\n"
        
        html_content = (
            "<div style='height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px;'>"
            "<h3 style='text-align: center; margin: 0; padding: 0; font-weight: bold;'>Histórico de Logs</h3>"
            "<hr style='margin: 5px 0;'>"
            + log_text.replace("\n", "<br>") +
            "</div>"
        )

        log_container.markdown(html_content, unsafe_allow_html=True)

    # Função de callback para atualizar links quebrados
    def update_broken_links(broken_link):
        nonlocal broken_links_text
        broken_links_text += broken_link + "\n"
        
        html_content = (
            "<div style='height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px;'>"
            "<h3 style='text-align: center; margin: 0; padding: 0; font-weight: bold;'>Links quebrados encontrados</h3>"
            "<hr style='margin: 5px 0;'>"
            + broken_links_text.replace("\n", "<br>") +
            "</div>"
        )

        broken_links_container.markdown(html_content, unsafe_allow_html=True)

    # Executa o scraping ao clicar no botão
    if start_button and domain_to_scrape:
        log_directory = scrape_site(
            domain_to_scrape, 
            log_update_callback=update_log, 
            broken_links_callback=update_broken_links
        )

        st.success("Scraping concluído!")
        
        # Compacta o diretório de logs para download
        zip_path = f"{log_directory}.zip"
        with zipfile.ZipFile(zip_path, 'w') as log_zip:
            for root, _, files in os.walk(log_directory):
                for file in files:
                    log_zip.write(os.path.join(root, file),
                                  arcname=os.path.relpath(os.path.join(root, file), log_directory))
        
        st.download_button("Baixar logs", data=open(zip_path, "rb"), file_name=os.path.basename(zip_path))


if __name__ == "__main__":
    main()
