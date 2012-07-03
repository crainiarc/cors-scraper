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
                "INSERT INTO modules (code, name, description, workload, mc,"
                "prerequisite, preclusion, examdate, examtime) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (
                    code, item['name'], item['desc'], item['workload'],
                    item['mc'], item['prereq'], item['preclu'],
                    item['exam_date'], item['exam_time']
                )
            )
            
            # Get the row id of the current module inserted
            module_id = tx.lastrowid
            
            # Insert lecture slots into the database
            if item['slots']:
                for slot in item['slots']:
                    tx.execute("SELECT id, name FROM slot_types WHERE name='%s'" % slot['type'])
                    
                    # Get the slot type id
                    q = tx.fetchone()
                    if q == None:
                        # Insert a new slot type
                        tx.execute("INSERT INTO slot_types(name) VALUES ('%s')" % slot['type'])
                        slot_type_id = tx.lastrowid
                    else:
                        slot_type_id = q['id']
                    
                    tx.execute(self._generateSlotQueryString(slot, module_id, slot_type_id))
            
            # Database transaction complete!
            log.msg("Item stored in db: %s" % item, level=log.DEBUG)
    
    def _generateSlotQueryString(self, slot, module_id, slot_type_id):
        """Generates the slot insertion query string."""
        query = (
            "INSERT INTO slots(code, module_id, starttime, endtime, day, "
            "slot_type_id, location, occurrence) "
            "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                slot['code'], module_id, slot['starttime'], slot['endtime'],
                slot['day'], slot_type_id, slot['location'], slot['occurrence']
            )
        )
        
        return query
    
    def handle_error(self, e):
        """Handles any errors in the database query."""
        log.err(e)
    