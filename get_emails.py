import sys  
from webscraping import common, download  
  
def get_emails(website, max_depth):  
    """Returns a list of emails found at this website  
  
max_depth is how deep to follow links  
"""  
    D = download.Download()  
    return D.get_emails(website, max_depth=max_depth)  
  
if __name__ == '__main__':  
    try:  
        website = sys.argv[1]  
        max_depth = int(sys.argv[2])  
    except:  
        print 'Usage: %s <URL> <max depth>' % sys.argv[0]  
    else:  
        print get_emails(website, max_depth)
