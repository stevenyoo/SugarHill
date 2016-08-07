import requests, hashlib, re, os, time
from bs4 import BeautifulSoup
from random import randint

class OpportunityParser: 
    def __init__(self):
        self.base_url = 'https://www.fbo.gov/index'

    def begin_parse(self, start_id=1, end_id=1292):
        for i in range(start_id, end_id+1):
            url = self.base_url + '?s=opportunity&mode=list&tab=list&pageID=' + str(i)
            html = read_html(url)
            op_pages = parse_search_list(html)

    ## make http request and return the response text
    def read_html(self, url):
        response = requests.get(url)

        if response.status_code is not 200:
            print 'FAILED to download', url
            print 'Status code:', response.status_code

        return response.text

    ## parse the search list and extract the opportunity page link
    def parse_search_list(self, html):
        op_pages = []
        soup = BeautifulSoup(html)
        for td in soup.findAll('td', {'class': 'lst-cl lst-cl-first'}):
            a = td.find('a')
            if a.has_attr('href'):
                op_pages.append(self.base_url + a['href'])
                
        return op_pages


def write_to_file(content, filename):
    outfile = open(filename, 'w')
    outfile.write(content.encode('utf-8'))
    outfile.close()

opParser = OpportunityParser()

## traverse the search lists from the first page to the last    
start_page_num=1
end_page_num=50
for i in range(start_page_num, end_page_num + 1):
    url = opParser.base_url + '?s=opportunity&mode=list&tab=list&pp=100&pageID=' + str(i)
    html = opParser.read_html(url)

    ## opportunity page links
    op_pages = opParser.parse_search_list(html)

    ## each list page has 100 results
    num_items_per_page = 100
    assert(len(op_pages) == num_items_per_page)

    for op_page_url in op_pages:
        filename = 'op_page.2013-11-02/' + hashlib.sha224(op_page_url).hexdigest()
        
        if os.path.exists(filename):
            continue
        
        op_page_html = opParser.read_html(op_page_url)
        write_to_file(op_page_html, filename)

        time.sleep(randint(0,5))
