# Copyright {2016} {Narrowbeam Limited}

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
   
from bs4 import BeautifulSoup
import requests
import re
import os
import json
from urllib.parse import urlparse
from pathlib import Path

docurl = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/"

page = requests.get (docurl + "aws-template-resource-type-ref.html" )
html_doc = page.content

urllist = []
serviceurllist = []

# Create the folder for the snippets
try:
  os.mkdir("./cfn-yaml")
except:
  pass

soup = BeautifulSoup(html_doc, 'html.parser')

# Selector based lookup - gets what we want and awstoc duplicates
urllisttmp = soup.select('li a[href*="AWS"]')

# Build a list of link description, url
for url in urllisttmp:
  try:
    myclass = url['class']
  except:
    # We actually only care about the ones without a class !!!
    urllist.append([url.text, docurl + url['href']])

snippetStart = """<snippet>
  <content><![CDATA[
"""
snippetEnd = """
]]></content>"""



serviceurllist = []

path = Path('listfile.txt')
if not path.is_file():
  for (pagelink,pageurl) in urllist:
    pageurl = pageurl.replace("./", "")
    print("Processing service " + pagelink + " -- " + pageurl)
    servicepage = requests.get (pageurl)
    service_html_doc = servicepage.content
    print("Got page " + str(len(service_html_doc)))
    service_soup = BeautifulSoup(service_html_doc, 'html.parser')
    # Selector based lookup - gets what we want and awstoc duplicates
    serviceurllisttmp = service_soup.select('li a[href*="aws-"]')

    # Build a list of link description, url
    for serviceurl in serviceurllisttmp:
      
      try:
        myclass = url['class']
      except:
        # We actually only care about the ones without a class !!!
        print("Service url: " + serviceurl['href'])
        serviceurllist.append([serviceurl.text, docurl + serviceurl['href']])
    

  json_string = json.dumps(serviceurllist)

  with open('listfile.txt', 'w') as filehandle:
    filehandle.write('%s\n' % json_string) 
else:
  with open('listfile.txt', 'r') as filehandle:
    serviceurllist = json.load(filehandle)
# currently we have a list of page titles, page urls
# for services page which lists all the necessary information

count = 0
for (pagelink,pageurl) in serviceurllist:
  print("Processing type " + pagelink)
  hotkey = ""
  snippet = ""
  pageurl = pageurl.replace("./", "")
  pagelinklist = pagelink.split("::")
  hotkey = "cfn-" + pagelinklist[1]
  for i in range(2,len(pagelinklist)):
    hotkey =  hotkey + "-" + pagelinklist[i]

  snippetFinish = """
  <tabTrigger>""" + hotkey + """</tabTrigger>
  <scope>source.yaml, source.cloudformation</scope>
  </snippet>"""

  # print hotkey

  snippet = snippet +  snippetStart
  snippet = snippet +  "#AWS-DOC " + pageurl + '\n'

  print("Requesting page " + pageurl)

  page = requests.get(pageurl).content
  soup2 = BeautifulSoup(page, 'html.parser')
  fragment = soup2.select_one('#YAML pre')

  print("TAG text is " + fragment.text)
  snippet = snippet + fragment.text

  # for tag in fragment:
  #   print("TAG text is " + tag.get_text())
  #   #Some source material has an extra \n that needs to be stripped
  #   snippetfilter = tag.text
  #   if snippetfilter[0] == '\n':
  #     snippet = snippet + snippetfilter[1:]
  #   else:
  #     snippet = snippet + tag.text  

  # count += 1
  snippet = snippet + snippetEnd
  snippet = snippet +  snippetFinish

  # if count == 10:
  #   break

  print("writing: " + "cfn-yaml/" + hotkey+".sublime-snippet")
  # print snippet
  print("Snippet: " + snippet)
  try:
    os.mkdir("cfn-yaml/" + pagelinklist[1])
  except:
    pass

  # with open("cfn-yaml/" + pagelinklist[1] + "/" + hotkey+".sublime-snippet", 'w') as filehandle:
  #     filehandle.write('%s\n' % json_string) 

  # f = open("cfn-yaml/" + pagelinklist[1] + "/" + hotkey+".sublime-snippet", "wb")
  f = open("cfn-yaml/" + pagelinklist[1] + "/" + hotkey+".sublime-snippet", "w")
  f.write(snippet)
  f.close()
