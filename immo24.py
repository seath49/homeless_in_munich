#!/usr/bin/env python3
import urllib.request
import re
import os
import time
import random
import datetime


# just get page data
def get_page(url):
    # html = requests.get(url).text
    # return BeautifulSoup(html, "lxml")
    # url = urllib.parse.quote(url)
    # print("From:", url)
    # url = urllib.parse.quote(url)

    # print("To:", url)
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req)
    return resp.read()


# immobilienscout24 link and caption extraction 
def parse_immo24(data):
    adverts = re.findall(r'<h5(.*?)</h5>', str(data))
    titles = []
    links = []
    # get link and caption
    for ad in adverts:
        # print('\nadvert: ')
        # print(ad)
        start = ad.find('-->')
        start += 3
        end = ad.find('<!--', start)
        this_ad_title = ad[start: end]
        titles.append(this_ad_title)
    # print('titles out: ', len(titles))
    return titles, links


def parse_wggs(data):
    ad_section = re.findall(r'<div class=\"col-xs-10(.*?)</div>', str(data))
    # print('ad_sec: ', ad_section)
    adverts = re.findall(r'<h3(.*?)</h3>', str(ad_section))
    # print('adverts: ', adverts)
    titles = []
    links = []

    # get link and caption
    # print(len(adverts))
    for ad in adverts:
        # print('\nadvert: ')
        # print(ad)
        if ad.find('immobilienscout24') != -1 or \
                ad.find('airbnb') != -1:  # or \
            # ad.find('noprint') != -1:
            # print('skippiing')
            continue

        start = ad.find('.html">')
        start += len('.html">') + 3
        end = ad.find('</a>', start)
        if start == -1 or end == -1:
            # print('sequence not found')
            continue
        this_ad_title = ad[start: end].strip()
        this_ad_title = this_ad_title[0: len(this_ad_title) - 3]
        titles.append(this_ad_title)
        # print('title: ', this_ad_title)
    # print('wg titles out: ', len(titles))
    return titles, links


# ebay kleineanzeigen
def parse_ebay(data):
    ad_section = re.findall(r'<li(.*?)</li>', str(data))
    adverts = re.findall(r'h2 class="text-module-begin(.*?)</h2>', str(ad_section))

    titles = []
    links = []
    # get link and caption
    for ad in adverts:
        # print('\nadvert: ')
        # print(ad)
        start = ad.find('">')
        start = ad.find('">', start + 2)
        start += 2
        end = ad.find('</a>', start)
        this_ad_title = ad[start: end]
        titles.append(this_ad_title)
        # print('titles out: ', this_ad_title)
    return titles, links


# quoka boards
def parse_quoka(data):
    ad_section = re.findall(r'<div id=\"ResultListData(.*?)<!-- id="ResultListData', str(data))
    # print(ad_section)
    adverts = re.findall(r'<h2 class="t-nowrap-overflow(.*?)</h2>', str(ad_section))
    # print(adverts)
    titles = []
    links = []
    # get link and caption
    for ad in adverts:
        # print('\nadvert: ')
        # print(ad)
        titles.append(ad)
        # print('titles out: ', this_ad_title)
    return titles, links


def parse_immonet(data):
    ad_section = re.findall(r'<a id=\"lnkToDetails_(.*?)</a>', str(data))
    # print('ad_section:', ad_section)
    adverts = re.findall(r'title=\"(.*?)">', str(ad_section))
    # print(ad_blocks)

    titles = []
    links = []
    # get link and caption
    for ad in adverts:
        # print('\nadvert: ')
        # print(ad)
        titles.append(ad)
        # print('titles out: ', this_ad_title)
    return titles, links


def parse_immowelt(data):
    adverts = re.findall(r'<h2 class=\"ellipsis\">(.*?)</h2>', str(data))
    del adverts[::2]
    # print('ad_section:', ad_section)
    # adverts = re.findall(r'title=\"(.*?)">', str(ad_section))
    # print(ad_blocks)

    titles = []
    links = []
    # get link and caption
    for ad in adverts:
        # print('\nadvert: ')
        # print(ad)
        titles.append(ad)
        # print('titles out: ', this_ad_title)
    return titles, links


def id2site(idx):
    if idx == 0:
        return 'immo24  '
    elif idx == 1:
        return 'wg-gs   '
    elif idx == 2:
        return 'ebay    '
    elif idx == 3:
        return 'quoka   '
    elif idx == 4:
        return 'immonet '
    elif idx == 5:
        return 'immowelt'


# url and parser_id struct
class url_:
    def __init__(self, address, parser):
        self.url = address
        self.parser_id = parser


