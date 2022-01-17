import json
from selenium import webdriver
from bs4 import BeautifulSoup
import regex as re
import os
import time
from multiprocessing.pool import ThreadPool
import pyperclip
import Build_Sqlite_Database
import dateutil.parser
from datetime import datetime, timezone

def time_passed(postdate):
    #Parse the postdate to make it a datetime.datetime tuple
    datetime_object = dateutil.parser.parse(postdate)

    #And convert it from datetime.datetime to time.time now
    posttime = time.mktime(datetime_object.timetuple())

    #Get the current time
    currenttime = time.time()

    #And see how many seconds have passed since the posttime
    passed = currenttime - posttime
    #If more than a day (= 86,400 seconds, return More than a day)
    if passed >= 86400:
        return 'More than a day'
    #If less than that, return Less than a day
    else:
        return 'Less than a day'

def clean_text(text):
    #performs a few cleaning steps to remove non-alphabetic characters

    #replace new line and carriage return with space
    text = text.replace("\n", " ").replace("\r", " ")
    #replace the numbers and punctuation (exclude single quote) with space
    punc_list = '!"#$%&()**+,-./:;<=>?@[\]^_{|}~' + '0123456789'
    t = str.maketrans(dict.fromkeys(punc_list, " "))
    text = text.translate(t)

    #replace single quote with empty character
    t = str.maketrans(dict.fromkeys("'`", ""))
    text = text.translate(t)

    return text

def word_tokenize(text):
    #Make a list of all the existing words
    WORD = re.compile(r'\w+')
    #Clean all punctuation, etc.
    text = clean_text(text)
    #And find all words
    words = WORD.findall(text)
    return words

def WaitForReply(waittime, totaltime):
    # Let's wait for a reply
    # The while loop runs for the amount of seconds indicated by totaltime if nothing happens
    # Check every waittime seconds if a reply was made
    mustend = time.time() + totaltime
    while time.time() < mustend:
        #Try to obtain the clipboard information. If we get an error, we'll just wait 3 seconds and try again.
        try:
            # If nothing was copied, take a nap
            if pyperclip.paste() == ' ':
                time.sleep(waittime)
            else:
                # If something was copied, we're going to move onward with that HTML code snippet.
                commenthtml = pyperclip.paste()
                break
        except KeyError:
            time.sleep(waittime)

    return commenthtml

def WaitForReply_par(waittime, totaltime):
    #Function to make our wait_until function less taxing on a computer
    pool = ThreadPool(processes=1)
    async_result = pool.apply_async(WaitForReply, (waittime, totaltime))
    return_val = async_result.get()
    return return_val

def nuscraper(url):
    #Start the clipboard empty
    pyperclip.copy(" ")
    currentpath = os.getcwd()
    #Load chromedriver
    chromedriver = currentpath + '/chromedriver.exe'
    os.environ["webdriver.chrome.driver"] = chromedriver
    #Set some options
    chrome_options = webdriver.ChromeOptions()
    #Make it headless, so that we don't have to see the browser window
    #chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--disable-infobars")
    # Create a chrome profile for this, but this can be turned off
    chrome_options.add_argument("user-data-dir=" + currentpath + "/Google_Profile")
    driver = webdriver.Chrome(chromedriver, options=chrome_options)
    #Load the URL
    driver.get(url)
    #Wait for a bit for it to load
    time.sleep(3)
    #If we need to click the Cookie wall button, we do so.
    try:
        button_css = '//*[@id="onetrust-accept-btn-handler"]'
        button = driver.find_element_by_xpath(button_css)
        button.click()
    except:
        pass

    #And then you have 30 minutes to get the comment element
    commenthtml = WaitForReply_par(2, 1800)
    #Get the page source containing all the text information
    page_source = driver.page_source
    #If the comment element is copied, we close the chrome tab.
    driver.close()
    #Return the source with the information to get the text, and the commenthtml-element
    return page_source, commenthtml

def get_text(page_source):
    #Get the source html in xml format
    soup = BeautifulSoup(page_source, "lxml")

    #Get the text, every paragraph is contained in p tags, and subheaders in h2 elements
    try:
        text = soup.find('div', {"class": "block article-body"}).find('div', {"class": "block-content"}).find_all(lambda t: t.name in ('p', 'h2'))
    except AttributeError:
        pass
    newtext = ''
    try:
        for idx, line in enumerate(text):
            #Get the paragraph text and add a whiteline if it's not the last paragraph
            newline = line.text.strip()
            newtext += newline
            if idx != len(text) - 1:
                newtext += '\n\n'
    except UnboundLocalError:
        pass

    return newtext

