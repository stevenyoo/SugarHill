from BeautifulSoup import BeautifulSoup
from urllib2 import urlopen, URLError, HTTPError, HTTPCookieProcessor, build_opener, install_opener

class ParserOhio:
    def __init__(self):
        self.baseurl = 'http://procure.ohio.gov/proc/'
        self.listurl = self.baseurl + 'searchCurContracts.asp'

    def parse_list(self):
        soup = BeautifulSoup(urlopen(self.listurl).read())
        tables = soup.findAll('table', width='590')
        targetTable = tables[1]
        trs = targetTable.findAll('tr')

        for tr in trs[2:]:
            tds = tr.findAll('td')

            title = tds[0].getText()
            contract_type = tds[1].getText()
            market_type = tds[2].getText()
            index_num = tds[3].getText()
            contract_num = tds[4].getText()
            effective_date = tds[5].getText()
            expiration_date = tds[6].getText()
            vendor = tds[7].getText()

            aTag = tr.find('a')
            rfpUrl = aTag.get('href')

            if contract_type.lower() != "rfp":
                continue

##            print "title        :\t" + title
##            print "contract type:\t" + contract_type
##            print "market tpye  :\t" + market_type
##            print "index #      :\t" + index_num
##            print "contract #   :\t" + contract_num
##            print "effective date:\t" + effective_date
##            print "expiration date:\t" + expiration_date
##            print "vendor       :\t" + vendor
##            print "rfp url      :\t" + rfpUrl
##            break
            print rfpUrl
            #self.parser_rpf(self.base + rfpUrl)
            
    def parse_rfp(self, url):
        soup = BeautifulSoup(urlopen(url).read())
        tables = soup.findAll('table', width='100%')
        targetTable = tables[0]
        trs = targetTable.findAll('tr')

        for tr in trs:
            print tr
            tds = tr.findAll('td')
            

if __name__ == '__main__':
    
    parser = ParserOhio()
    #parser.parse_list()
    parser.parse_rfp('http://procure.ohio.gov/proc/viewContractsAwards.asp?contractID=11103')
    
    
