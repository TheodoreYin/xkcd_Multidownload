import requests ,threading, os, logging
from bs4 import BeautifulSoup
logging.basicConfig(filename = "multiDownload.log", level = logging.DEBUG, format = "%(asctime)s - %(levelname)s - %(message)s")

faillist= []

url = "http://xkcd.com/"


def GetOnePage(comicNum):
    logging.debug("Page {0} Downloading".format(comicNum))    
    resp = requests.get(url + comicNum + '/')
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    imgurl = soup.select('#comic img')
    if imgurl == []:
        logging.debug("Page {0} not found.".format(comicNum))
        return None
    return imgurl[0].get("src")

def DownloadOnePage(comicNum, pagesrc):
    logging.debug("Page {0} downloading from src: {1}".format(comicNum, pagesrc))
    resp = requests.get("http:" + pagesrc)
    resp.raise_for_status()
    logging.debug("Page {0} downloaded succesfully".format(comicNum))
    with open("comics/xkcd." + str(comicNum) + os.path.basename(pagesrc), "wb") as fh:
        for each in resp.iter_content(100000):
            fh.write(each)
        logging.debug("Page {0} saved.".format(comicNum))
    
def download(comicNum):
    logging.info("Thread {0} started!".format(threading.get_ident()))
    try:
        DownloadOnePage(comicNum, GetOnePage(comicNum))
    except Exception as ex:
        logging.error("A exception occured in thread {0} : {1}".format(threading.get_ident(), ex))
        faillist.append(comicNum)
    logging.info("Thread {0} ended.".format(threading.get_ident()))


def multidownload():
    downloadthreads = []
    for i in range(1400):
        thread = threading.Thread(target = download, args = [i])
        downloadthreads.append(thread)
        thread.start()
        logging.info("thread {0} started".format(threading.get_ident()))
    return downloadthreads

if __name__ == "__main__":
    if not os.path.exists("comics"):
        os.mkdir("comics")
    downloadthreads = multidownload()
    for thread in downloadthreads:
        thread.join()
    print("A list of download fialed pages:\n", faillist)