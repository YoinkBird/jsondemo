#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import json
import cgi
import urllib
import urlparse

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import urlfetch

###############################################################################
# < templates>
#< htmlParen>
# wrap in p-tags
def htmlParen(string):
  string = '<p>%s</p>' % string
  return string
#</htmlParen>

#< def html_generateContainerDiv>
def html_generateContainerDiv(containerTitle,bgcolor):
  handlerContainer = '<div style="border-style:solid;border-width:1px;padding:0.5em 0 0.5em 0.5em;background-color:%s;">%s</div>' % (bgcolor, containerTitle )
  return handlerContainer
#</def html_generateContainerDiv>

#< def html_generateContainerDivBlue>
def html_generateContainerDivBlue(containerTitle):
  divColor = '#B0C4DE'
  return html_generateContainerDiv(containerTitle, divColor)
#</def html_generateContainerDivBlue>

################################################################
#< def html_generate_body_template>
# TODO: kwargs, make title optional, etc
def html_generate_body_template(titleText,bodyHtml):
  html = \
    '''
    <html>
      <head>
        <title>%s</title>
      </head>
      <body>
        %s
      </body>
    </html>
    '''
  body = (html % (titleText,bodyHtml))
  return body
#</def html_generate_body_template>
################################################################

# </templates>
###############################################################################

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')
        linkText = '<h1>Links</h1>'
        linkText += '<p><a href="%s">%s</a><p>\n' % ('/jsonreturntest','/jsonreturntest')
        linkText += '<p><a href="%s">%s</a><p>\n' % ('/formtest','/formtest')
        self.response.write(linkText)

###############################################################################
#< class_FormTest>
class FormTest(webapp2.RequestHandler):
  def get(self):
    form = self.get_html_form()
    self.response.write(form)
  def get_html_form(self):
    inputDict = {
        #'name':'value',
        'field1':'default1',
        'field2':'default2',
        'content':'default3',
        'username':'charlie',
        }
    htmlInputStr = ''
    labelCss = 'style = "display: inline-block; width: 6em; text-align: left;"'
    for name in inputDict:

      #TODO: why is '4em' not equal to '8 chars'? #SRC: http://stackoverflow.com/a/9686575
      htmlInputStr += '<div><label for="%s" %s>%s:</label>\n' % (name, labelCss, name)
      htmlInputStr += '<input name="%s" value="%s"></div>\n' % (name, inputDict[name])

    html_form_checkbox = lambda name,value: '<input type="checkbox" name="%s" value="%s">' % (name,value)
    htmlInputStr += '<label for="debug" '+labelCss+'>show json requests </label>'
    htmlInputStr += html_form_checkbox('debug',1)
    HTML_FORM = """\
    <form name="dataprocess" action="/form2json" method="post">
      <div><input name="action" value="dataprocess" type='hidden'></div>
      %s
      <div><input type="submit" value="Sign Guestbook"></div>
    </form>
    """
    response = HTML_FORM % htmlInputStr
    response = html_generate_body_template('json Form Test Page @ ' + self.request.host_url,response)
    return response
#</class_FormTest>
###############################################################################


