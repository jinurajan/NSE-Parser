"""
    NSE.Py
    Author:Jinu
    To run from command line:
        python NSE.py  <OutPutHtml Filename>
"""

import urllib2
import simplejson as json
import sys


Gainers = [("nifty","Nifty"),("jrNifty","Jr.Nifty"),("secGt20","Securities > Rs.20"),("secLt20","Securities < Rs.20"),("fno","F&O Securities" ), ("allTop","All Securities")]

class HTMLDocument(object):
    """
        Class for Creating HTML Document
    """
    def __init__(self,head="",body=""):
        self.head = head
        self.body = body
    def appendToHead(self,element):
        self.head = self.head + element +"\n"

    def appendToBody(self,element):
        self.body = self.body + element + "\n"

    def addStyle(self,style):
        appendToHead(self,style)

    def addScript(self,script):
        appendToHead(self,script)
    def getHtmlDocument(self):
        return str("<!DOCTYPE html>\n<html>\n\t<head>\n\t\t"+self.head+"\n\t</head>\n\t<body>\n\t"+self.body+"\n\t\t</body>\n</html>")

class HTMLElement(object):
    """
        Class for Creating HTML Elements
    """
    def __init__(self,tagname):
        self.tagname = tagname
        self.attributes = {}
        self.eventListeners ={}
        self.elements =[]
        self.text=""        
    def addAttribute(self,key,value):
        self.attributes[key]='"' + value + '"'

    def addEvents(self,event,FnName):
        self.eventListeners[event] = FnName
    
    def addElements(self,element):
        self.elements.append(element)
 
    def addText(self,text):
        self.text = self.text + text
    
    def getAttributes(self):
        attributes = ""
        for key,value in self.attributes.items():
            attributes = attributes+" "+key+"="+value
        return attributes

    def getEventListeners(self):
        events = ""
        for key,fnName in self.eventListeners.items():
            events = events+" "+key+"="+fnName
        return events

    def __str__(self):
        attributes = ""
        events = ""
        if len(self.attributes) != 0:
            attributes = self.getAttributes()
        if len(self.eventListeners) != 0:
            events = self.getEventListeners()
        if self.elements:
            elements = "".join(str(each) for each in self.elements)
            return "<"+self.tagname+ attributes+ events+">"+str(elements) + " </"+self.tagname+">\n" 
        else:
            return "<"+self.tagname+ attributes+ events+">"+self.text+ " </"+self.tagname+">\n" 
       