def get_comments(comments):
    # Get the source html in xml format
    soup = BeautifulSoup(comments, 'lxml')

    #Find all the comments (they all start with the same div class bit)
    regex = re.compile('talk-stream-comment-wrapper talk-stream-comment-wrapper(.*?)$')
    commentlist = soup.find_all("div", {"class": regex})

    toplevelcomment = []

    #Iterate over each comment
    for comment in commentlist:
        try:
            #Get the authorname (starts with the same span class bit)
            userregex = re.compile(r'AuthorName__name(.*?)$')
            username = comment.find('span', {'class': userregex}).text.strip()
        except AttributeError:
            continue

        #Get the timestamp (starts with the same span class bit)
        timestampregex = re.compile(r'CommentTimestamp__timestamp(.*?)$')
        timestamp = comment.find('span', {'class': timestampregex}).text.strip()

        #Get the comment content (same div class bit)
        contentregex = re.compile(r'Comment__content(.*?)$')
        content = comment.find('div', {'class': contentregex})
        #And make sure the linebreaks are respected (they are converted to ugly HTML)
        content = re.sub(r'<br class="talk-plugin-comment-content-linebreak"/></span>', '\n', str(content))
        content = BeautifulSoup(content, 'lxml').text.strip()

        #Get the number of respects for a comment
        respectnumber = comment.find('span', {'class': 'talk-plugin-respect-count'}).text.strip()

        #You can reply to comments. Those replies are given levels (no-reply is level 0, reply to that comment is level 1, reply to level 1 comment is level 2, etc. etc.
        #First, we need to find the level of the comment
        levelregex = re.compile('talk-stream-comment talk-stream-comment(.*?)$')
        levellist = comment.find("div", {"class": levelregex})['class']
        levelstring = ''
        for lvl in levellist:
            if 'level' in lvl:
                levelstring = re.search(r'level-(.*?)$', lvl).group(1)
                break
        levelstring = int(levelstring)

        #And make a nice dictionary that contains all the comment information (including a list for comments on that comment)
        commentdict = {'username': username, 'timestamp': timestamp, 'currenttime': time.strftime("%d-%m-%Y %H:%M:%S"), 'content': content,
                       'respectnumber': respectnumber, 'level': levelstring, 'comments': []}

        #This piece of code decides where to add the comment dictionary. To the main list (level 0), to the list of comments on a comment.
        #I got a bit of a headache writing this, but I think it works. I haven't seen anything beyond level 3, but let's just be sure that we collect deeper comments as well if they exist.
        if levelstring == 0:
            toplevelcomment.append(commentdict)  
        if levelstring == 1:
            try:
                toplevelcomment[-1]['comments'].append(commentdict)
            except IndexError:
                continue
        if levelstring == 2:
            try:
                toplevelcomment[-1]['comments'][-1]['comments'].append(commentdict)
            except IndexError:
                continue
        if levelstring == 3:
            try:
                toplevelcomment[-1]['comments'][-1]['comments'][-1]['comments'].append(commentdict)
            except IndexError:
                continue
        if levelstring == 4:
            try:
                toplevelcomment[-1]['comments'][-1]['comments'][-1]['comments'][-1]['comments'].append(commentdict)
            except IndexError:
                continue
        if levelstring == 5:
            try:
                toplevelcomment[-1]['comments'][-1]['comments'][-1]['comments'][-1]['comments'][-1]['comments'].append(commentdict)
            except IndexError:
                continue

    return toplevelcomment

def main_save(articletext, articlecomments, title, url, description, pubdate, permlink, image, catlist, creator, rights, rssfeed):
    #Tokenize the text to find the amount of words
    postlength = word_tokenize(articletext)
    postlength = str(len(postlength)) + ' words'

    #And get the currenttime (the load-date) in the same format as the Nu.nl postdate
    currenttime = datetime.now()
    tz = datetime.now(timezone.utc).astimezone().strftime('%z')
    timestampStr = currenttime.strftime("%a, %d %b %Y %H:%M:%S " + tz)

    #Filename is going to be the number of the Nu.nl permlink
    filename = re.search(r'(.*?)\-\/(.*?)\/', permlink).group(2)
    # See if we can find the filename, if we can find it, we need to get a new filename
    currentpath = os.getcwd()
    if os.path.isfile(currentpath + '/ArticleJson/' + filename + '.json'):
        # Add (2) or (3), etc. to the filename (the first number, starting at 2, that is not already a filename, is chosen)
        for i in range(2, 9999):
            newfilename = filename + '(' + str(i) + ')'
            # If the new filename is not used before, we will use it as our filename value
            if not os.path.isfile(currentpath + '/ArticleJson/' + newfilename + '.json'):
                filename = newfilename
                break
    #We've got our unique filename now, so let's add the .json extension
    filename = filename + '.json'

    #Make a textdict containing all relevant info for the Jsonfile
    textdict = {'filename': filename, 'title': title, 'text': articletext, 'length': postlength, 'comments': articlecomments, 'load-date': timestampStr, 'url': url, 'description': description, 'pubdate': pubdate, 'permlink': permlink, 'image': image, 'catlist': catlist, 'creator': creator, 'rights': rights, 'rssfeed': rssfeed}

    # Write JSON file
    with open(currentpath + '/ArticleJson/' + filename, 'w') as outfile:
        json.dump(textdict, outfile, indent=4, separators=(',', ': '))

def main():
    #This is the main function that does all our comment collection stuff.
    #First get the database with all saved articles and read it.
    allrows = Build_Sqlite_Database.database_read_rows('URLlist.db')
    #And parse it; every row is one article 
    for row in allrows:
        title, url, description, pubdate, permlink, image, catlist, creator, rights, rssfeed, iscollected, rowidx = Build_Sqlite_Database.parse_rows(row)
        #If the comment is already collected, we can skip it.
        if iscollected == 'x':
            continue
        #If less than a day has passed since publishing, skip it as well.
        if time_passed(pubdate) == 'Less than a day':
            continue
        #Otherwise, we can start collecting the page source and commenthtml
        page_source, commenthtml = nuscraper(permlink)
        #Let's parse the page_source to get the text
        articletext = get_text(page_source)
        #And let's parse the comments
        articlecomments = get_comments(commenthtml)
        #Cool, cool. Now let's save all our information in a JSON format.
        main_save(articletext, articlecomments, title, url, description, pubdate, permlink, image, catlist, creator, rights, rssfeed)
        #And finally, mark this particular article as collected
        Build_Sqlite_Database.set_as_collected('URLlist.db', rowidx)

main()