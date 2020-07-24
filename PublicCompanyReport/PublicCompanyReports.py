import requests
from bs4 import BeautifulSoup
from datetime import datetime

class PublicCompanyReports:
    def __init__(self, CIK):
        self.CIK = CIK
        self.url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={CIK}' + \
                    '&type={report_type}&dateb=&owner=exclude&start={start}&count=100'
        self.company_exist = self._check_company_exist()
        if not self.company_exist:
            print('Company not exist. Please try again.')

    def _check_company_exist(self):
        response = requests.get(self.url.format(CIK=self.CIK,report_type='',start=0))
        if 'No matching Ticker Symbol' in response.text:
            print('Company not exist. Please try again.')
            return False
        else:
            print('Company found.')
            return True

    def _get_link(self, link):
        # get each report html
        website2 = requests.get(link)
        soup2 = BeautifulSoup(website2.text, 'lxml')
        reportTable = soup2.findAll('table')[0]
        rows = reportTable.findAll('tr')[1:]
        row = rows[0]
        old_doc = link.split('.')[-1] == 'html'
        if old_doc:
            row = rows[-1]
        link = row.findAll('td')
        document = link[2]
        report_link = document.findAll('a')[0]['href']
        # original report link
        report_link = report_link.split('=')[-1]
        fullLink = 'https://www.sec.gov' + report_link
        return fullLink

    def getReports(self, report_type='', date_from=None, date_to=None):
        print('Fetching reports...')
        page = 0

        # deal with date
        if date_from is not None and date_to is not None:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()

        flag = True
        reports = []
        while flag:
            url = self.url.format(CIK=self.CIK, report_type=report_type, start=page * 100)
            website = requests.get(url)
            soup = BeautifulSoup(website.text, 'lxml')
            tables = soup.findAll('table')
            if(len(tables)==2):
                print('Invalid report filing.')
                break

            # get report table
            table = tables[2]
            # get each report link
            table = table.findAll('tr')
            if len(table) == 1:
                flag = False
            else:
                header = table[0]
                header = [i.text for i in header.findAll('th')]
                rows = table[1:]
                for row in rows:
                    info = row.findAll('td')
                    filing = info[header.index('Filings')].text
                    filing_date = datetime.strptime(info[3].text, '%Y-%m-%d').date()
                    if date_from is not None and date_to is not None \
                        and (filing_date<date_from or filing_date > date_to):
                        flag = False
                        break

                    link = 'https://www.sec.gov' + info[header.index('Format')].findAll('a')[0]['href']
                    link = self._get_link(link)
                    film_number = info[header.index('File/Film Number')].text.strip()
                    report = {'filling': filing, 'link': link, 'filling_date': filing_date, 'film_number': film_number}
                    reports.append(report)
                page += 1
        return reports

if __name__ == '__main__':
    tsla = PublicCompanyReports('tsla')
    tsla_reports = tsla.getReports(report_type='10-k',date_from='2008-01-01', date_to='2011-06-08')
    print(tsla_reports)
    print(len(tsla_reports))



