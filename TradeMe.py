from requests_html import HTMLSession
from apprise import Apprise
import time
a = Apprise()
a.add("discord://1123399583377145957/z25BS4vCfCu0zaOfKZ4QaIOdCYGtRR-o2pByeNnW0gsI3ypUSGwYuryJXQGHEzUNDiHV")
session = HTMLSession()
found = set()
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'}

cache = open("cache.txt", "r+")
def convert(text, link):
    lines = text.splitlines()
    addy = "n/a"
    for line in lines:
        if "Christchurch City" in line:
            addy = line
    bed = lines[lines.index("Bedrooms")+1]
    bath = lines[lines.index("Bathrooms")+1]
    try:
        park = lines[lines.index("Total parking")+1]
    except ValueError:
        park = "no information"
    ava = lines[lines.index(addy)+1]
    rent = lines[-1]
    rent_num = int(lines[-1].split('$')[-1].split()[0].replace(",", ""))/4
    return f'**{addy}**\n{ava}\nBedrooms: {bed}\nBathrooms: {bath}\nParking: {park}\n**{rent} (${rent_num})**\nLink: {link}'

while True:
    r = session.get('https://www.trademe.co.nz/a/property/residential/rent/search?suburb=2504&suburb=2280&suburb=2505&suburb=2101&suburb=2165&suburb=1993&suburb=2177&bedrooms_min=4&bedrooms_max=4&sort_order=expirydesc', headers=headers)
    r.html.render()

    flats = r.html.find('.tm-property-premium-listing-card__link')
    non_prem_flats = r.html.find('.tm-property-search-card__link')

    def is_good_start(x):
        for month in ['Aug', 'Sep', 'Oct', 'Jul', 'Now']:
            if month in x:
                return False
        return True
 
    flats = [x for x in flats if is_good_start(x.text)]
    non_prem_flats = [x for x in non_prem_flats if is_good_start(x.text)]
    for l in [flats, non_prem_flats]:
        while l:
            try:
                addy = l[0].find("tm-property-search-card-listing-address")[0].text
            except IndexError:
                addy = l[0].find("tm-property-search-card-listing-title")[0].text
            cache.seek(0)
            if addy not in cache.read().splitlines():
                details = convert(l[0].text, l[0].absolute_links.pop())
                print(details)
                a.notify(details, title="## New flat found!")
                cache.write("\n" + addy)
                cache.flush()
                l.pop(0)
            else:
                break
    time.sleep(600)