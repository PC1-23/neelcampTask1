from bs4 import BeautifulSoup
import requests 
import json
import re
import html



url = "https://www.campbirchwood.com/"
result = requests.get(url)
doc = BeautifulSoup(result.text, "html.parser")
allInfo = {"About": "", "Activities":[],"Camper Experience":"", "Testimonials" :[]} ##dictionary to keep track of all the info 

missionText = [] ##add all info about the mission statement
header1 = doc.find("h2") ##find header 
header1Txt  = header1.get_text().strip() + "." ##get text without the tags 
header2 = doc.find("h3") 
header2Txt = header2.get_text().strip()  
mission = doc.find_all("p", class_= "sqsrte-large")
missionText.append(header1Txt) 
missionText.append (header2Txt)
for element in mission:
    text = element.get_text().strip()
    missionText.append(text)

allInfo["About"]= " ".join(missionText)

##now extract and add all activities 
activitiesList = [] ##list for adding all activities 
activities = doc.find_all("h4", style="text-align:center;white-space:pre-wrap;")
for activity in activities:
    html_content = str(activity)
    content = re.sub(r'<h4[^>]*>|</h4>', '', html_content)
    activity_items = re.split(r'<br\s*/?>', content)
    for item in activity_items:
        clean_item = re.sub(r'<[^>]+>', '', item).strip()
        clean_item = html.unescape(clean_item)
        activitiesList.append(clean_item)
        
allInfo["Activities"] = activitiesList[6:len(activitiesList)]

##extract and add camper experience

experienceText = []
experienceHeader = doc.find("h3", string=re.compile(r"Welcome to your.*home away from home"))
parentDiv = experienceHeader.find_parent("div", class_="sqs-html-content")
experienceParagraphs = parentDiv.find_all("p", style="text-align:center;white-space:pre-wrap;")
for p in experienceParagraphs:
            text = p.get_text().strip()
            experienceText.append(text)
camperExperience = " ".join(experienceText)

allInfo["Camper Experience"] = camperExperience



##extract and add testimonials 
urlTestimonials = "https://www.campbirchwood.com/testimonials"
resultTestimonials = requests.get(urlTestimonials)
docTestimonials = BeautifulSoup(resultTestimonials.text, "html.parser")
testimonialDivs = docTestimonials.find_all("div", class_= "sqs-html-content")

testimonialsText =[]

for div in testimonialDivs:
    quotes = div.find_all("h4", style="text-align:center;white-space:pre-wrap;")
    for quoteElement in quotes:
        quoteText = quoteElement.get_text().strip()

        nextElement = quoteElement.find_next_sibling()
        author = ""
        role = ""
        while nextElement:
            if nextElement.name == 'p':
                strongTag = nextElement.find("strong")
                if strongTag:
                    authorText = strongTag.get_text().strip()
                    author = re.sub(r'^[-–—/\s]+', '', authorText)
                    fullText = nextElement.get_text().strip()
                    roleText = fullText.replace(authorText, '').strip()
                    role = re.sub(r'^[-–—/\s]+', '', roleText)
                    role = re.sub(r'//\s*', '', role)  #remove // separator
                    break

            nextElement = nextElement.find_next_sibling()
        if quoteText and roleText and author:
            testimonialsText.append({
                    "quote": quoteText,
                    "author": author,
                    "role": role
                })

allInfo["Testimonials"] = testimonialsText
with open('data.json', 'w') as file:
    json.dump(allInfo, file)
