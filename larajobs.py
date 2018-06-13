import re
from bs4 import BeautifulSoup

class LarajobsScraper:
    def __init__(self, browser, technologies, skillset):
        self.browser = browser
        self.url = 'http://www.larajobs.com'
        self.skillset = skillset
        self.technologies = technologies

    def scrape(self):
        """
        Scrape new job postings off Larajobs into a local db
        """
        res = self.browser.open(self.url)
        html = res.read()
        soup = BeautifulSoup(html,"html.parser")

        with open('page_log.txt', 'w') as log:
            log.write(html)

        jobs = self.get_jobs(soup)

        for job in jobs:
            try:
                self.browse_job_page(job['href'])
            except:
                continue

    def get_jobs(self, soup, preferred_location = 'remote'):
        """
        Get jobs and their data
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
                job['lara_job_id'] = str(self.get_job_id(job_a['href']))

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

    def browse_job_page(self, url):
        """
        Browse a job page to extract skillset required
        and information needed to apply
        """
        keywords = []

        res = self.browser.open(url)
        html = str(res.read()).lower()

        for tech in self.technologies:
            if tech.lower() in html:
                keywords.append(tech)

        emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", html)
        print emails

        print keywords

    def get_job_id(self, url):
        """
        Get id of job as on Larajobs
        """
        parts = url.split("/")
        return parts[-1:]