from scrapy.item import Item, Field

class ModuleItem(Item):
    # All the details to be scraped
	code      = Field()
	name      = Field()
	desc      = Field()
	mc        = Field()
	exam_date = Field()
	exam_time = Field()
	prereq    = Field()
	preclu    = Field()
	workload  = Field()
	lectures  = Field()
	tutorials = Field()