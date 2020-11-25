import requests, urllib.parse, json, sys
import urllib.request
from bs4 import BeautifulSoup
import re

proxies={
	"https":"https://localhost:8080"
}



if(len(sys.argv) < 2):
	print("need an url")
	exit()

if(len(sys.argv) < 3):
	print("need the password")
	exit()

url = sys.argv[1]
password = sys.argv[2]
video_id = urllib.parse.urlparse(url).path.replace("/","")
streams=[]

try:

	import requests
	headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"}
	response = requests.get(url, headers=headers)
	soap_response = BeautifulSoup(response.content.decode(),'html.parser')
	scripts = soap_response.findAll('script')
	
	xsrf_token=""
	vuid=""

	for script in scripts:
		if(str(script).find(',"vimeo":{"xsrft":')!=-1):
			x=re.findall('\"xsrft\"\:\"\w*\.\w*\.\w*', script.string)
			xsrf_token = x[0].replace('"xsrft":"',"")

	if(xsrf_token==""): 
		print("Can't get xsrf token, exiting...")
		exit()

	for cookie in response.cookies:
		if cookie.name == "vuid":
			vuid = cookie.value

	if(vuid==""): 
		print("Can't get vuid cookie, exiting...")
		exit()



	url = "https://vimeo.com/"+str(video_id)+"/password"
	cookies = {"vuid": vuid}
	headers = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"}
	post_data = {"password": password, "is_review": '', "is_file_transfer": '', "token": xsrf_token}
	# response = requests.post(url, headers=headers, cookies=cookies, data=post_data, proxies=proxies, verify=False, allow_redirects=False)
	response = requests.post(url, headers=headers, cookies=cookies, data=post_data, allow_redirects=False)

	pass_cookie=""
	if response.status_code == 302:
		for cookie in response.cookies:
			if(cookie.name.replace("_password","")==video_id):
				pass_cookie = cookie.value


	if(pass_cookie==""): 
		print("Can't get pass cookie, exiting...")
		exit()


	url = "https://vimeo.com/"+video_id
	cookies = {video_id+"_password": pass_cookie}
	headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"}
	response = requests.get(url, headers=headers, cookies=cookies)


	config_url = ""

	title = BeautifulSoup(response.content.decode(), 'html.parser').find('title').string

	soap_response = BeautifulSoup(response.content.decode(),'html.parser')
	scripts = soap_response.findAll('script')
	for script in scripts:
		if(str(script).find('{"config_url":"')!=-1):
			x=re.findall('\{\"config_url\"\:\".*\"\,\"player_url\"', script.string)
			config_url = x[0].replace('","player_url"',"").replace('{"config_url":"',"").replace("\/","/")

	if(config_url==""): 
		print("Can't get config url, exiting...")
		exit()




	headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"}

	cookies = {video_id+"_password": pass_cookie}
	response = requests.get(config_url, headers=headers, cookies=cookies)


	json_response = json.loads(response.content.decode())
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