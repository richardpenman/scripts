import sys
from collections import deque # threadsafe datatype
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
NUM_THREADS = 3 # how many threads to use

class Render(QWebView):
    active = deque() # track how many threads are still active
    data = {} # store the data

    def __init__(self, urls):
        QWebView.__init__(self)
        self.loadFinished.connect(self._loadFinished)
        self.urls = urls
        self.crawl()

    def crawl(self):
        try:
            url = self.urls.pop()
            print 'downloading', url
            Render.active.append(1)
            self.load(QUrl(url))
        except IndexError:
            # no more urls to process
            if not Render.active:
                # no more threads downloading
                print 'finished'
                self.close()

    def _loadFinished(self, result):
        # process the downloaded html
        frame = self.page().mainFrame()
        url = str(frame.url().toString())
        Render.data[url] = frame.toHtml()
        Render.active.popleft()
        self.crawl() # crawl next URL in the list

app = QApplication(sys.argv) # can only instantiate this once so must move outside class 
urls = deque(['http://sitescraper.net', 'http://sitescraper.net/questions',
    'http://sitescraper.net/blog', 'http://sitescraper.net/projects'])
renders = [Render(urls) for i in range(NUM_THREADS)]
app.exec_() # will execute qt loop until class calls close event