class NSE(HTMLDocument):
    """
        Class for Fetch HTML Page and create HTML Document
    """
    def __init__(self,URL,headers):
        self.URL = URL
        self.headers = headers
        HTMLDocument.__init__(self)
        
    def FetchGainers(self,gainer,URL=None):
        if not URL:
            URL = self.URL 
        print "Fetching data from URL" + URL
        PATH = URL+gainer+"Gainers1.json"
        req = urllib2.Request(PATH, headers=self.headers)
        try:
            content = urllib2.urlopen(req)
            return content
        except urllib2.HTTPError, e:
            print e.fp.read()
            return None

    def getTableContent(self,heading=None):
        """
        Get Table Content from the Data Fetched and return as a list
        """
        
        if not heading:
            heading =('Symbol','Open','High','Latest Ex Date')
        for each in Gainers:
            rows =[heading]
            contentdata = self.FetchGainers(each[0])
            if contentdata:
                data =json.loads(contentdata.read())['data']
            else:
                print contentdata
            rows = rows + [ ( i['symbol'],i['openPrice'], i['highPrice'], i['lastCorpAnnouncementDate'] ) for i in data]
            yield rows
        
    def createTable(self,tablecontent,index,heading=False):
        """Create Table Element with the Content
        """
        
        Table = HTMLElement("Table")
        Table.addAttribute("id",str(index)+"_table")
        Table.addAttribute("style","display:none;")
        if heading:
            header_row = HTMLElement("tr")
            for eachHeading in tablecontent[0]: 
                heading = HTMLElement("th")
                heading.text = eachHeading
                header_row.addElements(str(heading))
            Table.addElements(str(header_row))
        for row in tablecontent[1:]:
            eachrow = HTMLElement("tr")
            for eachItem in row:
                item = HTMLElement("td")
                item.text = eachItem
                eachrow.addElements(str(item))
            Table.addElements(str(eachrow))
        return str(Table)
                
    def getHtml(self):
        """
        Get All Table Elements
        """
        tablecontent = self.getTableContent()
        tabledata =""
        index = 0
        while True:
            try:
                tabledata = tabledata + self.createTable(tablecontent.next(),index,heading=True)
                index = index+1    
            except StopIteration:
                div = HTMLElement("div")
                div.addAttribute("class","tablecontent")
                div.addElements(tabledata)
                self.createHtml(str(div))
                break;
            
    def createHtml(self,tabledata):
        """
        Create Html with all Fetched Table Data
        """
        if len(sys.argv) >= 2:
            filename = sys.argv[1]
        else:
            filename = "NSE.html"
        f = open(filename,"w+")
        
        self.appendToHead(self.getstyles())
        
        maindiv = HTMLElement("div")
        maindiv.addAttribute('class','container')
        maindiv.addElements(self.getheaders())
        maindiv.addElements(tabledata)
        
        self.appendToBody(str(maindiv))
        self.appendToBody(self.getFooter())
        self.appendToBody(self.getJqueryscript())
        self.appendToBody(self.getHelperscript())
        
        f.write(self.getHtmlDocument())
        f.close()
        return
        
    def getheaders(self):
        """
        Create Header Element and return
        """
        
        div = HTMLElement("div")
        div.addAttribute('class','header')
        ul = HTMLElement("ul")
        ul.addAttribute('class','headerlist')
        for each in Gainers:
            li = HTMLElement("li")
            a = HTMLElement("a")
            a.addAttribute('href','#'+str(Gainers.index(each)) + "_table")
            a.addEvents("onclick","changeTable(this)")
            a.addText(each[1])
            li.addElements(str(a))
            ul.addElements(str(li))
        div.addElements(str(ul))
        return str(div)
    
    def getJqueryscript(self):
        """
        Include Jquery Script to the Html
        """
        
        script = HTMLElement("script")
        script.addAttribute("src","https://code.jquery.com/jquery-1.10.2.min.js")
        return str(script)
    
    def getHelperscript(self):
        """
        Create helper Javascript and returns the Script Element
        """
        script = HTMLElement("script")
        script.addText("""
                        var i =0;
                        $(document).ready(function(){
                            $("#0_table").show();
                            $("ul.headerlist li:first a:first").css("font-weight","bold");
                        });
                        function changeTable(element){
                            $("table").hide();
                            var href = $(element).attr("href");
                            $("ul.headerlist li:eq(" + i.toString() +") a:first").css("font-weight","normal");
                            i = Number(href.substring(1).split('_')[0]);
                            $("ul.headerlist li:eq(" + i +") a:first").css("font-weight","bold");
                            $(href).show();
                        }
                        """)
        return str(script)
    
    def getFooter(self):
        """
        Create Footer and returns Footer Element 
        """
        
        footer = HTMLElement("div")
        footer.addAttribute("id","footer")
        p =HTMLElement("p")
        p.addText("Copyright &copy; 2014. All rights reserved.")
        p.addAttribute("class","copyright")
        footer.addElements(str(p))
        return str(footer)
         
    def getstyles(self):
        """
        Create Styles for HTML Elements and returns Style
        """
        style = HTMLElement("style")
        style.addText("""\ntable{
                        background:#EEEEEE;
                        margin:24px auto;
                        
                    } """)
        style.addText(""" td,th{
                        border:1px solid grey;
                        width:10em;
                        text-align:center;
                    }""")
        style.addText("""th{
                    background:#6F9F9F;
    
                    } """)
        style.addText("""ul{
                        list-style: none outside none;;
                        display:inline;
                        text-align:center;
                        margin:0;
                        float:left;
                        padding:10px 0;
                        background:#444444;
                        width:100%;
                    } """)
        style.addText("""ul li{
                        display:inline;
                        padding:1em 1em 1em 1em;
                        width:16.66666%;
                    } """)
        style.addText("""div.header{
                        width:100%;
                        height:auto;
                        background:gray;
                        margin:0 5em 0 0;
                        overflow:hidden;
                    } """)
        style.addText("""div.header > ul >  li > a{
                            color:white;
                            text-decoration:none;
                            /*overflow:hidden;*/
                            padding-right:10px;
                            font-weight:normal;
                            border-right:1px solid #A4A4A4;
                    } """)
        style.addText("""body{
                        margin:0px;
                    } """)
        style.addText("""tablecontent{
                        margin:100px 0;
                        
                    } """)
        style.addText("""div.header > ul >  li > a:active{
                           font-weight:bold;
                    } """)
        style.addText(""".container{
                           overflow:auto;
                    } """)
        style.addText("""#footer {
                           position:fixed;
                           left:0px;
                           bottom:0px;
                           height:30px;
                           width:100%;
                           background:#444444;
                        } """)
        style.addText(""".copyright {
                        padding: 5px 0;
                        color: #FFF;
                        background: #444444;
                        margin: 0;
                        font-size: 12px;
                        text-align:center;
                    }""")
        return str(style)
     

if __name__ == "__main__":
    
    URL = "http://www.nseindia.com/live_market/dynaContent/live_analysis/gainers/"
    headers = {
                'User-Agent': '*/*',
               'Accept': 'application/plain',
            }
    NSEdoc = NSE(URL,headers)
    NSEdoc.getHtml()