# comapre to previous poll, check for new ad
def get_history_diff(history, titles, idx):
    new_ads = []
    # print('tits: ', len(titles))
    if len(history[idx]) == 0:
        # print('Initializing history container for id: ', idx)
        for tit in titles:
            history[idx].append(tit)
    else:
        # search if hisotry has title record
        record_exists = False
        for tit in titles:
            for his in history[idx]:
                if his == tit:
                    record_exists = True

            # if this
            if not record_exists:
                new_ads.append(tit)
                history[idx].append(tit)
    return new_ads


# if clearing history is a way to stop sending e-mails
def clear_new_posts(new_posts):
    size = len(new_posts)
    del new_posts[:]
    for nn in range(size):
        new_posts.append([])


################################################################################
# Setup


parser_immo24 = 0
parser_wggs = 1
parser_ebay = 2
parser_quoka = 3
parser_immonet = 4
parser_immowelt = 5

# addresses to check
urls = []

# immobilienscout24
# urls.append(url_('https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Bayern/Muenchen/-/-/-/EURO--900,00', parser_immo24))
# urls.append(url_('https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Bayern/Muenchen/Laim/-/-/EURO--900,00', parser_immo24))
# urls.append(url_('https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Bayern/Starnberg-Kreis/Gilching/-/-/EURO--900,00', parser_immo24))
# urls.append(url_('https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Bayern/Muenchen/Sendling/-/-/EURO--900,00', parser_immo24))
# urls.append(url_('https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Bayern/Muenchen/Schwabing-West/-/-/EURO--900,00', parser_immo24))
# urls.append(url_('https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Bayern/Muenchen/Maxvorstadt/-/-/EURO--900,00', parser_immo24))
# urls.append(url_('https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Bayern/Muenchen/Schwanthalerhoehe/-/-/EURO--900,00', parser_immo24))
# all Munich
# urls.append(url_('https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Bayern/Muenchen/-/-/-/EURO--900,00', parser_immo24))


urls.append(url_('https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Bayern/Muenchen/Pasing/-/-/EURO--900,00', parser_immo24))
urls.append(url_('https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Bayern/Muenchen/Nymphenburg/-/-/EURO--900,00', parser_immo24))
urls.append(url_('https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Bayern/Muenchen/Sendling-Westpark/-/-/EURO--900,00', parser_immo24))

# wggesucht - 1-zimmer wohnung
urls.append(url_('http://www.wg-gesucht.de/1-zimmer-wohnungen-in-Muenchen.90.1.1.0.html?offer_filter=1&stadt_key=90&sort_column=&sort_order=&autocompinp=M%C3%BCnchen&country_code=&countrymanuel=&city_name=&city_id=90&category=1&rent_type=2&sMin=&rMax=900&dFr=&hidden_dFrDe=&dTo=&hidden_dToDe=&radLat=&radLng=&radAdd=&radDis=0&ot[2124]=2124&ot[2127]=2127&ot[2129]=2129&ot[2132]=2132&ot[2133]=2133&ot[2134]=2134&ot[2139]=2139&hidden_wgFla=0&hidden_wgSea=0&hidden_wgSmo=0&hidden_wgAge=&hidden_wgMnF=0&hidden_wgMxT=0&sin=1&exc=0&hidden_rmMin=0&hidden_rmMax=0&pet=0&fur=0', parser_wggs))

# wggesucht - Wohnung
urls.append(url_('http://www.wg-gesucht.de/wohnungen-in-Muenchen.90.2.1.0.html?offer_filter=1&stadt_key=90&sort_column=0&sort_order=&autocompinp=M%C3%BCnchen&country_code=&countrymanuel=&city_name=&city_id=90&category=2&rent_type=2&sMin=&rMax=900&dFr=&hidden_dFrDe=&dTo=&hidden_dToDe=&radLat=&radLng=&radAdd=&radDis=0&ot[2124]=2124&ot[2127]=2127&ot[2129]=2129&ot[2132]=2132&ot[2133]=2133&ot[2134]=2134&ot[2139]=2139&hidden_wgFla=0&hidden_wgSea=0&hidden_wgSmo=0&hidden_wgAge=&hidden_wgMnF=0&hidden_wgMxT=0&sin=1&exc=0&rmMin=0&rmMax=0&pet=0&fur=0', parser_wggs))

