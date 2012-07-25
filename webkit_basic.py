import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

class Render(QWebPage):  
  def __init__(self, urls):  
    self.app = QApplication(sys.argv)  
    QWebPage.__init__(self)  
    self.loadFinished.connect(self._loadFinished)  
    self.urls = urls  
    self.data = {} # store downloaded HTML in a dict  
    self.crawl()  
    self.app.exec_()  
      
  def crawl(self):  
    if self.urls:  
      url = self.urls.pop(0)  
      print 'Downloading', url  
      self.mainFrame().load(QUrl(url))  
    else:  
      self.app.quit()  
        
  def _loadFinished(self, result):  
    frame = self.mainFrame()  
    url = str(frame.url().toString())  
    html = frame.toHtml()  
    self.data[url] = html  
    self.crawl()  
  
urls = ['http://sitescraper.net', 'http://sitescraper.net/blog']  
r = Render(urls)
