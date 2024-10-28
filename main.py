import os
import re
import time
import requests
from bs4 import BeautifulSoup
from colorama import Fore, init
from urllib.parse import urljoin, urlparse

# Inicializando Colorama para colorir o terminal
init(autoreset=True)

def get_current_time():
    """Retorna o horário atual formatado"""
    return time.strftime("%Y-%m-%d %H:%M:%S")

def get_formatted_time():
    """Retorna data e hora no formato adequado para nome de arquivo"""
    return time.strftime("%Y-%m-%d_%H-%M")  # Mantém o formato H-M

def clean_url_for_filename(url):
    """Limpa o URL para que possa ser utilizado como nome de arquivo"""
    return re.sub(r'[^A-Za-z0-9]', '_', url)  # Substitui caracteres inválidos por "_"

def create_log_directories(site_url):
    """Cria uma pasta principal com o nome do domínio e uma subpasta com o timestamp"""
    site_name = re.sub(r'https?://(www\.)?|\.com|\.br|\.net|\.org|\.info|\.io|\.gov|\.edu|\.co|\.me|\.biz|\.mil|\.tv|\.cc', '', site_url)
    site_name = site_name.split('/')[0]  # Remove qualquer caminho após o nome do site
    timestamp = time.strftime("%Y-%m-%d_H%H-M%M")  # Formato desejado
    
    # Cria diretório principal com o nome do domínio
    main_directory = os.path.join(os.getcwd(), site_name)
    if not os.path.exists(main_directory):
        os.makedirs(main_directory)
    
    # Cria subdiretório com o timestamp da execução
    timestamp_directory = os.path.join(main_directory, timestamp)
    if not os.path.exists(timestamp_directory):
        os.makedirs(timestamp_directory)
    
    return timestamp_directory

def create_log_filenames(log_directory):
    """Cria nomes para o arquivo de log completo e o arquivo de links quebrados"""
    raw_log_filename = os.path.join(log_directory, "log_raw.txt")
    broken_links_filename = os.path.join(log_directory, "broken_links.txt")
    return raw_log_filename, broken_links_filename

def write_log_to_file(log_file, message):
    """Escreve o log no arquivo de log"""
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def write_broken_link_to_file(broken_links_file, broken_link_data):
    """Escreve as informações de links quebrados no arquivo específico"""
    with open(broken_links_file, "a", encoding="utf-8") as f:
        f.write(broken_link_data + "\n")

def print_log(log_file, message, status="info"):
    """Imprime logs coloridos no terminal e escreve no arquivo de log"""
    current_time = get_current_time()
    
    if status == "ok":
        formatted_message = f"🟢 [{current_time}] [OK] {message}"
        write_log_to_file(log_file, formatted_message)

        return f"{formatted_message}"
    
    elif status == "warning":
        formatted_message = f"⚠️  [{current_time}] [Aviso] {message}"
        write_log_to_file(log_file, formatted_message)

        return f"{formatted_message}"
    
    elif status == "error":
        formatted_message = f"❌ [{current_time}] [Erro] {message}"
        write_log_to_file(log_file, formatted_message)

        return f"{formatted_message}"
    
    else:
        formatted_message = f"[{current_time}] {message}"
        write_log_to_file(log_file, formatted_message)

        return formatted_message

def is_valid_url(url):
    """Checa se a URL tem um esquema válido (http ou https)"""
    parsed = urlparse(url)
    return parsed.scheme in ['http', 'https']

def clear_screen():
    """Limpa a tela parcialmente, mantendo a parte da página atual visível"""
    os.system('cls' if os.name == 'nt' else 'clear')

def explain_status_code(status_code):
    """Fornece uma breve explicação para o status code"""
    explanations = {
        404: "(inacessível)",
        500: "(erro no servidor)",
        403: "(protegido)",
        400: "(requisição inválida)",
        503: "(serviço indisponível)",
    }
    return explanations.get(status_code, "(erro desconhecido)")

def print_completion_message(log_file, base_domain, start_time):
    """Imprime uma mensagem de conclusão ao final do scraping com o tempo de duração"""
    current_time = get_current_time()
    end_time = time.time()  # Captura o horário de término
    duration = end_time - start_time  # Calcula o tempo de duração em segundos
    hours, remainder = divmod(int(duration), 3600)  # Converte para horas e obtém o restante
    minutes, seconds = divmod(remainder, 60)  # Converte o restante para minutos e segundos

    completion_message = (
        f"\n{'='*60}\n"
        f"🎉 [{current_time}] Parabéns! Todas as páginas dentro do domínio '{base_domain}' foram verificadas com sucesso!\n"
        f"🕒 Duração total do processo: {hours} horas, {minutes} minutos e {seconds} segundos."
        f"\n{'='*60}"
    )

    write_log_to_file(log_file, completion_message.strip())

    return completion_message