# wggesucht - WG 
urls.append(url_('http://www.wg-gesucht.de/wg-zimmer-in-Muenchen.90.0.1.0.html?offer_filter=1&stadt_key=90&sort_column=0&sort_order=&autocompinp=M%C3%BCnchen&country_code=&countrymanuel=&city_name=&city_id=90&category=0&rent_type=2&sMin=&rMax=900&dFr=&hidden_dFrDe=&dTo=&hidden_dToDe=&radLat=&radLng=&radAdd=&radDis=0&ot[2124]=2124&ot[2127]=2127&ot[2129]=2129&ot[2132]=2132&ot[2133]=2133&ot[2134]=2134&ot[2139]=2139&wgFla=0&wgSea=0&wgSmo=0&wgAge=&wgMnF=0&wgMxT=0&sin=1&exc=0&hidden_rmMin=0&hidden_rmMax=0&pet=0&fur=0', parser_wggs))

# ebay
urls.append(url_('https://www.ebay-kleinanzeigen.de/s-wohnung-mieten/muenchen/anzeige:angebote/preis::900/c203l6411', parser_ebay))

# quoka all Munich
urls.append(url_('https://www.quoka.de/vermietung-wohnungen/vermietung-1-zimmer-wohnungen/muenchen/cat_21_2103_2070_ct_123976.html', parser_quoka))

# immonet.de all munich
urls.append(url_('https://www.immonet.de/immobiliensuche/sel.do?&sortby=0&suchart=1&objecttype=1&marketingtype=2&parentcat=1&toprice=900&city=121673&locationname=M%C3%BCnchen', parser_immonet))

# immowelt all munich
urls.append(url_('https://www.immowelt.de/liste/muenchen/wohnungen/mieten?prima=900&sort=createdate%2Bdesc', parser_immowelt))

# history
history = []
posts_to_check = []
new_post_counter = []

for url_item in urls:
    history.append([])
    posts_to_check.append([])
    new_post_counter.append(0)

for hitem in history:
    hitem = []

### parsing test
# data = get_page('https://www.immowelt.de/liste/muenchen/wohnungen/mieten?prima=900&sort=createdate%2Bdesc')
# parse_immowelt(data)
# quit()

#################################################################################
#### MAIN ###
titles = []
links = []
data = ""

start_of_search = datetime.datetime.now()
while True:
    for site in range(len(urls)):
        ### TODO: catch this
        data = get_page(urls[site].url)

        if urls[site].parser_id == parser_immo24:
            titles, links = parse_immo24(data)
        elif urls[site].parser_id == parser_wggs:
            titles, links = parse_wggs(data)
        elif urls[site].parser_id == parser_ebay:
            titles, link = parse_ebay(data)
        elif urls[site].parser_id == parser_quoka:
            titles, link = parse_quoka(data)
        elif urls[site].parser_id == parser_immonet:
            titles, link = parse_immonet(data)
        elif urls[site].parser_id == parser_immowelt:
            titles, link = parse_immowelt(data)

        # faster initialization
        if len(history[site]) == 0:
            pass
        else:
            # random time between 1~2 minutes
            time.sleep(random.uniform(60. / len(urls), 90. / len(urls)))

        new_ads = get_history_diff(history, titles, site)
        for idx in range(len(new_ads)):
            print(idx, ': ', new_ads[idx])
            posts_to_check[site].append(new_ads[idx])

        #### print status
        os.system('cls' if os.name == 'nt' else 'clear')
        now = datetime.datetime.now()
        mail_body = 'Advertisments you need to check from ' + now.strftime('%Y-%m-%d @ %H:%M') + '\n\n'
        send_new_mail = False

        print('Start of search:    ' + start_of_search.strftime('%Y-%m-%d @ %H:%M:%S'))
        print('Timestamp:          ' + now.strftime('%Y-%m-%d @ %H:%M:%S'))

        print(' id     website    cached_ads   new_ads')
        for idx in range(len(posts_to_check)):
            if idx == site:
                print("*%2d     %s       %2d         %2d" % (idx, id2site(urls[idx].parser_id), len(history[idx]), new_post_counter[idx]))
            else:
                print(" %2d     %s       %2d         %2d" % (idx, id2site(urls[idx].parser_id), len(history[idx]), new_post_counter[idx]))

        print('\n\n')
        for idx in range(len(posts_to_check)):
            for post in posts_to_check[idx]:
                print('Site ', idx, ': ', post)

                send_new_mail = True
                mail_body += post + '\n'
                mail_body += 'link: ' + urls[idx].url + '\n\n'

        if send_new_mail:
            # save temp file
            f = open('links', 'w')
            f.write(mail_body)
            f.close()

            command = 'echo " Hurry up! " | mail -s "!!! HOUSING ALERT !!!" -a links <YOUR_EMAIL>'
            os.system(command)

            # store how many posts were discovered already
            for idx in range(len(posts_to_check)):
                new_post_counter[idx] += len(posts_to_check[idx])

            # the new posts have been sent and can be cleared
            clear_new_posts(posts_to_check)
