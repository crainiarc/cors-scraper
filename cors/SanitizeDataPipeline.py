import re

class SanitizeDataPipeline(object):
    """Sanitize Data Class"""
    
    def process_item(self, item, spider):
        """Sanitizes the data so that it is safe to insert into MySQL"""
        
        item['desc'] = self._clean(item['desc']) if item['desc'] else None
        item['prereq'] = self._clean(item['prereq']) if item['prereq'] else None
        item['preclu'] = self._clean(item['preclu']) if item['preclu'] else None
        item['workload'] = self._clean(item['workload']) if item['workload'] else None
        
        # Reformat lectures and tutorials strings
        item['lectures']  = [lecture.strip() for lecture in item['lectures']]
        item['lectures']  = self._timeParse(item['lectures']) if item['lectures'] else None
        
        item['tutorials'] = [tutorial.strip() for tutorial in item['tutorials']]
        item['tutorials'] = self._timeParse(item['tutorials']) if item['tutorials'] else None
        
        return item
    
    def _timeParse(self, parse_list):
        """
    	This takes a list of parsed strings, like:

    		[u'DESIGN LECTURE Class [1]',
    		u'MONDAY From 1400 hrs to 1800 hrs in AKI2,',
    		u'Week(s): EVERY WEEK.',
    		u'THURSDAY From 1400 hrs to 1800 hrs in AKI2,',
    		u'Week(s): EVERY WEEK.',
    		u'Not Available in Tutorial Balloting yet.'],

    	and turns it into this:

    		[
    			{
    			'name': DESIGN LECTURE Class [1],
    			'sessions':
    					[{
    						'day': 1,
    						'starttime': '1400',
    						'endtime': '1800',
    						'location': 'AK12',
    						'occurence': [1,2,3,4,5,6,7,8,9,10,11,12,13]
    					}]
    			}
    		]

    		There can be many lecture classes in the list. There can also be
    		multiple sessions, which explains why the {day, starttime, endtime etc}
    		dict is stored in a list.
    	"""
    	
    	time = re.compile('(?P<day>\w+) From (?P<starttime>\d+) hrs to (?P<endtime>\d+) hrs in (?P<location>.+),')
    	occur = re.compile('Week\(s\): (.*?)\.')
    	ballot = re.compile('.*? Tutorial Balloting .*?')
    	nolecture = re.compile('.*? no lectures .*?')

    	res = []
    	pos = 0 # pos indicates tutorial or lecture position in the list
    	secondary = 0 # secondary indicates session number, for classes with multiple sessions

    	for l in parse_list:
    		time_re = time.match(l)
    		occur_re = occur.match(l)
    		ballot_re = ballot.match(l)

    		# Check if there are no lectures.
    		if nolecture.match(l):
    		    return None

    		if not time_re and not occur_re and not ballot_re:
    			# If there are no matches in the above regular expressions,
    			# that can only mean that it is the beginning of the new slot
    			# details, or the end of the list.
    			
    			# If res is empty and position is 0, assign the first line in
    			# the list to be the name.
    			if pos == 0 and not res:
    				res.append({'name': l})
    				
    			# If res is already populated and we know l exists
    			# then we know this is the next lesson slot.
    			elif l:
    				res.append({'name': l})
    				secondary = 0
    				pos += 1
    				
    			# otherwise, bugfix for added table that causes name to be empty.
    			else:
    				pass
    				
            # If the current line states the time...
    		if time_re:
    			day = time_re.group('day')
    			starttime = time_re.group('starttime')
    			endtime = time_re.group('endtime')
    			location = time_re.group('location')

    			curr_session = {
    			    'day': self._convertDay(day),
    				'starttime': starttime,
    				'endtime': endtime,
    				'location': self._clean(location)
    			}
    			
    			# If this is the first session
    			if secondary == 0:
    				res[pos]['sessions'] = [curr_session]
    			else:
    				res[pos]['sessions'].append(curr_session)

    		if occur_re: # If the current line states the occurrence
    			occurence = self._convertOccur(occur_re.group(1))
    			res[pos]['sessions'][secondary]['occurrence'] = occurence
    			
    			# Next line is read is either another session, or a new slot
    			# We increment the counter just in case...
    			secondary += 1
    			
    	return res
    
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
    