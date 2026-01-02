import requests
import csv
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

#csv文件路径
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(script_dir, 'store_data.csv')

#创建csv表头
with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Store Name', 'Address'])

#日本全国47都道府县循环爬取
for a in range(0, 47):
    url = "https://location.am-all.net/alm/location?gm=96&ct=1000&at={a}&lang=en".format(a=a)
    
    # Send an HTTP GET request to the website
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the response with the correct encoding
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding=response.encoding)

        # Find all <span class="store_name"> and <span class="store_address"> elements
        store_name_elements = soup.find_all("span", class_="store_name")
        store_address_elements = soup.find_all("span", class_="store_address")

        # Extract the text content of the <span> elements
        store_names = [element.text.strip() for element in store_name_elements]
        addresses = [element.text.strip() for element in store_address_elements]

        # Initialize a list to store the data
        data = []

        # Collect each store name and address
        for store_name, address in zip(store_names, addresses):
            data.append((store_name, address))

        # Append data to CSV file with utf-8-sig encoding
        with open(csv_file, 'a', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data)

        print(f"Successfully added {len(data)} stores to {csv_file}")
    else:
        print("Failed to retrieve the website content.")  

  