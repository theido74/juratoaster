import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin


URL_BASE = 'https://www.anibis.ch/fr'


def go_to_toaster_research():
    try:
        response = requests.get(URL_BASE)
        print(f"Status code Requests: {response.status_code}")
        response.raise_for_status()

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(URL_BASE)
            page.get_by_role("button", name="J'accepte").click()

            # Remplir le champ de recherche et cliquer sur le bouton "Cherchez"
            search_input = page.get_by_role("combobox", name="Que cherchez-vous?")
            search_input.fill('Toaster Jura')
            search_button = page.get_by_role("button", name="Cherchez")
            search_button.click()

            # Attendre que la page soit complètement chargée
            page.wait_for_load_state("networkidle", timeout=30000)

            # Récupérer l'URL après le clic sur le bouton "Cherchez"
            current_url = page.url
            print(f"Current URL: {current_url}")
                    
            # Fermer le navigateur
            browser.close()

            return current_url

        
    except requests.exceptions.RequestException as e:
        print(f'Il y a eu un problème lors de l acces au site')
        raise requests.exceptions.RequestException from e

def get_all_toaster_links():
# Récupérer le contenu HTML de la page avec l'URL récupérée
    current_url = go_to_toaster_research()
    response = requests.get(current_url)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')

    # Récupérer les liens
    link_tags = soup.find_all('a', class_='mui-style-blugjv')
    links = []
    for link_tag in link_tags:
        links.append(link_tag['href'])

    corrected_links = []
    for link in links:
        full_links = urljoin(URL_BASE,link)
        corrected_links.append(full_links)
    print('Nombre de Liens : ',len(corrected_links))

    price_list = []
    cp_list = []
    date_list = []
    description_list = []
    mixed_liste = []
    for link in corrected_links:
        response = requests.get(link)
        html = response.content
        soup = BeautifulSoup(html,'html.parser')
        price_tags = soup.find_all('dd', class_='ItemDetails_dlListValue__OaG_q')
        date_tags = soup.find('span', class_='MuiTypography-root MuiTypography-body1 ecqlgla1 mui-style-rn1u6h')
        descpriton_tags = soup.find('div', 'MuiBox-root mui-style-znb5ut')
        for price_tag in price_tags:
            price_span = price_tag.find('span', class_='MuiTypography-root MuiTypography-body1 ecqlgla1 mui-style-rn1u6h')
            if price_span:
                mixed_liste.append(price_span.get_text())
        for date_tag in date_tags:
            date_list.append(date_tag.text)
        for description in descpriton_tags:
            description_list.append(description.text)
    for i, nombre in enumerate(mixed_liste):
        if i % 2 == 0:
            price_list.append(nombre)
        else:
            cp_list.append(nombre)
    
    info_totale = []
    for i in range(len(corrected_links)):
        info_totale.append((corrected_links[i],price_list[i],date_list[i],description_list[i]))
    for info in info_totale:
        print('\033[1m\033[91mNEW TOASTER ON ANIBIS\033[0m')
        print(info)
        print()
    return info_totale


get_all_toaster_links()