# encoding: utf-8
# Created on 2014-5-13
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from bookshelf.items import Book, BookDesc, Sections

class ItemHelper():

    @staticmethod
    def gene_book_item(name, source, author, source_name, home_spider):
        item = Book()
        item['name'] = name
        item['source'] = source
        item['source_name'] = source_name
        item['author'] = author
        item['homes'] = {home_spider : source}
        item['source_home_spider'] = home_spider
        return item

    @staticmethod
    def gene_book_desc_item(_id, desc):
        bc = BookDesc()
        bc['_id'] = _id
        bc['desc'] = desc
        return bc

    @staticmethod
    def gene_sections_item(source_short_name, source_zh_name, b_id, source, spider, secs, is_source):
        item = Sections()
        item['source_short_name'] = source_short_name
        item['source_zh_name'] = source_zh_name
        item['b_id'] = b_id
        item['source'] = source
        item['spider'] = spider
        item['secs'] = secs
        item['is_source'] = is_source
        return item

    @staticmethod
    def sections_2_doc(b_id, source_short_name, source_zh_name, url, is_source, name, crawl_time):
        return {
                'b_id' : b_id,
                'source_short_name' : source_short_name,
                'source_zh_name' : source_zh_name,
                'url' : url,
                'is_source' : is_source,
                'name' : name,
                'crawl_time' : crawl_time
                }
