import telebot
import requests
from bs4 import BeautifulSoup
import csv
import random

# выносим номер телефона в глобальную перменную
phone_global = 0

# Передаю питону токен телеграма
bot = telebot.TeleBot("1155031589:AAE4TeZKUfBy7KHjCuZq8SAPUYgGYNKj-Pg")
state = dict()


@bot.message_handler(commands=['start'])
def handle_start(message):
    global state
    bot.send_message(message.from_user.id, 'Введите поисковой запроc:')
    state[message.from_user.id] = 'wait'


@bot.message_handler(content_types=['text'])
def handle_command(message):
    global state
    try:
        if state[message.from_user.id] == 'wait':
            inpt = str(message.text).replace(' ', '%20')
            if inpt[-1] == '+':
                inpt = inpt[:-1]
            else:
                pass

            URL = 'https://www.wildberries.ru/catalog/0/search.aspx?search={0}'.format(inpt)
            print(URL)


            FILE = '../res.csv'

            def get_html(url, params=None):
                HEADERS = {
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko)'
                                  ' Chrome/84.0.4147.135 Safari/537.36 OPR/70.0.3728.154', 'accept': '*/*'}

                r = requests.get(url, headers=HEADERS, params=params)
                return r

            def save_file(items, path):
                with open(path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow(['name', 'brandname', 'price', 'link', 'rating', 'discount', 'orders', 'comments','promo'])
                    for item in items:
                        writer.writerow([item['name'],
                                         item['brandname'],
                                         item['price'],
                                         item['link'],
                                         item['rating'],
                                         item['discount'],
                                         item['orders'],
                                         item['comments'],
                                         item['promo']])

            def get_pages_count(html):
                soup = BeautifulSoup(html, 'html.parser')
                pagination = soup.find_all('a', class_="pagination-item")
                print(len(pagination))
                return len(pagination) + 1

            #def get_pages_count(html):
             #   soup = BeautifulSoup(html, 'html.parser')
              #  pagination = soup.find('ul', class_="js-pagination-list").get('data-pages')
               # pagination2 = soup.find('div', class_="b-pagination-wrapper js-b-pagination-wrapper")
                #if pagination is None:
                 #   if pagination2 is None:
                  #      pagination = 0
                   # else:
                    #    pagination = pagination2
               # else:
                #    pass
                #print(pagination)
                #return int(pagination)

            def get_content(html):
                soup = BeautifulSoup(html, 'html.parser')
                items = soup.find_all('div', class_='dtList i-dtList j-card-item')
                goods = []
                counter = 0
                for item in items:
                    lines = open('dbjokes.txt').read().splitlines()
                    joke = random.choice(lines)
                    # Задаем основные поля с карточек товара

                    name = item.find('span', class_='goods-name c-text-sm').get_text(strip=True)
                    link = item.find('a', class_='ref_goods_n_p j-open-full-product-card').get('href')

                    if item.find('ins', class_="lower-price") is not None:
                        price = item.find('ins', class_="lower-price").get_text()
                    else:
                        price = item.find('span', class_="lower-price").get_text()

                    if item.find('strong', class_='brand-name c-text-sm') is None:
                        brandname = 'Неизвестный бренд'
                    else:
                        brandname = item.find('strong', class_='brand-name c-text-sm').get_text(strip=True)

                    if item.find('span', class_='price-sale active') is None:
                        discount = 0
                    else:
                        discount = item.find('span', class_='price-sale active').get_text(strip=True)

                    if item.find('span', class_='dtList-comments-count c-text-sm') is None:
                        comments = 0
                    else:
                        comments = item.find('span', class_='dtList-comments-count c-text-sm').get_text(strip=0)

                    if item.find('span', class_='c-stars-line-lg j-stars stars-line-sm star0') is not None:
                        rating = 0
                    elif item.find('span', class_='c-stars-line-lg j-stars stars-line-sm star1') is not None:
                        rating = 1
                    elif item.find('span', class_='c-stars-line-lg j-stars stars-line-sm star2') is not None:
                        rating = 2
                    elif item.find('span', class_='c-stars-line-lg j-stars stars-line-sm star3') is not None:
                        rating = 3
                    elif item.find('span', class_='c-stars-line-lg j-stars stars-line-sm star4') is not None:
                        rating = 4
                    elif item.find('span', class_='c-stars-line-lg j-stars stars-line-sm star5') is not None:
                        rating = 5
                    else:
                        rating = "Нет рейтинга"

                    if get_html(link).status_code == 200:
                        x = open('../html', 'w')
                        x.write(get_html(link).text)
                        x.close()
                        x = open('../html')
                        for line in x:
                            if line.find('ordersCount') != -1:
                                x = line.find('ordersCount')
                                y = line.find("qualityRate")
                                buy = line[x + 13:y - 2]
                            else:
                                pass
                        soup = BeautifulSoup(get_html(link).text, 'html.parser')
                        if soup.find('span', 'discount-tooltipster-value') is not None:
                            promo = soup.find('span', 'discount-tooltipster-value').get_text()
                        else:
                            promo = ''

                    goods.append({
                        'name': name,
                        'brandname': brandname,
                        'price': price,
                        'link': link,
                        'rating': rating,
                        'discount': discount,
                        'orders': buy,
                        'comments': comments,
                        'promo':promo
                    })
                    print("Спарсил товар: {0}".format(name))
                    counter += 1
                    if counter == 1:
                        bot.send_message(message.from_user.id, 'Я начал парсить. Ничего не трогай. \n'
                                                               'Пока держи анекдот: \n{0}'.format(joke))
                    elif counter % 20 == 0:
                        bot.send_message(message.from_user.id, 'Спарсил {0} товаров. Продолжаю работать. \n'
                                                               'Пока ничего не трогай и держи анекдот: \n\n'
                                                               '{1}'.format(counter, joke))

                return goods

                # for i in results:
                # print(i)
                # print(len(results))

            def parse():
                html = get_html(URL)
                if html.status_code == 200:  # Проверяем достучались ли мы до сервера. В таком случае код 200
                    res = []
                    pages_count = get_pages_count(html.text)
                    for page in range(1, pages_count + 1):
                        print('Парсинг страницы {0} из  {1}...'.format(page, pages_count))
                        html = get_html(URL, params={'page': page})
                        res.extend(get_content(html.text))
                    save_file(res, FILE)
                    for i in res:
                        print(i)
                    print("Бот спарсил {0} товаров.".format(len(res)))
                    doc = open(FILE, 'rb')
                    bot.send_document(message.from_user.id, doc)
                    doc.close()
                    bot.send_message(message.from_user.id, str("Бот спарсил {0} товаров.".format(len(res))))
                else:
                    print("Произошла ошибка")
                    bot.send_message(message.from_user.id, 'Ошибка интернет соединения')

            parse()
            bot.send_message(message.from_user.id, 'Введите поисковой запроc:')
            state[message.from_user.id] = 'wait'
        else:
            bot.send_message(message.from_user.id, 'Введите поисковой запроc:')
            state['message.from_user.id'] = 'wait'
    except KeyError:
        bot.send_message(message.from_user.id, 'Введите поисковой запроc:')
        state['message.from_user.id'] = 'wait'
    except AttributeError:
        bot.send_message(message.from_user.id, 'Произошла ошибка. \n\n'
                                               'Скорее всего поисковая выдача очень небольшая и легче сделать вручную. '
                                               'Либо результатов нет вовсе. '
                                               'Проверьте так ли это. Для удобства ссылка: msk.pulscen.ru \n'
                                               '\n'
                                               'В случае чего, пишите @aldiandadiani')

        state['message.from_user.id'] = 'wait'


try:
    bot.polling(none_stop=True, timeout=9999)
except Exception or ConnectionError as err:
    if ConnectionError is True:
        print("Bad Internet connection!")
    elif Exception is True:
        print("Internet error!")
