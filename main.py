import re
from mechanize import *
from larajobs import LarajobsScraper

technologies = [
    'Vue.js', 'jQuery', 'Laravel', 'Javascript', 'PHP', 'MySQL'
]

br = Browser()
user_agent = 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'
br.addheaders = [('User-agent', user_agent)]
br.set_handle_robots(True)

scraper = LarajobsScraper(br, technologies, [])
scraper.scrape()