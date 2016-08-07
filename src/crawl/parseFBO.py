# -*- coding: utf-8 -*-
## This script parses the federal business opportunities from fbo.gov
## 1. Hit the search pages
## 2. Iterates the search results and visit each page
## 3. Parses the necessary information for individual page
## 4. Normalize the data based on the data type

#import requests
import hashlib, re, os, sys
from datetime import datetime
from bs4 import BeautifulSoup
from base64 import b64encode

debug = False

class OpportunityParser: 
    def __init__(self):
        self.base_url = 'https://www.fbo.gov/index'
        self.op_url_prefix = 'https://www.fbo.gov/index?s=opportunity&mode=form&id='

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
        for td in soup.findAll('td', {'class':'lst-cl lst-cl-first'}):
            a = td.find('a')
            if a.has_key('href'):
                op_pages.append(self.base_url + a['href'])
                
        return op_pages

    ## parse each oppotunity page
    def parse_op_page(self, html):
        soup = BeautifulSoup(html)
        debug_text = ''

        ## original url
        op_id = self.substr(html, '&id=', '&tab=')
        if not op_id:
            return
        
        page_url = self.op_url_prefix + op_id
        if debug:
            debug_text += '==Source URL:' + page_url + '\n'
        
        ## title
        node_agency_header = soup.find('div', {'class':'agency-header'})
        if node_agency_header and node_agency_header.h2:
            title = self.clean(node_agency_header.h2.text.encode('utf-8'))
            if debug:
                debug_text += '==Title:' + title + '\n'
        else:
            title = ''

        ## agency 
        agency_name_text = self.get_text(soup, 'div', class_name='agency-name')
        agency_name = self.clean(self.substr(agency_name_text, 'Agency:', '<br'))
        if debug:
            debug_text += '==Agency:' + agency_name + '\n'
            
        ## solicitation number
        sol_num = self.get_text(soup, 'div', id_name='dnf_class_values_procurement_notice__solicitation_number__widget')
        if debug:
            debug_text += '==Solicitation Number:' +  sol_num + '\n'

        ## description
        desc = b64encode(self.get_text(soup, 'div', id_name='dnf_class_values_procurement_notice__description__widget'))
        if debug:
            debug_text += '==Desc:' + desc[:100] + '\n'
            
        ## notice type
        notice_type = self.get_text(soup, 'div', id_name='dnf_class_values_procurement_notice__procurement_type__widget')
        # skip award notices
        notice_type_lower = notice_type.lower()
        if 'award' in notice_type_lower or 'cancel' in notice_type_lower or 'justification' in notice_type_lower:
            return
        if debug:
            debug_text += '==Notice Type:' + notice_type + '\n'

        ## contracting office address
        contract_office = self.get_text(soup, 'div', id_name='dnf_class_values_procurement_notice__office_address__widget')
        if not contract_office:
            contract_office = self.get_text(soup, 'div', id_name='dnf_class_values_procurement_notice__office_address_text__widget')
        if debug:
            debug_text += '==Contract Office Address:' + contract_office + '\n'

        ## place of performance
        place_of_performance = self.get_text(soup, 'div', id_name='dnf_class_values_procurement_notice__place_of_performance__widget')
        if debug:
            debug_text += '==Place of Performance:' + place_of_performance + '\n'

        ## state from place of performance or contract office
        state = self.parse_state(place_of_performance)
        if state is '':
            state = self.parse_state(contract_office)
        if debug:
            debug_text += '==State:' + state + '\n'
            
        ## Point of contract
        poc = self.get_text(soup, 'div', id_name='dnf_class_values_procurement_notice__primary_poc__widget')
        if not poc:
            poc = self.get_text(soup, 'div', id_name='dnf_class_values_procurement_notice__poc_text__widget')
        if debug:
            debug_text += '==Point of Contact:' + poc + '\n'

        ## Response Date
        due_date_text = self.get_text(soup, 'div', id_name='dnf_class_values_procurement_notice__response_deadline__widget').strip()
        due_date = self.parse_date(due_date_text)
        if debug:
            debug_text += '==Response Date:' + due_date + '\n'

        ## Set Aside
        set_aside = self.get_text(soup, 'div', id_name='dnf_class_values_procurement_notice__set_aside__widget').strip()
        if debug:
            debug_text += '==Set Aside:' + set_aside + '\n'
            
    
        ## classfication code
        class_code_text = self.get_text(soup, 'div', id_name='dnf_class_values_procurement_notice__classification_code__widget')
        class_code = self.parse_class_codes(class_code_text)
        if debug:
            debug_text += '==Classification Codes:' + class_code + '\n'
        
        ## naics code
        naics_code_text = self.get_text(soup, 'div', id_name='dnf_class_values_procurement_notice__naics_code__widget')
        naics_codes = self.parse_naics_codes(naics_code_text)
        if debug and len(naics_codes) > 0:
            debug_text += '==NAICS Codes:' + ' '.join(naics_codes) + '\n'

        ## solicitation_num, Title, Agency, Response Date, Classification Codes, NAICS Codes, Place of Performance, Point of Contact, Contract Office, Notice Type, Source URL, Desc
        if debug:
            print debug_text
        else:
            print sol_num + '\t' + title + '\t' + agency_name + '\t' + due_date + '\t' + class_code + '\t' + ' '.join(naics_codes) + '\t' + place_of_performance + '\t' + poc + '\t' + contract_office + '\t' + state + '\t' + set_aside + '\t' + notice_type + '\t' + page_url + '\t' + desc
        

    def get_text(self, soup, tag_name, id_name='', class_name=''):
        if id_name != '':
            node = soup.find(tag_name, {'id': id_name})
        elif class_name != '':
            node = soup.find(tag_name, {'class': class_name})
        else:
            return ''
        
        if not node:
            return ''
        
        try:
            return self.clean(node.renderContents())
        except:
            return self.clean(node.get_text())
        
    def parse_naics_codes(self, text):
        naics_codes = []
        for naics_code_text in text.split('/'):
            split_code = naics_code_text.split('-')
            naics_code = split_code[0].strip()
            if len(naics_code) == 6:
                naics_codes.append(naics_code)
        return naics_codes
        
    def parse_class_codes(self, text):
        class_code = ''
        for class_code_text in text.split('/'):
            split_code = class_code_text.split('-')
            if class_code == '':
                class_code = split_code[0].strip()
            else:
                class_code += ',' + split_code[0].strip()
        return class_code
        
    def clean(self, text):
        pattern = re.compile(r'(\s)+')
        cleaned_text = re.sub(pattern, ' ', text)
        cleaned_text = cleaned_text.replace('\t', ' ')
        cleaned_text = cleaned_text.strip()
        return cleaned_text

    def parse_date(self, date_string):
        year_start ='201'
        year_pos = date_string.find(year_start)
        if year_pos == -1:
            return ''
        year_pos += len(year_start) + 1

        try:
            date = datetime.strptime(date_string[:year_pos], "%b %d, %Y")
            return date.strftime("%m/%d/%Y")
        except ValueError:
            try:
                date = datetime.strptime(date_string[:year_pos], "%B %d, %Y")
                return date.strftime("%m/%d/%Y")
            except ValueError:
                return ''
        
        return ''

    def substr(self, text, start_str, end_str):
        start_pos = text.find(start_str)
        if start_pos == -1:
            return ''
        start_pos += len(start_str)

        end_pos = text.find(end_str, start_pos)
        if end_pos == -1:
            return text[start_pos:]
        
        return text[start_pos:end_pos]

    ## find the state in the address and return the state abbreviation
    def parse_state(self, address):
        state_map = {'AL':'Alabama','AK':'Alaska','AZ':'Arizona','AR':'Arkansas','CA':'California','CO':'Colorado','CT':'Connecticut','DE':'Delaware','FL':'Florida','GA':'Georgia','HI':'Hawaii','ID':'Idaho','IL':'Illinois','IN':'Indiana','IA':'Iowa','KS':'Kansas','KY':'Kentucky','LA':'Louisiana','ME':'Maine','MD':'Maryland','MA':'Massachusetts','MI':'Michigan','MN':'Minnesota','MS':'Mississippi','MO':'Missouri','MT':'Montana','NE':'Nebraska','NV':'Nevada','NH':'New Hampshire','NJ':'New Jersey','NM':'New Mexico','NY':'New York','NC':'North Carolina','ND':'North Dakota','OH':'Ohio','OK':'Oklahoma','OR':'Oregon','PA':'Pennsylvania','RI':'Rhode Island','SC':'South Carolina','SD':'South Dakota','TN':'Tennessee','TX':'Texas','UT':'Utah','VT':'Vermont','VA':'Virginia','WA':'Washington','WV':'West Virginia','WI':'Wisconsin','WY':'Wyoming','AS':'American Samoa','DC':'District of Columbia','FM':'Federated States of Micronesia','GU':'Guam','MH':'Marshall Islands','MP':'Northern Mariana Islands','PW':'Palau','PR':'Puerto Rico','VI':'Virgin Islands'}

        for state_abbr, state_fullname in state_map.items():
            if ' ' + state_fullname + ' ' in address or ' ' + state_abbr + ' ' in address:
                return state_abbr
        return ''
        
def write_to_file(content, filename):
    outfile = open(filename, 'w')
    outfile.write(content)
    outfile.close()

opParser = OpportunityParser()

## download an example for debugging
##html = opParser.read_html('https://www.fbo.gov/index?s=opportunity&mode=form&id=ffaf3eaaea9fd09c017dd5c5579e5352&tab=core&_cview=1')
##write_to_file(html, 'op_page/ffaf3eaaea9fd09c017dd5c5579e5352.html')

if len(sys.argv) < 2:
    print 'usage: python.exe parseFBO.py inputDirectory'
    exit(1)

local_dir_name = sys.argv[1]
print 'Reading the files from ' + local_dir_name

for dirname, dirnames, filenames in os.walk(local_dir_name):
    for op_page_filename in filenames:
        filename = dirname + op_page_filename

        if debug:
            print '\r\n\r\n==Filename:', filename
        op_page_html = open(filename, 'r').read()
        opParser.parse_op_page(op_page_html)
