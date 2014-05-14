# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from scrapy.item import Item, Field

class Book(Item):
    # define the fields for your item here like:
    # name = Field()
    _id = Field()  # id
    name = Field()  # book name
    source = Field()  # first site link
    source_name = Field()  # first site name
    desc = Field()  # description
    author = Field()  # author
    homes = Field()  # first site and update site home page of book, is a dict, key: spider name
    source_home_spider = Field()  # this spider name for first site home page of book

class BookDesc(Item):
    _id = Field()  # id
    desc = Field()

class Sections(Item):
    b_id = Field()  # book id
    secs = Field()  # sections, is a OrderedDict, key is section's url, value is sections's name
    source_short_name = Field()  # section source site short name
    source_zh_name = Field()  # section source site zh name
    source = Field()  # book home page
    is_source = Field()  # is first?
    spider = Field()  # spider name
