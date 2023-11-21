import csv
import json
import re
import requests
import re

from bs4 import BeautifulSoup
pattern = r"MLC-\d+"

# Function to extract JSON from the script text
def extract_json_from_script(script_text):
    json_pattern = re.compile(r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});', re.DOTALL)
    match = json_pattern.search(script_text)
    if match:
        json_string = match.group(1)
        return json_string
    return None

# Function to save JSON content to a file for debugging
def save_json_for_debugging(json_data, identifier):
    with open(f'preloaded_state_{identifier}.json', 'w', encoding='utf-8') as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)

# Function to save HTML content to a file for debugging
def save_html_for_debugging(html_content, identifier):
    with open(f'listing_{identifier}.html', 'w', encoding='utf-8') as file:
        file.write(html_content)

def scrape(url):
    headers = {
        # User-Agent and other headers
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve content: {response.status_code}")
        return None

filename = "identifiers.csv"

def parse(html_content):
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['ID', 'LINK'])
        soup = BeautifulSoup(html_content, 'html.parser')
        all_listings = soup.find_all('div', class_='ui-search-result__content no-borders')
        for listing in all_listings:
            listing_url = listing.find('a', class_='ui-search-link')['href']
            listing_id = re.search(pattern, listing_url).group()
            listing_content = scrape(listing_url)
            # Save the HTML content for each listing for debugging
            save_html_for_debugging(listing_content, listing_id)
            file_path = f'listing_{listing_id}.html'
            # Open the file and read its content
            html_content = None
            with open(file_path, 'r') as file:
                html_content = file.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            for script in soup.find_all('script'):
                if 'window.__PRELOADED_STATE__' in script.text:
                    json_string = extract_json_from_script(script.text)
                    if json_string:
                        try:
                            preloaded_state_json = json.loads(json_string)
                            return preloaded_state_json
                        except json.JSONDecodeError as e:
                            return None
            break

def main():
    html_content = scrape("https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/providencia-metropolitana#applied_filter_id%3DOPERATION_SUBTYPE%26applied_filter_name%3DModalidad%26applied_filter_order%3D5%26applied_value_id%3D244562%26applied_value_name%3DPropiedades+usadas%26applied_value_order%3D1%26applied_value_results%3D4134%26is_custom%3Dfalse")
    if html_content:
        return parse(html_content)

def parser_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps(main())
        }
