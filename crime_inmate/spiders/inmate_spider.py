import scrapy
from datetime import datetime
from scrapy.selector import Selector
# from maine_inmates.items import MaineInmatesItem
# from maine_inmates.models import Base
# from sqlalchemy.orm import sessionmaker



class InmatesSpider(scrapy.Spider):
    name = 'inmates'
    allowed_domains = ["maine.gov"]
    start_urls = [
        'https://www1.maine.gov/cgi-bin/online/mdoc/search-and-deposit/search.pl?Search=Continue']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        yield scrapy.Request(
            url='https://www1.maine.gov/cgi-bin/online/mdoc/search-and-deposit/search.pl?Search=Continue',
            headers=self.search_headers(),
            body=self.search_body(),
            method='POST',
            callback=self.parse_results,
            dont_filter=True
        )

    def parse_results(self, response):
        cookie = response.headers.get('Set-Cookie').decode('utf-8')
        ids = response.css('table.at-data-table a::attr(href)').extract()
        for id in ids:
            yield scrapy.Request(
                url='https://www1.maine.gov/cgi-bin/online/mdoc/search-and-deposit/' + id,
                headers=self.header(cookie),
                callback=self.parse_data,
                dont_filter=True
            )

        next_url = response.css('a::attr(href)').get()
        if next_url:
            yield scrapy.Request(
                url='https://www1.maine.gov/cgi-bin/online/mdoc/search-and-deposit/' + next_url,
                headers=self.header(cookie),
                callback=self.parse_results,
                dont_filter=True
            )

    def parse_inner_page(self, response):
        data_rows = response.xpath('//table[@class="at-data-table"]/tr')
        parsed_data = []
        for row in data_rows:
            cells = row.xpath('.//td')
            if len(cells) >= 2:
                key = cells[0].xpath('string()').get().strip()
                value = cells[1].xpath('string()').get().strip()
                parsed_data.append(self.parse_data(key, value))

        return parsed_data

    def parse_data(self, response):
        link = response.url
        inmates_data_hash = self.get_maine_inmates(response, link)
        inmate_item = MaineInmatesItem(**inmates_data_hash)
        yield inmate_item

    def get_maine_inmates(self, response, link):
        inmitates_data_hash = {}
        inmitates_data_hash['full_name'] = self.data_fetcher(response, 'Last Name, First Name, Middle Initial:')
        inmitates_data_hash['first_name'], inmitates_data_hash['middle_name'], inmitates_data_hash['last_name'], inmitates_data_hash['suffix'] = self.name_split(inmitates_data_hash['full_name'])
        birthdate = self.data_fetcher(response, 'Date of Birth:')
        inmitates_data_hash['birthdate'] = self.get_date(birthdate)
        inmitates_data_hash['sex'] = self.data_fetcher( response, 'Gender:')
        inmitates_data_hash['race'] = self.data_fetcher(response, 'Race/Ethnicity:')
        inmitates_data_hash['data_source_url'] = link
        return inmitates_data_hash

    def get_date(self, date):
        try:
            date_obj = datetime.strptime(date, "%m/%d/%Y")
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            return None

    def name_split(self, full_name):
        suffix_name = None
        if ' - ' in full_name:
            name_splitting = [a.strip().replace(' - ', '-')
                              for a in full_name.split(',')]
            first_name = name_splitting[0]
            last_name = name_splitting[-1]
            if len(last_name.split(' ')) == 2:
                middle_name, last_name = last_name.split(' ')
            else:
                middle_name = None
        else:
            try:
                name_splitting = full_name.strip().split(' ')
                middle_name, last_name = None, None
                first_name = name_splitting[0]
                suffix_name = self.get_suffix(name_splitting)
                filtered_array = [s for s in name_splitting if s.upper() not in [
                    "JR", "JR.", "SR", "SR."]]
                if len(filtered_array) == 1:
                    middle_name, last_name = None, None
                elif len(filtered_array) == 2:
                    middle_name, last_name = None, filtered_array[-1]
                elif len(filtered_array) == 3:
                    middle_name, last_name = filtered_array[1], filtered_array[2]
                elif len(filtered_array) > 3:
                    middle_name, last_name = filtered_array[1], ' '.join(
                        filtered_array[2:])
            except:
                first_name, middle_name, last_name = None, None, None

        return self.remove_comma(first_name), self.remove_comma(middle_name), self.remove_comma(last_name), suffix_name

    def remove_comma(self, name):
        return name.replace(",", "") if name else name

    def get_suffix(self, name_splitting):
        suffix_value = None
        suffix_list = ["JR", "JR.", "SR", "SR."]
        suffix_matches = [
            s for s in name_splitting if s.upper() in suffix_list]
        if suffix_matches:
            suffix_value = suffix_matches[0]
        return suffix_value

    def data_fetcher(self, response, search_text, index=0):
        table = response.css('table.at-data-table')[0]
        values = table.xpath('.//td[contains(text(), "{}")]/following-sibling::td[1]//text()'.format(search_text)).getall()
        if values:
            return values[index].strip()
        else:
            return None

    def parse_image(self, response):
        # Parse the image here
        pass

    def search_headers(self):
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www1.maine.gov',
            'Referer': 'https://www1.maine.gov/cgi-bin/online/mdoc/search-and-deposit/search.pl?Search=Continue'
        }

    def header(self, cookie):
        return {
            'Cookie': cookie,
            'Referer': 'https://www1.maine.gov/cgi-bin/online/mdoc/search-and-deposit/search.pl?Search=Continue'
        }

    def search_body(self):
        return 'mdoc_number=&first_name=&middle_name=&last_name=&gender=&age_from=&age_to=&weight_from=&weight_to=&feet_from=&inches_from=&feet_to=&inches_to=&eyecolor=&haircolor=&race=&mark=&status=&location=&mejis_index=&submit=Search'


if __name__ == '__main__':
    import os
    from scrapy.cmdline import execute
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    SPIDER_NAME = InmatesSpider.name
    try:
        execute(
            [
                'scrapy',
                'crawl',
                SPIDER_NAME,
                '-s',
                'FEED_EXPORT_ENCODING=utf-8',
            ]
        )
    except SystemExit:
        pass
