import requests, urllib.parse, json, sys
import urllib.request
from bs4 import BeautifulSoup
if(len(sys.argv) < 2):
	print("need an url")
	exit()
url = sys.argv[1]
video_id = urllib.parse.urlparse(url).path.replace("/","")
streams=[]

try:
	title = BeautifulSoup(requests.get(url).content.decode(), 'html.parser').find('title').string
	json_response = json.loads(requests.get("https://player.vimeo.com/video/"+str(video_id)+"/config").content.decode())
	for obj in json_response["request"]["files"]["progressive"]:streams.append({"quality":obj["quality"],"url":obj["url"]})
	streams.sort(key=lambda stream: int(stream["quality"].replace("p","")),reverse=True)
	i=1
	for stream in streams:
		print(str(i)+"-"+stream["quality"])
		i=i+1
	choice = int(input("Choose: "))
	print(streams[choice-1]["quality"]+":\t"+streams[choice-1]["url"])
	if(input("Download? (yes/no) ")!="yes"):
		print("Exiting...")
		exit()
	print("Downloading...")
	urllib.request.urlretrieve(streams[choice-1]["url"], title+" ("+streams[choice-1]["quality"]+")"+'.mp4') 
	print("Completed.")
except Exception as exception:
	print(exception)