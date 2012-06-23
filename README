National University of Singapore (NUS) CORS Scrapper
====================================================

This project scrapes through the CORS website for module information, including lecture and tutorial timings and then stores it into a MySQL database.

The implementation was initially based on another project by shadowsun7 (https://github.com/shadowsun7/cors-api), however only the scrapper was used. Hence it is only fitting that this is listed as a separate project.

Dependencies
------------
You will need:
* Python interpreter
* Scrapy
* MySQLdb-python

and optionally, but recommended: VirtualEnv, which will create an isolated environment to install your dependencies.

Configuration
-------------
You will need to give cors/settings.py your MySQL database details so that scrapy will know where to dump them.

How to scrape
-------------
Simply change to the cors-scraper directory and run:

	scrapy crawl cors

The CORS spider will start to crawl through all the modules in the CORS website and dump the information into the database.
