# Scrapy settings for cors project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME    = 'cors'
BOT_VERSION = '1.0'

SPIDER_MODULES   = ['cors.spiders']
NEWSPIDER_MODULE = 'cors.spiders'
USER_AGENT       = '%s/%s' % (BOT_NAME, BOT_VERSION)

LOG_LEVEL = "INFO"

ITEM_PIPELINES = [
    'cors.SanitizeDataPipeline.SanitizeDataPipeline',
    'cors.MySQLStorePipeline.MySQLStorePipeline'
]

MYSQL_HOST  = "localhost"
MYSQL_USER  = "twf_user"
MYSQL_PASS  = "Cr2E1o3h79ynF8w"
MYSQL_DB    = "twf_db"
