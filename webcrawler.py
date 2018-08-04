#!/usr/bin/python
#
# This program does a Google search for "quick and dirty" and returns
# 50 results.
#
import re
import webbrowser
import urllib
import urllib2
import json
import codecs
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from xgoogle.search import GoogleSearch, SearchError

resultg = []
#f.write('<html>\n<head>\n<link rel="stylesheet" type="text/css" href="mystyle.css">\n</head>\n<body>\n<p class="small">')

def bing_search(query, search_type):
    #search_type: Web, Image, News, Video
    key= '8VrdEoOdguaxZD6u20DBb6vCcI1Y7/bFNFfGkm/Z9Mg'
    query = urllib.quote(query)
    # create credential for authentication
    user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'
    credentials = (':%s' % key).encode('base64')[:-1]
    auth = 'Basic %s' % credentials
    url = 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/'+search_type+'?Query=%27'+query+'%27&$top=50&$format=json'
    request = urllib2.Request(url)
    request.add_header('Authorization', auth)
    request.add_header('User-Agent', user_agent)
    request_opener = urllib2.build_opener()
    response = request_opener.open(request)
    response_data = response.read()
    json_result = json.loads(response_data)
    resultb = json_result['d']['results']
    f=open("final.txt","w")
    for line in resultb:
        if line['Url'] not in resultg:
            f.write('<a href='+line['Url'].encode('utf8')+'>'+'<h1>'+line['Title'].encode('utf8')+'</h1>\n'+'</a>\n')
    f.close()

def google_search(query):
    try:
        results = []
        resultg = []
        gs = GoogleSearch(query)
        gs.results_per_page = 30
        while True:
            tmp = gs.get_results()
            if not tmp: # no more results were found
              break
            results.extend(tmp)
        #f.write(res.title.encode('utf8'))
        #f.write("\n<br><br>")
        #f.write(res.desc.encode('utf8'))
        #f.write("\n<br><br>")
        f=open("final.txt","w")  
        for res in results:
            f.write('\n <a href='+res.url.encode('utf8')+'>'+'<h1>'+res.title.encode('utf8')+'</h1>\n'+'</a>\n')
            resultg.extend(res.url.encode('utf8'))
        f.close()
    except SearchError, e:
        print "Search failed: %s" % e


def get_page(strurl):
    page = urllib.urlopen(strurl)
    page = str(page.read())
    return page
##

def get_next_target(page):
    start_link = page.find('<a href=')
    if start_link == -1:
        return None,0
    start_quote = page.find('"',start_link)
    end_quote = page.find('"',start_quote+1)
    url = page[start_quote+1:end_quote]
    return url,end_quote
##

def union(p,q):
    for object in q:
        if object not in p:
            p.append(object)
##

def get_all_links(page,max_pages):
    links = []
    pages_num = 0
    while True and pages_num <= max_pages:
        url,endpos = get_next_target(page)
        if url:
            if url[1:5] == 'wiki':
                links.append('http://en.wikipedia.org'+url)
            else:
                links.append(url)
            pages_num = pages_num+1
            page = page[endpos:]
        else:
            break
    return links
##

def print_all_links(page,max_pages):
    links = get_all_links(page,max_pages)
    f=open("final.txt","w")  
    for url in links:
        f.write('<a href='+url+'>'+'<h1>'+url+'</h1></a>\n'+'\n')
    f.close()
##



class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(2)
        self.end_headers()
        self.wfile.write("""
            <html><head>
            <style>
            p.ex1{
                padding: 5cm 0cm 0cm 15.5cm;
            }
            p.ex2{
                padding: 0cm 0cm 0cm 12cm
            }
            p.ex3{
                padding: 0cm 0cm 0cm 16.7cm
            }
            </style>
            </head>
            <body>
            <p class = "ex1"><font color = "blue" size=35><b>B</font>
            <font color = "red" size=30>i</font>
            <font color = "#E9B713" size=30>z</font>
            <font color = "blue" size=35>B</font>
            <font color = "green" size=30>o</font>
            <font color = "red" size=30>t</font></b></p>
            <form method="POST">
            <p class = "ex2">
            <textarea name="mood" rows="1" cols="60">
            </textarea>
            </p>
            <p class = "ex3">
            <input type="submit" name="Search" value="Search">
            </p>
            </form>
            </body>
            </html>
            """)
        return

    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        themood = form["mood"]
        url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',themood.value)
        f=open("final.txt","w");
        f.write('<html>\n<head>\n<link rel="stylesheet" type="text/css" href="mystyle.css">\n</head>\n<body>\n<p class="small">' )
        f.close()
        if url:
            print url[0]
            print_all_links(get_page(url[0]),1000)
        else:
            resultg = []
            bing_search(themood.value, 'Web')
            google_search(themood.value)
            #f.write('</p></body>\n</html>')
            #f.close()
        with open("final.txt", "r") as ins:
            for line in ins:
                self.wfile.write(line)
        print f.read
        return


def main():
    #print "Enter query"
    #query = raw_input()
    #f.write('</p></body>\n</html>')
    #webbrowser.open("final.html")
    #f.close()
    server = HTTPServer(('', 8080), Handler)
    server.serve_forever()



if __name__ == "__main__":
    main()
