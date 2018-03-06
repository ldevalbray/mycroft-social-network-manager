from Levenshtein import ratio
# from selenium.common.exceptions import NoSuchElementException 
import requests  


def dist(name1, name2):
    if isinstance(name1, str):
        name1 = unicode(name1, "utf-8")
    if isinstance(name2, str):
        name2 = unicode(name2, "utf-8")
    return ratio(name1, name2)

def findMatchingString(name, listOfNames):
    closest = 0
    closestName = None
    for s in listOfNames:
        distance = dist(name, s)
        if( distance > closest):
            closest = distance
            closestName = s

    return closestName

def check_exists_by_xpath(xpath, driver):
    # try:
    #     driver.get_element(data=xpath, name="xpath", type="xpath")
    # except NoSuchElementException:
    #     return False
    return True

def check_exists_by_name(name, driver):
    # try:
    #     driver.get_element(data=name, name="name", type="name")
    # except NoSuchElementException:
    #     return False
    return True

def check_exists_by_id(id, driver):
    # try:
    #     driver.get_element(data=id, name="id", type="id")
    # except NoSuchElementException:
    #     return False
    return True

def is_number(n):
    try:
        float(n)
    except ValueError:
        return False
    return True

def getAllData(data, code):
    toReturn = {}
    for d in data["data"]:
        exec(code)
    while("next" in data["paging"]):
        data = requests.get(data["paging"]["next"]).json()
        for d in data["data"]:
            exec(code)
    
    return toReturn