import re
import sqlite3
from bs4 import BeautifulSoup

class LarajobsScraper:
    def __init__(self, browser, technologies, skillset):
        self.browser = browser
        self.url = 'http://www.larajobs.com'
        self.skillset = skillset
        self.technologies = technologies
        self.conn = sqlite3.connect('jobs.db')

    def scrape(self):
        """
        Scrape new job postings off Larajobs into a local db
        """
        res = self.browser.open(self.url)
        html = res.read()
        html = open('page_log.txt', 'r').read()
        soup = BeautifulSoup(html,"html.parser")

        with open('page_log.txt', 'w') as log:
            log.write(html)

        jobs = self.get_jobs(soup)

        for job in jobs:
            if not self.job_indexed(job['lara_job_id']):
                tech_stack, emails = self.browse_job_page(job['href'])

                if (tech_stack is not None) and (emails is not None):
                    self.save_job(job, tech_stack, emails)

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
        emails = []

        try:
            res = self.browser.open(url)
            html = str(res.read()).lower()
        except:
            return None, None

        for tech in self.technologies:
            if tech.lower() in html:
                keywords.append(tech.lower())

        emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", html)

        return keywords, emails

    def get_job_id(self, url):
        """
        Get id of job as on Larajobs
        """
        parts = url.split("/")
        return parts[len(parts) - 1]

    def job_indexed(self, job_id):
        """
        Check to see whether we are already tracking this job in our local db
        """
        db_id = 'lara_' + job_id

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM jobs WHERE job_id=?", (db_id,))

        rows = cur.fetchall()

        if len(rows):
            return True

        return False

    def save_job(self, job, tech_stack, emails):
        """
        Save a job into the local db
        """
        match = self.calculate_match(tech_stack)
        job_id = 'lara_' + job['lara_job_id']
        emails = ",".join(emails)
        title = job['title']
        url = job['href']
        company = job['company']
        applied = 0

        values = (job_id, title, company, emails, url, applied, match)

        sql = """INSERT INTO jobs(job_id, title, company, emails, url, applied, match)
                  VALUES(?, ?, ?, ?, ?, ?, ?)"""

        with self.conn:
            cur = self.conn.cursor()
            cur.execute(sql, values)

    def calculate_match(self, tech_stack):
        """
        Calculate how much user's skillset matches a company's tech
        stack
        """
        covered = 0

        if len(tech_stack) < 1:
            return 1

        skillset = [skill.lower() for skill in self.skillset]

        for tech in tech_stack:
            if tech in skillset:
                covered += 1

        return  round(float(covered) / len(tech_stack), 2)
