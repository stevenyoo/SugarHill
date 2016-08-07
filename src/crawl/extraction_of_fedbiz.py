# parsing fedbiz

from BeautifulSoup import BeautifulSoup
import urllib, urllib2
##from encode import multipart_encode
##from streaminghttp import register_openers
import mechanize


def get_html(url, form_data):
    #the http headers are useful to simulate a particular browser (some sites deny
    #access to non-browsers (bots, etc.)
    #also needed to pass the content type. 
    headers = {
        'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13',
        'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml; q=0.9,*/*; q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

##    data, headers = multipart_encode(form_data)
##    headers['User-Agent'] = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13'
    
    print headers
    print form_data

    request = urllib2.Request(url, urllib.urlencode(form_data), headers)
    response = urllib2.urlopen(request)
    return response.read()


def log(data, filename):
    tmp = open(filename, 'w')
    tmp.write(data)
    tmp.close()

def get_value(html, name):
    soup = BeautifulSoup(html)
    result = soup.findAll(attrs={"name":name})
    return result[0]['value']
    

def readSearchResult():
    url = 'https://www.fbo.gov/index?s=opportunity&tab=search&mode=list'
    html = get_html(url, {})            
    data = {"dnf_opt_finalize":"1",
            "_____dummy":get_value(html, '_____dummy'),
            "so_form_options":get_value(html, 'so_form_options'),
            "so_form_checksum":get_value(html, 'so_form_checksum'),
            "so_form_timestamp":get_value(html, 'so_form_timestamp'),
            "so_form_prefix":get_value(html, 'so_form_prefix'),
            "dnf_opt_action":get_value(html, 'dnf_opt_action'),
            "dnf_opt_template":get_value(html, 'dnf_opt_template'),
            "dnf_opt_template_dir":get_value(html, 'dnf_opt_template_dir'),
            "dnf_opt_subform_template":get_value(html, 'dnf_opt_subform_template'),
            "dnf_opt_mode":get_value(html, 'dnf_opt_mode'),
            "dnf_opt_target":get_value(html, 'dnf_opt_target'),
            "dnf_opt_validate":get_value(html, 'dnf_opt_validate'),
            "dnf_class_values[procurement_notice][dnf_class_name]":get_value(html, 'dnf_class_values[procurement_notice][dnf_class_name]'),
            "dnf_class_values[procurement_notice][notice_id]":get_value(html, 'dnf_class_values[procurement_notice][notice_id]'),
            "dnf_class_values[procurement_notice][_so_agent_save_agent]":get_value(html, 'dnf_class_values[procurement_notice][_so_agent_save_agent]'),
            "dnf_class_values[procurement_notice][custom_response_date]":get_value(html, 'dnf_class_values[procurement_notice][custom_response_date]'),
            "dnf_class_values[procurement_notice][searchtype]":["archived"],
            "dnf_class_values[procurement_notice][all_agencies]":["all"],
            "dnf_class_values[procurement_notice][recovery_act]":"",            
            "dnf_class_values[procurement_notice][procurement_type][]":["a"],
            "dnf_class_values[procurement_notice][naics_code][]":["0220"],
            "dnf_class_values[procurement_notice][agency][dnf_class_name]":"agency"
            }
    url='https://www.fbo.gov/index?s=opportunity&mode=list&tab=searchresults&tabmode=list&pp=100'

    print url, data
    html = get_html(url, data)
    log(html, 'fedbiz7.html')
    

def search():
    data = {'mb_id':'anoia7',
            'mb_password':'audgns',
            'url':'%2F'
            }
    html = get_html('http://www.bangabanga.net/bbs/login_check.php', data)
    log(html, 'banga.html')
    


class CCR:
    def __init__(self):
        self.br = mechanize.Browser()
        self.br.set_handle_robots(False)
        
    def login(self, username, password):
        url = 'https://www.bpn.gov/ccr/default.aspx'

        self.br.open(url)
        self.br.select_form('aspnetForm')
        self.br['ctl00$cphBody$loginUserId$UserName']=username
        self.br['ctl00$cphBody$loginUserId$Password']=password
        response = self.br.submit()
       
        log(response.read(), 'ccr_login_result.html') 

    def search(self, naics_code):
        url = 'https://www.bpn.gov/CCRSearch/Search.aspx'

        self.br.open(url)
        self.br.select_form('aspnetForm')
        self.br['ctl00$ContentPlaceHolder1$txtNAICS'] = naics_code
        self.br['ctl00$ContentPlaceHolder1$rdoRegStatus'] = ['ALL']
                                                        
        response = self.br.submit()
       
        log(response.read(), 'ccr_search_result.html') 

    def next_search_result(self):
        self.br.select_form('aspnetForm')
        self.br['ctl00$ContentPlaceHolder1$gvSearchResults']='Page$2'
        response = self.br.submit()
       
        log(response.read(), 'ccr_search_result2.html') 
    

def main():
    ccr = CCR()
    ccr.login('kajaldeepak', 'Sugarhill3*')
    ccr.search('541110')
##    ccr.next_search_result()
    
    
##    readSearchResult()
##    search()
    
if __name__ == '__main__':
    main()
