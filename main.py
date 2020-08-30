import glob
import requests
import json
import pandas 
from bs4 import BeautifulSoup
from os.path import dirname, join

session = requests.Session()

current_dir = dirname(__file__)
file_path = join(current_dir, "./result/category-product/")

def bs_version():
    print(BeautifulSoup.__version__)

def get_category_url():

    url = 'https://www.gogobli.com/'
    res = session.get(url)
    res = BeautifulSoup(res.content, 'html5lib')
    category_list = res.find_all('div', attrs={'class':'dd-menu-item link'})
    urls = []
    no = 1
    for cl in category_list:
        node = cl.find('a')
        if node['href'].startswith(("#","https")):
            pass
        else :
            print (f'Get Menu...{no}')
            category = node['href']
            urls.append(category)
            no += 1
    
    return urls

def get_choosen_category(category):
    base_url = 'https://www.gogobli.com/'

    get_url = (base_url+category)

    return get_url

def pagination(link):
    page = 1
    url_with_page = (link+'?page={}'.format(page))

    res = session.get(url_with_page)
    res = BeautifulSoup(res.content, 'html.parser')

    all_pages = res.find('div', attrs={'class':'new-pagination pull-right'})
    page_data = []

    for page_count in all_pages.find_all('a'):
        page_list = page_count.get_text()
        page_data.append(page_list)
    
    page_number = len(page_data)
    page_num = ''

    if page_number == 4:
        page_num = page_data[2]
    elif page_number == 3:
        page_num = page_data[1]
    elif page_number == 1:
        page_num = page_data[0]
    
    all_url = []

    for page in range(int(page_num)):
        all_url.append(url_with_page)
        page += 1

    return all_url

def get_category_item_list(all_url):
    res = session.get(all_url)
    res = BeautifulSoup(res.content, 'html.parser')

    all_title = res.findAll('a', attrs={'class':'frame-item', 'href':True})
    data_titles = []

    for title in all_title:
        product_link = title['href']
        data_titles.append(product_link)
    
    return data_titles

def get_product_detail(url_product):
    base_url = 'https://www.gogobli.com'
    res = session.get(base_url+url_product)
    res = BeautifulSoup(res.content, 'html.parser')
    product_title = res.find('div', class_='col-md-10 hidden-xs nama-produk').find('h1').text.strip()
    product_brand = res.find('div', class_='col-md-10 hidden-xs nama-produk').find('a').text.strip()
    product_price = res.find('div', class_='price___').text.strip()
    try:
        product_price_with_discount = res.find('span', class_='red').text.strip()
    except: 
        product_price_with_discount = ''

    product_image = res.find('div', class_='foto-produk').findAll('a')
    data_image = []
    for image in product_image:
        data_image.append('http://www.gogobli.com/'+image['href'])

    product_description = res.find('div', class_='frame-desc-product').text.strip().replace('Deskripsi Produk','').replace("\n","").replace("\u00a0","").replace("\u00a0","")
    return {
        'product_title': product_title,
        'product_brand': product_brand,
        'product_price': product_price,
        'product_price_with_discount' : product_price_with_discount,
        'product_image': data_image,
        'product_description': product_description,
    }

def json_file(response, name_file):
    data = []
    for item in response:
        data.append(item)
    with open(f'./result/category-product/{name_file}.json', 'w') as outfile:
        json.dump(response, outfile)


def json_load(filename):
    with open(filename) as outfile:
        return json.load(outfile)

def csv_file(filename):
    data_product = []
    with open('./result/category-product/'+filename) as outfile:
        data = json.load(outfile)
        data_product = data

    csv = pandas.DataFrame(data_product)
    csv.to_csv(f'./result/csv-file-of-category-product/{filename.replace(".json", "-product")}.csv', index=False)

def get_all_category_product_json_file():
    files = sorted(glob.glob('./result/category-product/*.json'))
    return  files

def run():
    while True:
        menu = ''
        menu += '===================================\n'
        menu += '|| https://gogobli.com | SCRAPER ||\n'
        menu += '===================================\n'
        menu += 'Choose Menu :\n'
        menu += '1. Get All Category \n'
        menu += '2. Get All Item Of Category \n'
        menu += '3. Create CSV file of category product \n'
        menu += '4. Exit \n'
        menu += 'Input number : '

        option = int(input(menu))
        if option == 1:
            get_category_url()
            print("Getting All Category...")
            datas = get_category_url()
            with open(f'./result/all_category.json', 'w') as outfile:
                json.dump(datas, outfile)
                
        if option == 2:
            print('Getting All Product Of Category...')
            data = json_load('./result/all_category.json')
            no = 0
            for category in data:
                print(f"[{no}] => {category}")
                no += 1

            menu = 'Choose category for scrap: '
            option = int(input(menu))
            choosen_category = ''
            for key,value in enumerate(data):
                if key == option:
                    choosen_category = value

            link = get_choosen_category(choosen_category)

            product_detail = []

            current_pages = 1
            for current_page in range(int(len(pagination(link)))):
                print(f'Getting {choosen_category} category product, page {current_pages}...')
                all_page_numbers = pagination(link)
                all_page_number = all_page_numbers[current_page]
                current_page += 1
                current_pages += 1

                data = get_category_item_list(all_page_number)
                no = 1
                
                for item in data:
                    print(f'Getting product detail ...{no}')
                    product_detail.append(get_product_detail(item))
                    no += 1

            json_file(product_detail, choosen_category)
            print(f'Total Product is : {len(product_detail)}')
            print('Done...')

        if option == 3:
            data = get_all_category_product_json_file()
            choosen_file = ''
            no = 0
            for item in data:
                print(f'[{no}] => {item.replace("./result/category-product/", "")}')
                no += 1
            option = int(input('Choose file: '))
            choose = 0
            for item in data:
                if choose == option:
                    choosen_file = item.replace('./result/category-product/', '')
                choose += 1
            csv_file(choosen_file)
            print('Done...')

        if option == 4:
            exit()


if __name__ == "__main__":
    run()