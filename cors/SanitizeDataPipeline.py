import re

class SanitizeDataPipeline(object):
    """Sanitize Data Class"""
    
    def process_item(self, item, spider):
        """Sanitizes the data so that it is safe to insert into MySQL"""
        
        item['desc'] = self._clean(item['desc']) if item['desc'] else None
        item['prereq'] = self._clean(item['prereq']) if item['prereq'] else None
        item['preclu'] = self._clean(item['preclu']) if item['preclu'] else None
        item['workload'] = self._clean(item['workload']) if item['workload'] else None
        item['slots']  = self._parseSlots(item['slots']) if item['slots'] else None
        
        return item
    
    def _parseSlots(self, slots):
        """Cleans up the slot dict to a more database-friendly format"""
        
        for slot in slots:
            slot["code"] = ' '.join(slot["code"].split()) if slot["code"] else None
            slot["type"] = self._clean(slot["type"])
            slot["day"]  = self._convertDay(slot["day"])
            
            slot["occurrence"] = self._clean(slot["occurrence"])
            slot["occurrence"] = self._convertOccur(slot["occurrence"])
        
        return slots
    
    def _convertDay(self, day):
    	"""Takes day as scraped, and converts it to number representations"""
    	
    	mapping = {
        	'MONDAY'    : 1,
        	'TUESDAY'   : 2,
        	'WEDNESDAY' : 3,
        	'THURSDAY'  : 4,
        	'FRIDAY'    : 5,
        	'SATURDAY'  : 6,
        	'SUNDAY'    : 7
        }
    	
    	return mapping.get(day, None)
    
    def _convertOccur(self, text):
        """
        Convert string of occurences to a string of weeks separated by spaces.
        """
        
    	def_weeks = ['1','2','3','4','5','6','7','8','9','10','11','12','13']
    	if text == "EVERY WEEK":
    		return u' '.join(def_weeks)
    	elif text == "EVEN WEEK":
    		return u' '.join(filter(lambda x: int(x) % 2 == 0, def_weeks))
    	elif text == "ODD WEEK":
    		return u' '.join(filter(lambda x: int(x) % 2 != 0, def_weeks))
    	else:
    		return u' '.join([e for e in text.split(',')])
    
    def _clean(self, text):
        """
        Removes \r and \n from text,
    	Converts unicode entities back to html/xml ones
    	Returns a null object if the text is a negative
    	"""
    	
    	text = u' '.join([w.strip() for w in text.split()])
    	text = text.encode('ascii', 'xmlcharrefreplace')
    	
    	# Checks if the text has as a null string or its equivalent...
    	t = text.lower()
    	if (t == 'null' or t == 'nil'
    	    or t == 'n/a' or t == 'n.a'
    	    or t == 'n.a.' or t == 'na' or t == 'none'):
    	    return None
    	
    	return text
    
