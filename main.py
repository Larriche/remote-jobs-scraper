import re
from mechanize import *
from bs4 import BeautifulSoup


technologies = [
    'Vue.js', 'jQuery', 'Laravel', 'Javascript', 'PHP', 'MySQL'
]

br = Browser()
user_agent = 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'
br.addheaders = [('User-agent', user_agent)]
br.set_handle_robots(False)

def get_jobs(soup, preferred_location = 'remote'):
    """
    Get information about jobs
    """
    jobs = []

    table = soup.find('table', {'class': 'jobs'})
    rows = table.findAll('tr')

    for tr in rows:
        job = {}

        columns = tr.findAll('td')
        col = None

        if len(columns):
            col = columns[0]
        else:
            continue

        job_a = col.find('a')
        info_wrap = col.find('div', {'class': 'job-wrap'})
        info_divs = info_wrap.findAll('div')
        location_div = info_divs[len(info_divs) - 1]
        location = str(location_div.getText()).strip()

        if (location.lower() == preferred_location.lower()):
            job['href'] = str(job_a['data-url'])
            job['lara_job_id'] = str(get_job_id(job_a['href']))

            company_section = info_divs[0].find('h4')
            description_section = info_divs[0].find('div', {'class': 'description'})
            new_label = company_section.find('div')

            if (new_label):
                job['company'] = str(new_label.findNext().getText()).strip()
            else:
                job['company'] = str(company_section.getText()).strip()

            if description_section:
                job['title'] = str(description_section.getText()).strip()
            else:
                job['title'] = ''

            jobs.append(job)

    return jobs

def get_job_id(url):
    """
    Get id of job as on Larajobs
    """
    parts = url.split("/")
    return parts[-1:]


def browse_job_page(url):
    """
    Browse a job page to extract skillset required
    and information needed to apply
    """
    keywords = []

    res = br.open(url)
    html = str(res.read()).lower()

    for tech in technologies:
        if tech.lower() in html:
            keywords.append(tech)

    emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", html)
    print emails

    print keywords


url = 'https://larajobs.com/'

res = br.open(url)
html = res.read()
soup = BeautifulSoup(html,"html.parser")

with open('page_log.txt', 'w') as log:
    log.write(html)

jobs = get_jobs(soup)

for job in jobs:
    browse_job_page(job['href'])