###############################################################################
#< class_form2json>
# input x-www-form
# output: ????
# convert form data to json, send to service specified in form, 
class form2json(webapp2.RequestHandler):
  def post(self):
    debug = 1
    debug = self.request.get('debug',0) # for now, simply check if true is defined
    if(debug >= 1):
      self.response.write(html_generateContainerDiv('<h1>Handler: JsonTest</h1>' ,'#C0C0C0'))
      self.response.write(htmlParen('> self.request.body'))
      self.response.write(self.request.body)
  
    jsondata  = json.dumps((self.request.body))
    # dict of lists: https://docs.python.org/2/library/urlparse.html#urlparse.parse_qs
    jsondata  = json.dumps(urlparse.parse_qs(self.request.body))
    # dict of key-value:  http://stackoverflow.com/a/8239167
    jsondata  = json.dumps(dict(urlparse.parse_qsl(self.request.body)))
    #debug printout
    if(debug >= 1):    
      self.response.write(htmlParen('> json.dumps(self.request.body)'))
      self.response.write(htmlParen(jsondata))
    
    jsonRetStr = ''
    formDict = json.loads(jsondata)
    # make the request
    url = self.request.host_url
    # default action is 'dataprocess'
    if('action' in formDict):
      if(debug >= 1):    
        self.response.write(htmlParen('TODO: add one redirect per service that needs a form then read something like the request path to determine the action'))
        self.response.write(htmlParen('found action in formDict'))
      url += '/%s?jsonstr=' % formDict['action']
    else:
      url += '/%s?jsonstr=' % 'dataprocess'
    #TODO: validate response
    jsonreq = urllib.quote_plus(jsondata)
    if(debug >= 1):    
      self.response.write(htmlParen(jsonreq))
    #result = urlfetch.fetch(url + jsonreq,method=urlfetch.POST)
    #json style
    url = self.request.host_url + '/' + formDict['action']
    if('action' not in formDict):
      self.response.write(htmlParen('\naction not in formDict\n'))
    url = self.request.host_url + '/' + 'dataprocess'
    #TODO: rename to response
    # https://developers.google.com/appengine/docs/python/appidentity/#Python_Asserting_identity_to_Google_APIs
    result = urlfetch.fetch(
        #url + jsonreq,
        url,
        payload = jsondata,
        method=urlfetch.POST,
        headers = {'Content-Type' : "application/json"},
        )
    jsonRetStr = 'fail'
    if(result.status_code == 200):
      #jsonRetStr = json.loads(result.content)
      jsonRetStr = result.content
    #self.response.write('<h1>urlfetch response</h1>' + result.content)
    #return
    #raise Exception("Call failed. Status code %s. Body %s", result.status_code, result.content)

    #self.response.write(html_generateContainerDivBlue(htmlParen(jsonRetStr)))
    if(debug >= 1):    
      responseStr = htmlParen('response from dataprocess')
      responseStr += htmlParen('raw output:' + htmlParen(jsonRetStr))
    jsonDict = json.loads(jsonRetStr)
    response = jsonRetStr
    if(debug >= 1):    
      if('greeting' in jsonDict):
        responseStr += htmlParen('message:' + jsonDict['greeting'])
      response = html_generateContainerDivBlue(responseStr)
    self.response.write(response)
    
    # TODO: not sure what to do with this now
    #self.redirect('/formtest')
#</class_form2json>
###############################################################################


###############################################################################
#< class_DataProcessor>
# receive json, do something, output json
class DataProcessor(webapp2.RequestHandler):
#  def get(self):
#    debug = 0
#    if(debug >= 1):
#      self.response.write(htmlParen('> self.request.body'))
#      self.response.write(self.request.body)
  def get(self):
    self.post()

  def post(self):
    debug = 0
    
    #jsonDict = json.loads(self.request.get('jsonstr'))
    jsonDict = json.loads(self.request.body)

    # generate greeting
    if('username' in jsonDict):
      jsonDict['greeting'] = 'sorry %s!' % jsonDict['username']
    #del jsonDict
    #jsonDict = {}
    #jsonDict['hi'] = 'good'
    jsonStr = json.dumps(jsonDict)

    if(debug >= 1):
      self.response.write(html_generateContainerDiv('<h1>Handler: DataProcessor</h1>' ,'#C0C0C0'))
      self.response.write('<html><body>You wrote:<pre>')
      self.response.write(cgi.escape(self.request.get('content')))
      self.response.write(self.request.body)
      self.response.write('</pre></body></html>')
    #self.response.write(jsonStr)
    #self.response.write(cgi.escape(self.request.get('jsonstr')))
    self.response.write(jsonStr)
#</class_DataProcessor>
###############################################################################


