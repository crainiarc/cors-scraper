from datetime import date
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from cors.items import ModuleItem

class CorsSpider(CrawlSpider):
    """Scrapy Spider Class"""
    
    name = "cors"
    allowed_domains = ["nus.edu.sg"]
    start_urls = ["https://aces01.nus.edu.sg/cors/jsp/report/ModuleInfoListing.jsp"]
    rules = [Rule(SgmlLinkExtractor(allow="ModuleDetailedInfo\.jsp"), callback="parseModule")]
    
    def parseModule(self, response):
        """
        This method will be called for every module info link found in the
        module listing page.
        """
        
        # Scraping Raw Unicode Strings of the respective fields
        hxs = HtmlXPathSelector(response)
        details_obj = hxs.select("//div[@id='wrapper']/table/tr[2]/td/table[1]/tr[3]/td")
        module_obj = details_obj.select("table[1]")
        lecture_obj = details_obj.select("table[3]")
        tutorial_obj = details_obj.select("table[4]")
        
        # Extracting the data...
        code        = module_obj.select("tr[2]/td[2]/text()").extract()
        name        = module_obj.select("tr[3]/td[2]/text()").extract()
        desc        = module_obj.select("tr[4]/td[2]/text()").extract()
        mc          = module_obj.select("tr[7]/td[2]/text()").extract()
        exam        = module_obj.select("tr[6]/td[2]/text()").extract()
        prereq      = module_obj.select("tr[8]/td[2]/text()").extract()
        preclu      = module_obj.select("tr[9]/td[2]/text()").extract()
        workload    = module_obj.select("tr[10]/td[2]/text()").extract()
        
        # Create an array of lectures and tutorials
        lectures  = lecture_obj.select("tr[2]/td/div/table/tr[position()>1]")
        tutorials = tutorial_obj.select("tr[3]/td/div/table/tr[position()>1]")
        
        slots = []
        slots.extend(self._splitClasses(lectures))
        slots.extend(self._splitClasses(tutorials))
        
        # Reformat the exam date to ISO8601
        exam = exam[0].strip() if exam else u'null'
        if exam != "No Exam Date.":
            exam_dict = self._processExamDate(exam)
            exam_date = exam_dict['date']
            exam_time = exam_dict['time']
        else:
        	exam_date = None
        	exam_time = None
        
        # Start creating the Module Item for the next stage in the pipeline
        module              = ModuleItem()
        module['code']      = ' '.join(code[0].split()) if code else None
        module['name']      = name[0].strip() if name else None
        module['desc']      = desc[0]
        module['mc']        = mc[0].strip() if mc else None
        module['slots']     = slots
        module['exam_date'] = exam_date
        module['exam_time'] = exam_time
        module['prereq']    = prereq[0]
        module['preclu']    = preclu[0]
        module['workload']  = workload[0]
        
        return module

    def _processExamDate(self, exam):
        """
        Processes an exam date and returns a dict representation
    	@param exam string
    	@returns {date: <<date in ISO8601 format>>, time (no standard): <<AM or PM or EVE>>}
    	If there's an index error at any stage, this returns the original string
    	"""
    	
    	try:
    		t    = exam.split()
    		d    = t[0].split('-')
    		t[1] = t[1].upper() # Ensures that the time-code is standardised.
    		
    		if t[1] == "EVENING":
    		    t[1] = "EVE"
    		
    		return {'date': date(int(d[2]), int(d[1]), int(d[0])).isoformat(), 'time': t[1]}
    		
    	except IndexError:
    		return exam
    
    def _splitClasses(self, classes):
        """
        Takes in an XPath object containing the class slot and returns a list
        of dicts of the slot information.
        """
        
        slots = []
        
        for l in classes:
            code       = l.select("td[1]/text()").extract()
            slot_type  = l.select("td[2]/text()").extract()
            occurrence = l.select("td[3]/text()").extract()
            day        = l.select("td[4]/text()").extract()
            starttime  = l.select("td[5]/text()").extract()
            endtime    = l.select("td[6]/text()").extract()
            location   = l.select("td[7]/text()").extract()
            
            # Bug fix for lecturers that like to list a null lecture as a lecture slot
            if ' '.join(occurrence[0].split()) == 'There are no lectures for this module.':
                return []
            
            # Create the dict
            slots.append({
                "code"      : code[0] if code else None,
                "type"      : slot_type[0] if slot_type else None,
                "occurrence": occurrence[0] if occurrence else None,
                "day"       : day[0] if day else None,
                "starttime" : starttime[0] if starttime else None,
                "endtime"   : endtime[0] if endtime else None,
                "location"  : location[0] if location else None
            })
        
        return slots
    
