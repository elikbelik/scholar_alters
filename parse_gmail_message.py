# -*- coding: utf-8 -*-
"""
Open emails and aggregate them together
"""

from connect_to_gmail import  *
import base64
from html.parser import HTMLParser
import webbrowser
from os import path as ospath
from os import makedirs
import pickle

DATA_FOLDER = r'.\data'
PAPERS_LABEL = 'Papers'
PREV_PAPERS_FILE = r'prev_papers.pickle'
ARCHIVE_TSV = r'archive.tsv'
BROWSER_COMMAND = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s"


def clean_title(st):
    if st[0] == '[':
        st = st[st.find(']')+1:]
    st = st.replace('\\xe2\\x80\\x8f','')
    return st.strip()
    

class Paper:
    def __init__(self, ref):
        self.title = ''
        self.data = ''
        self.link = ''
        self.idx = ''
        self.ref = [ref]
        self.chosen = 0
    
    def add_title(self,data):
        self.title += clean_title(data) + " "
        self.idx = self.title.strip().upper()
        
    def add_data(self,data):
        self.data += data + "\n"
        
    def add_ref(self, ref):
        self.ref.append(ref)
        
    def set_chosen(self):
        self.chosen = 1
        
    def __eq__ (self, paper):
        return self.idx == paper.idx
    
    def __str__ (self):
        return self.title + '\n\n' + self.data + '\n' + str(self.ref)
    
    def __repr__ (self):
        return self.title

    
class PapersHTMLParser(HTMLParser):
    def __init__ (self, author_ref):
        HTMLParser.__init__(self)
        self.is_title = False
        self.papers = []
        self.ref = author_ref
        
    def handle_starttag(self, tag, attrs):
        if tag == 'h3':
            self.papers.append(Paper(self.ref))
            self.is_title = True
        if tag == 'a' and self.is_title:
            for attr in attrs:
                if attr[0].lower() == 'href':
                    self.papers[-1].link = attr[1]

    def handle_endtag(self, tag):
        if tag == 'h3':
            self.is_title = False

    def handle_data(self, data):
        if len(self.papers) > 0:
            if self.is_title:
                self.papers[-1].add_title(data)
            else:
                self.papers[-1].add_data(data)
         
            
class PaperAggregator:
    def __init__ (self):
        self.paper_list = []
        
    def add(self, paper):
        try:
            idx = self.paper_list.index(paper)
            self.paper_list[idx].add_ref(paper.ref[0])
        except ValueError: # Paper not in the list
            self.paper_list.append(paper)
            
    def remove(self, paper):
        try:
            idx = self.paper_list.index(paper)
            self.paper_list.pop(idx)
        except ValueError: # Paper not in the list
            pass
    
    
if __name__ == '__main__':
    # Create data folder if not exists
    if not ospath.exists(DATA_FOLDER):
        makedirs(DATA_FOLDER)
    
    # Call the Gmail API
    service = get_service(DATA_FOLDER)
    
    # Get all the messages with labels
    labels = GetLabelsId(service,'me',[PAPERS_LABEL,'UNREAD'])
    messages = ListMessagesWithLabels(service,"me",labels)
    print ('Found %d messages'%len(messages))
    
    # Parse the mails
    pa = PaperAggregator()
    
    for msg in messages:
        msg_content = GetMessage(service, "me", msg['id'])
        try:
            msg_str = base64.urlsafe_b64decode(msg_content['payload']['body']['data'].encode('ASCII'))
        except KeyError:
            continue
        
        msg_title = ''
        for h in msg_content['payload']['headers']:
            if h['name'] == 'Subject':
                msg_title = h['value']
        parser = PapersHTMLParser(msg_title)
        parser.feed(str(msg_str))
        
        for paper in parser.papers:
            pa.add(paper)
            
    # Remove previously seen papers
    pickle_file = ospath.join(DATA_FOLDER, PREV_PAPERS_FILE)
    if ospath.exists(pickle_file):
        with open(pickle_file,'rb') as pkl:
            old_pa = pickle.load(pkl)
            for paper in old_pa.paper_list:
                pa.remove(paper)
    
    # Sort by number of refernece mails
    pa.paper_list.sort(key=lambda a: len(set(a.ref)),reverse=True)
    print ('Found %d papers'%len(pa.paper_list))
    
    # User Input
    counter = 1
    good_papers = []
    web = webbrowser.get(BROWSER_COMMAND)
    for paper in pa.paper_list:
        print ('\n\n' + '-'*100 + '\n\n')
        print('Message %d / %d\n'%(counter,len(pa.paper_list)))
        print(paper)
        response = input("Interesting? (y/n) ")
        if response.strip()[:1].lower() == 'y':
            good_papers.append(paper)
            paper.set_chosen()
        counter+=1
        
    print("Now processing...")
    
    # Write current papers
    with open(pickle_file,'wb') as pkl:
        pickle.dump(pa,pkl)
        
    # Open papers
    first_open = 1
    for paper in good_papers:
        web.open(paper.link,new=2-first_open)
        first_open = 0
    
    # Mark all as read
    body = {"addLabelIds": [], "removeLabelIds": ["UNREAD","INBOX"]}
    for msg in messages:
        service.users().messages().modify(userId="me", id=msg['id'],
                                          body=body).execute()
                                          
    # Archive the results for later learning
    with open(ospath.join(DATA_FOLDER, ARCHIVE_TSV),'a', encoding="utf-8") as f:
        for paper in pa.paper_list:
            f.write('{title}\t{authors}\t{ref}\t{selected}\n'.format(title=paper.title,authors=paper.data.split('\n')[0],ref=paper.ref,selected=paper.chosen))
            

