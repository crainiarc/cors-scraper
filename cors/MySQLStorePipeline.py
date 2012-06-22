from twisted.enterprise import adbapi
import datetime
import re
import MySQLdb.cursors
from scrapy import log
from scrapy.conf import settings

class MySQLStorePipeline(object):

    def __init__(self):
        # Connect to database
        self.dbpool = adbapi.ConnectionPool('MySQLdb',
            host        = settings['MYSQL_HOST'],
            db          = settings['MYSQL_DB'],
            user        = settings['MYSQL_USER'],
            passwd      = settings['MYSQL_PASS'],
            cursorclass = MySQLdb.cursors.DictCursor,
            charset     = 'utf8', use_unicode=True
        )

    def process_item(self, item, spider):
        """Insert the item to the database, handle the errors if it fails"""
        
        # run db query in thread pool
        query = self.dbpool.runInteraction(self._insert, item)
            
        query.addErrback(self.handle_error)
        return item
    
    def _insert(self, tx, item):
        """
        Insert the item to the modules and slots table. Should any of the
        intermediate transactions fail, it will rollback the query.
        """
        
        # Checks if the module code is a cross listed code format and
        # creates a list of module codes related that that particular module
        if re.compile('.+ / .+').match(item['code']):
            codes = item['code'].split(' / ')
        else:
            codes = [item['code']]
        
        # For every module code, we insert an entry to the database.
        for code in codes:
            # Insert an entry in the module table
            tx.execute(
                "insert into modules (code, name, description, workload, mc,"
                "prerequisite, preclusion, examdate, examtime) "
                "values (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (
                    code, item['name'], item['desc'], item['workload'],
                    item['mc'], item['prereq'], item['preclu'],
                    item['exam_date'], item['exam_time']
                )
            )
            
            # Get the row id of the current module inserted
            module_id = tx.lastrowid
            slot_re_obj = re.compile('.+\[(?P<slotcode>.+)\]$')
            
            # Insert lecture slots into the database
            if item['lectures']:
                for lecture in item['lectures']:
                    slot_re = slot_re_obj.match(lecture['name'])
                    slot_code = slot_re.group('slotcode')
                    
                    for session in lecture['sessions']:
                        tx.execute(
                            "insert into slots (code, module_id, starttime, "
                            "endtime, day, slot_type_id, location, occurrence)"
                            "values (%s, %s, %s, %s, %s, %s, %s, %s)", (
                                slot_code, module_id, session['starttime'],
                                session['endtime'], session['day'], 1,
                                session['location'], session['occurrence']
                            ) # slot type = 1 = lectures
                        )
            
            # Insert tutorial slots into the database
            if item['tutorials']:
                for tutorial in item['tutorials']:
                    slot_re = slot_re_obj.match(tutorial['name'])
                    slot_code = slot_re.group('slotcode')
                    
                    for session in tutorial['sessions']:
                        tx.execute(
                            "insert into slots (code, module_id, starttime,"
                            "endtime, day, slot_type_id, location, occurrence)"
                            "values (%s, %s, %s, %s, %s, %s, %s, %s)", (
                                slot_code, module_id, session['starttime'],
                                session['endtime'], session['day'], 2,
                                session['location'], session['occurrence']
                            ) # slot_type_id = 2 = tutorials
                        )
            
            # Database transaction complete!
            log.msg("Item stored in db: %s" % item, level=log.DEBUG)
    
    def handle_error(self, e):
        """Handles any errors in the database query."""
        log.err(e)
    