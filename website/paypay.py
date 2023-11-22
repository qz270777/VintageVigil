from math import ceil

from .base.common_imports import *
from .base.scraper import BaseScrapy


class Paypay(BaseScrapy):
    def __init__(self):
        super().__init__(
            base_url="https://paypayfleamarket.yahoo.co.jp/api/v1/search", page_size=100
        )

    async def create_search_params(self, search, page: int) -> dict:
        return {
            "query": search.keyword,
            "results": self.pageSize,
            "imageShape": getattr(search, "imageShape", "square"),
            "sort": getattr(search, "sort", "ranking"),
            "order": getattr(search, "order", "ASC"),
            "webp": getattr(search, "webp", "false"),
            "module": getattr(search, "module", "catalog:hit:21"),
            "itemStatus": getattr(search, "itemStatus", "open"),
            "offset": (page - 1) * self.pageSize,
        }

    async def get_max_pages(self, search) -> int:
        res = await self.get_response(search, 1)
        data = json.loads(re.search(r"{.*}", res.text, re.DOTALL).group())
        max_pages = ceil(data["totalResultsAvailable"] / self.pageSize)
        return max_pages

    async def get_response_items(self, response):
        data = json.loads(re.search(r"{.*}", response, re.DOTALL).group())
        if not data or "items" not in data:
            return []  # 当get_response返回None或无有效数据时，返回空列表

        items = data["items"]
        return items

    async def create_product_from_card(self, item) -> SearchResultItem:
        name = await self.get_item_name(item)

        id = await self.get_item_id(item)

        product_url = await self.get_item_product_url(id)

        image_url = await self.get_item_image_url(item)

        price = await self.get_item_price(item)

        site = await self.get_item_site()

        search_result_item = SearchResultItem(
            name=name,
            price=price,
            image_url=image_url,
            product_url=product_url,
            id=id,
            site=site,
        )
        return search_result_item

    async def get_item_id(self, item):
        return item["itemid"]

    async def get_item_name(self, item):
        return item["title"]

    async def get_item_price(self, item):
        return item["price"]

    # TODO 目前TG服务器无法解析图片链接
    async def get_item_image_url(self, item):
        # 加上random=64，避免tg服务器无法解析链接
        image_url = item["thumbnailImageUrl"]
        image_url = image_url + "&random=64"
        return image_url

    async def get_item_product_url(self, id):
        product_url = "https://paypayfleamarket.yahoo.co.jp/item/{}".format(id)
        return product_url

    async def get_item_site(self):
        return "paypay"
