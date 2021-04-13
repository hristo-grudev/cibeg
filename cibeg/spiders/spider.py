import scrapy
from scrapy import FormRequest

from scrapy.loader import ItemLoader

from ..items import CibegItem
from itemloaders.processors import TakeFirst


class CibegSpider(scrapy.Spider):
	name = 'cibeg'
	start_urls = ['https://www.cibeg.com/English/InvestorRelations/NewsGovernanceAndResearch/Pages/NewsReleases.aspx']

	def parse(self, response):
		post_links = response.xpath('//h3/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="AspNetPagerPrevNextButtonsClass"][text()=">"]/@href').getall()
		if next_page:
			argument = next_page[0].split(',')[1][1:-2]
			yield FormRequest.from_response(response, formdata={'__EVENTTARGET': 'ctl00$ctl54$g_1ed76902_160d_4564_ad61_d3b69cdf260c$ctl00$_aspNetContentPager', "__EVENTARGUMENT": f'{argument}'}, callback=self.parse)

	def parse_post(self, response):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@class="newsTextDetails"]//text()[normalize-space() and not(ancestor::span[@id="lblNewsPublishDate"])]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//span[@id="lblNewsPublishDate"]/text()').get()

		item = ItemLoader(item=CibegItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