###############################################################################
#< class_JsonTest>
# inspiration: http://stackoverflow.com/a/12664865
# doc: https://developers.google.com/appengine/docs/python/tools/webapp/responseclass#Response_out
# The contents of this object are sent as the body of the response when the request handler method returns.
#   http://stackoverflow.com/a/10871211
#   self.response.write and self.response.out.write are same thing
'''
Sample Usage:
  assumes that service accepts query params in to decide what to do
  from google.appengine.api import urlfetch
  # create query_params
  url = self.request.host_url
  result = urlfetch.fetch(url + urllib.urlencode(query_params),method=urlfetch.POST)
  if(result.status_code == 200):
    jsonStr += json.loads(result.content)
'''
class JsonTest(webapp2.RequestHandler):
  def post(self):
    jsonStr = self.get_json_str()
    self.response.write(jsonStr)
    #self.response.write('{"success": "some var", "payload": "some var"}')
  #TODO: adding 'return' breaks the page. This may be due to 'self.response.out.write'
  #return
  def get(self):
    response = '' # store request response
    # get user name - default to 'user_unspecified'
    user_name = self.request.get('userid','user_unspecified')
    query_params = urllib.urlencode({'userid': user_name})
    #< send POST request>
    if(0):
      result = self.test_urlfetch()
      result = html_generateContainerDiv(result,'salmon') # websafe colours
      response += result
    #< >
    url = self.request.host_url
    service_url = '/jsonreturntest'
    url += service_url
    #result = urlfetch.fetch(url + urllib.urlencode(query_params),method=urlfetch.POST)
    result = urlfetch.fetch(url,method=urlfetch.POST)
    #response += urlfetch.fetch(url,method=urlfetch.POST)
    if(result.status_code == 200):
      jsonStr = 'This code will make this page POST to itself and then read the output.<br/>\n'
      jsonStr += 'Python Code:<br/>\n' #'Example json return string that a service could use:<br/>\n'
      jsonStr += '<pre>'
      jsonStr += "jsonData = \"\"\n"
      jsonStr += "result = urlfetch.fetch('%s',method=urlfetch.POST)\n" % url
      jsonStr += "  if(result.status_code == 200):\n"
      jsonStr += "    jsonData = json.loads(result.content)\n"
      jsonStr += '</pre>'
      jsonStr += 'This is the output:<br/>\n'
      jsonStr += '<pre>'
      jsonStr += json.loads(result.content)
      jsonStr += '</pre>'
    else:
      jsonStr = 'request failed: ' + str(result.status_code)
    #< />
    jsonReturnText = jsonStr
    response += html_generateContainerDivBlue(jsonReturnText)

    #greetText = 'This page generates the following json string when visited with POST:<br/>\n' + self.get_json_str()
    #response += html_generateContainerDivBlue(greetText) # websafe colours
    # wrap in grey div
    response = html_generateContainerDiv('<h1>Handler: JsonTest</h1>' + response,'#C0C0C0')
    #response = '<html>\n  <body>\n' + response + '\n  </body>\n</html>'
   # title contains host as well to show in browser's "window name" to make alt+tabbing easier
    response = html_generate_body_template('json Test Page @ ' + self.request.host_url,response)
    self.response.write(response)
  #< def_get_json_str>
  def get_json_str(self):
    return json.dumps('{"success": "some var", "payload": "some var"}')
  #</def_get_json_str>
  #< def test_urlfetch>
  def test_urlfetch(self):
    #TODO: as a testing exercise, rewrite to capture status messages and print summary
    #NOTE: this is how I learned that port 80 is the default port that non-specific query will use
    #      that is why this "coverage tests" all urls with "no port", 80, and 8080 
    from google.appengine.api import urlfetch

    result = '<h1>TESTCODE OUTPUT</h1>'
    result += 'self.request.url is ' + self.request.url + '<br/>' + '\n'
    result += 'self.request.path is ' + self.request.path + '<br/>' + '\n'
    result += 'self.request.host_url is ' + self.request.host_url + '<br/>' + '\n'
    relpath = 'jsonreturntest'
    testUrls =  [
        self.request.host_url,
        self.request.host_url + '/' + relpath,
        '' + relpath,
        '/' + relpath,
        # find out why running on port :80 allowed '/<path>' to work
        'localhost/' + relpath,
        'localhost:80/' + relpath,
        'localhost:8080/' + relpath,
        'http://localhost/' + relpath,
        'http://localhost:80/' + relpath,
        'http://localhost:8080/' + relpath
        ]
    for url in testUrls:
      result += '>try:> urlfetch.fetch(\'%s\',method=urlfetch.POST)' % url
        
      result += '<br/>' + '\n'
      try:
        urlfetch.fetch(url,method=urlfetch.POST)
        result+='SUCCESS'
      except:
        result+='&nbsp;&nbsp;&nbsp;failure'
      result += '<br/>' + '\n'
    return result
    response += '\n'+result+'\n'
    #</send POST request>
    self.response.write(response)
  #<def test_urlfetch>
#</class_JsonTest>
###############################################################################

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/jsonreturntest',JsonTest),
    ('/formtest',FormTest),
    ('/form2json',form2json),
    ('/dataprocess',DataProcessor),
], debug=True)
