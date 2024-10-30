# app.py

import streamlit as st
from main import scrape_site, scrape_sitemap_only
import zipfile
import os

def main():
    st.title("Scraper de Links Quebrados")
    domain_to_scrape = st.text_input("Digite a URL do domínio que deseja verificar:")
    only_sitemap = st.checkbox("Apenas Sitemap")  # Checkbox para a opção de apenas sitemap
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
        if only_sitemap:
            log_directory = scrape_sitemap_only(
                domain_to_scrape, 
                log_update_callback=update_log, 
                broken_links_callback=update_broken_links
            )

            st.success("Scraping concluído!")
        
            # Compacta o diretório de logs para download
            two_levels_up = os.path.dirname(os.path.dirname(log_directory))
            zip_path = os.path.join(two_levels_up, f"{os.path.basename(two_levels_up)}.zip")

            with zipfile.ZipFile(zip_path, 'w') as log_zip:
                for root, _, files in os.walk(two_levels_up):
                    for file in files:
                        log_zip.write(
                            os.path.join(root, file),
                            arcname=os.path.relpath(os.path.join(root, file), two_levels_up)
                        )
        else:
            log_directory = scrape_site(
                domain_to_scrape, 
                log_update_callback=update_log, 
                broken_links_callback=update_broken_links
            )

            st.success("Scraping concluído!")
        
            # Compacta o diretório de logs para download
            one_levels_up = os.path.dirname(log_directory)
            zip_path = f"{os.path.basename(one_levels_up)}.zip"

            with zipfile.ZipFile(zip_path, 'w') as log_zip:
                for root, _, files in os.walk(one_levels_up):
                    for file in files:
                        log_zip.write(
                            os.path.join(root, file),
                            arcname=os.path.relpath(os.path.join(root, file), one_levels_up)
                        )

        st.download_button("Baixar logs", data=open(zip_path, "rb"), file_name=os.path.basename(zip_path))
        st.balloons()

if __name__ == "__main__":
    main()