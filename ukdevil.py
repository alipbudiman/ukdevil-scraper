import json
import random
import concurrent.futures
import time
import urllib
import uuid
import os
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote
import urllib.request
from flask import Flask, jsonify, request

CONFIG = {
    "PORT":5005,
    "DEBUG":False,
    "HOST":"0.0.0.0"
}

HOST = "https://ukdevilz.com"
VIDEO_HOST = "video"
WATCH_HOST = "watch"

try:
  clearport = str(os.popen(f"lsof -t -i:{CONFIG['PORT']}").read()).split("\n")
  for x in clearport:
      if x != '':
          os.system(f"kill -9 {x}")
except:pass

def AlterWarning(que):
    r = f"{HOST}/{VIDEO_HOST}/{quote(que)}"
    result = requests.get(r)
    data = BeautifulSoup(result.content, "html5lib")
    for i in data.findAll("div", attrs={"class": "alert_warning"}):
        return i.text

def AlterWarningURL(url):
    result = requests.get(url)
    data = BeautifulSoup(result.content, "html5lib")
    for i in data.findAll("div", attrs={"class": "alert_warning"}):
        return i.text

def Query(que):
    data_list = []
    img_list = []
    r = f"{HOST}/{VIDEO_HOST}/{quote(que)}"
    for x in range(3):
        HostMax = "?p=" + str(random.randint(1,100))
        HosMerger = f"{HOST}/{VIDEO_HOST}/{quote(que)}{HostMax}"
        aw = AlterWarningURL(HosMerger)
        if aw == None:
            r = HosMerger
            break
    result = requests.get(r)
    data = BeautifulSoup(result.content, "html5lib")
    for i in data.findAll("div", attrs={"class": "item"}):
        for j in i.findAll("a"):
            data_list.append(f"{HOST}{j.get('href')}")
        for x in i.findAll("img"):
            img_list.append(x.get('data-src'))
    
    return data_list, img_list

def OpenIframe(url):
    res = ""
    n = ""
    result = requests.get(url)
    data = BeautifulSoup(result.text, "html.parser")
    for i in data.findAll("iframe", attrs={"id":"iplayer"}):
        res = f"{HOST}{i['src']}"
    for x in data.findAll("div", attrs={"class":"l_info"}):
        n = x.find("h1").text
    return res, n

def OpenEmbed(url, name):
    result = requests.get(url)
    data = BeautifulSoup(result.content, "html.parser")
    script_tags = data.find_all('script')
    for sc in script_tags:
        script = str(sc)
        if "window.playlistUrl=" in script:
            scriptS = script.split("';window.ads=")[0].replace("<script>window.playlistUrl='", "")
            r = f"{HOST}{scriptS}"
            rg = requests.get(r).json()
            rg = rg["sources"]
            return {
                "file":(rg[0])["file"],
                "name":name
            }


def Randomname():  
    # Generate a random UUID
    random_uuid = str(uuid.uuid4()) + str(time.time()) + str(random.randint(1111,9999))
    file_name = random_uuid + ".jpg"
    return file_name

def DownloadImage(image_url):
    file_name = Randomname()
    req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})

    try:
        # Open the URL and download the image
        with urllib.request.urlopen(req) as response, open(file_name, 'wb') as out_file:
            out_file.write(response.read())
        return file_name
    except urllib.error.HTTPError as e:
        pass

def fxprint(djson, ind=4):
    print(json.dumps(djson, indent=ind, sort_keys=True))

def RunUkDevil(Vquery:str):
    res = []
    def OpenIframeAndEmbed(nl, im):
        u,n = OpenIframe(nl)
        nlr = OpenEmbed(u,n)
        nlr["img"] = im
        res.append(nlr)

    aw = AlterWarning(Vquery)
    if aw == None:
        newlist = []
        imgs = []
        mylist, img = Query(Vquery)
        for num, x in enumerate(mylist):
            if "watch/-" in x:
                newlist.append(x)
                imgs.append(img[num])
        with concurrent.futures.ThreadPoolExecutor(max_workers=99) as executor:
            if len(newlist) <= 0:
                return {
                    "status":404,
                    "results":res,
                    "message":"video not found"
                }
            for nums, nl in enumerate(newlist):
                executor.submit(OpenIframeAndEmbed, nl, imgs[nums])
            c = 0
            while True:
                c += 1
                time.sleep(1)

                # create stop
                if len(newlist) <= len(res):
                    return {
                        "status":200,
                        "results":res
                    }

                # create time out
                if c >= 10:
                    return {
                        "status":200,
                        "results":res
                    }
    else:
        return {
            "status":404,
            "results":res,
            "message":"video not found"
        }


app = Flask(__name__)

@app.errorhandler(Exception)
def handle_error():
    return jsonify({
        "status":500,
        "results":[],
        "message":"bad request"
    }), 500

@app.route("/ukdevil",methods=["GET"])
def ukdevil():
    s = request.args.get('s')
    if s:
        return jsonify(RunUkDevil(s))
    else:
        return jsonify({
            "status":500,
            "results":[],
            "message":"bad request"
        })

if __name__ == "__main__":
    app.run(host=CONFIG["HOST"],debug=CONFIG["DEBUG"], port=CONFIG["PORT"])
