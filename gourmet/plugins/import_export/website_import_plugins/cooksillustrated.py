from selenium import webdriver

d = webdriver.Chrome('/home/thomas/Downloads/chromedriver')
print('got here :)')
d.get('https://www.cooksillustrated.com/sign_in/')
un=d.find_element_by_xpath('//*[@name="user[email]"]')
#un.send_keys('USERNAME')
pw = d.find_element_by_xpath('//*[@name="user[password]"]')
#pw.send_keys('PASSWORD\n')

# import cookielib
# import urllib
# import urllib2
import BeautifulSoup

title = bs.find('h2',{'class':'document-header__title'})
ingredients = bs.findAll('div',{'class':'ingredient'})
instructions = bs.findAll('div',{'class':'recipe-instructions'})
notes = bs.findAll('div',{'class':'asides'})
yields = bs.find('span',{'class':'recipe-instructions__yield'})

# cj = cookielib.CookieJar()

# br = mechanize.Browser()
# br.set_cookiejar(cj)
# br.open('https://www.cooksillustrated.com/sign_in')
# br.select_form(nr=0)
# br.form['user[email]'] = 'USERNAME'
# br.form['user[password]']='PASSWORD'
# br.submit()
# print br.response().read()

# #opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
# #opener.addheaders = [('User-agent','Testing123')]
# #urllib2.install_opener(opener)



# #first_req = urllib2.Request('https://www.cooksillustrated.com/sign_in')
# #resp = urllib2.urlopen(first_req)
# #contents = resp.read()
# bs = BeautifulSoup.read(contents)

# form = bs.find(id='new_user')


# inputs = form.findChildren('input')

# payload = {
# }

# for i in inputs:
#     if i.has_key('name') and i.has_key('value'):
#         payload[i['name']] = i['value'].encode('utf8')
#     elif i.has_key('name'):
#         if 'user' in i['name'].lower():
#             payload[i['name']] = 'USERNAME'
#         elif 'passw' in i['name'].lower():
#             payload[i['name']] = 'PASSWORD'
        

# data = urllib.urlencode(payload)

# req = urllib2.Request(authurl, data)
