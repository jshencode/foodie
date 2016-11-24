import scrapy

from foodie_crawler.items import Restaurant
from foodie_crawler.utils import geocode

class FoodieSpider(scrapy.Spider):
    name = 'foodie_spider'
    start_urls = []
    cities = ["san-francisco", "los-angeles", "seattle", "new-york", "chicago", "vancouver"]
    for city in cities:
        url = 'https://www.thechihuo.com/%s/find/restaurants' % city
        start_urls.append(url)

    def parse(self, response):
        link_path = '//div[@class="list-list"]/div[@class="col-lg-12 col-md-12 col-sm-12 col-xs-12 list-item restaurant-list-item list-item-large"]/div[@class="list-item-main"]'
        links = response.xpath(link_path)
        for link in links:
            url = link.xpath('div[@class="list-item-thumb list-item-thumb-bg"]/@style').re_first(r'background-image: url\(\'(.*)\'\)')
            names = [name.strip() for name in link.xpath('div[@class="list-item-hd"]/h2[@class="h1 trimTextWithEllipsis"]/a/text()').extract_first(default="not_found").split("/")]
            # eg. 43767 Boscell Rd, Fremont,  CA 94538 (510) 657-8188
            address_phone_regex_us = r'\s*([^,]+)\s*,+\s*([^,]+)\s*,+\s*([A-Z]{2})\s*([0-9]{5})\s*(\([0-9]{3}\)\s*[0-9]{3}\-[0-9]{4})?' 
            # eg. 1995 Cornwall Avenue, Vancouver, BC V6J 1C9, Canada (604) 734-8971
            address_phone_regex_ca = r'\s*([^,]+)\s*,+\s*([^,]+)\s*,+\s*([A-Z]{2})\s*([A-Z1-9]{3}\s?[A-Z1-9]{3}),\s*Canada\s*(\([0-9]{3}\)\s*[0-9]{3}\-[0-9]{4})?' 
            full_address_phone = link.xpath('div[@class="list-item-hd"]/div[@class="address"]/text()').re(address_phone_regex_us)
            country = 'US'
            if not full_address_phone:
                country = 'Canada'
                full_address_phone = link.xpath('div[@class="list-item-hd"]/div[@class="address"]/text()').re(address_phone_regex_ca)
                
            if full_address_phone:
                restaurant = Restaurant()
                restaurant['url'] = url
                restaurant['names'] = names
                restaurant['address'] = full_address_phone[0]
                restaurant['city'] = full_address_phone[1]
                restaurant['state'] = full_address_phone[2]
                restaurant['zipcode'] = full_address_phone[3]
                restaurant['country'] = country
                restaurant['phone'] = full_address_phone[4]
                (lat, lng) = geocode(restaurant['address'], restaurant['city'], restaurant['state'], restaurant['zipcode'])
                if lat and lng:
                    restaurant['loc'] = {'type': 'Point', 'coordinates': [lng,lat]}
                yield restaurant
            else:
                print(link.xpath('div[@class="list-item-hd"]/div[@class="address"]/text()').extract())

        next_page = response.xpath('//ul[@class="pagination col-lg-12"]/li[@class="last"]/a/@href').extract_first()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