def scrape_site(start_url, log_update_callback=None, broken_links_callback=None):
    try:
        if log_update_callback:
                """Função principal para percorrer o site e identificar links quebrados"""
                start_time = time.time()  # Captura o horário de início do scraping
                
                if not is_valid_url(start_url):
                    # Adiciona "https://" se o usuário esqueceu de colocar
                    start_url = 'https://' + start_url

                # Criar diretórios e nomes de arquivo para logs
                log_directory = create_log_directories(start_url)
                raw_log_file, broken_links_file = create_log_filenames(log_directory)
                
                # Extrai o domínio base da URL inicial
                base_domain = urlparse(start_url).netloc

                visited = set()
                to_visit = [start_url]

                while to_visit:
                    url = to_visit.pop(0)

                    # Evita visitar a mesma página mais de uma vez
                    if url in visited:
                        continue
                    visited.add(url)

                    try:
                        # Limpa a tela e mostra a página atual no topo com o horário
                        clear_screen()
                        page_log = f"[{get_current_time()}] 🔎 Página atual: {url}\n{'='*50}"
                        log_update_callback(page_log)
                        write_log_to_file(raw_log_file, page_log)  # Também escreve o log da página no arquivo

                        # Faz a requisição HTTP para a página
                        response = requests.get(url)
                        
                        # Checa se a requisição foi bem-sucedida
                        if response.status_code == 404:
                            log_update_callback(print_log(raw_log_file, f"Problema na página {url} - Código: 404", status="error"))
                            continue

                        log_update_callback(print_log(raw_log_file, f"Acessando: {url}", status="ok"))

                        # Parse do conteúdo HTML
                        soup = BeautifulSoup(response.content, "html.parser")

                        # Encontrando todos os links na página
                        links = [urljoin(url, a.get('href')) for a in soup.find_all('a', href=True)]

                        for link in links:
                            # Verifica se o link é do mesmo domínio
                            link_domain = urlparse(link).netloc
                            if link_domain == base_domain and link not in visited:
                                try:
                                    link_response = requests.get(link)
                                    
                                    # Verifique se a página carregou corretamente
                                    if link_response.status_code == 404:
                                        explanation = explain_status_code(404)
                                        broken_link_data = f"❌ {{\n  página: {url},\n  link_quebrado: {link},\n  erro: Código 404 {explanation}\n}}"
                                        broken_links_callback(print_log(raw_log_file, f"Link quebrado encontrado na página {url}", status="error"))
                                        broken_links_callback(print_log(raw_log_file, broken_link_data, status="error"))
                                        write_broken_link_to_file(broken_links_file, broken_link_data)
                                    else:
                                        log_update_callback(print_log(raw_log_file, f"Link OK: {link}", status="ok"))

                                except Exception as e:
                                    # Captura a mensagem de erro e mantém apenas a parte relevante
                                    error_message = str(e).split("\n")[0]  # Pega apenas a primeira linha do erro
                                    broken_link_data = f"❌ {{\n  página: {url},\n  link_quebrado: {link},\n  erro: {error_message}\n}}"
                                    broken_links_callback(print_log(raw_log_file, f"Link quebrado encontrado na página {url}", status="error"))
                                    broken_links_callback(print_log(raw_log_file, broken_link_data, status="error"))
                                    write_broken_link_to_file(broken_links_file, broken_link_data)

                                # Adiciona novos links à lista de páginas para visitar
                                to_visit.append(link)

                    except Exception as e:
                        # Captura a mensagem de erro e mantém apenas a parte relevante
                        error_message = str(e).split("\n")[0]  # Pega apenas a primeira linha do erro
                        log_update_callback(print_log(raw_log_file, f"Erro ao acessar a página {url}: {error_message}", status="error"))

                log_update_callback(print_completion_message(raw_log_file, base_domain, start_time))

        return log_directory
    except:
        return log_directory
    

if __name__ == "__main__":
    # Exemplo de uso
    domain_to_scrape = input("Digite a URL do domínio que deseja verificar: ")
    scrape_site(domain_to_scrape)
