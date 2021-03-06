import pickle
from pprint import pprint
import urllib.request
import smtplib

# Outputs first job posting and ending position
def get_next_entry(html_block):
    start_point = html_block.find('<a href=')
    if start_point == -1:
        return None, 0
    start_entry = html_block.find('"',start_point)
    end_point = html_block.find('"DNN_News_ItemDetails"')
    end_entry = html_block.find('</p>',end_point)
    entry = html_block[start_entry:end_entry-1]
    return entry, end_entry
    
def send_jobs():
# Uses get_next_entry() to crawl through the html source code and append all job postings to raw_entries
    file = urllib.request.urlopen('https://www.wildlife.ca.gov/Employment/Seasonal')
    html = str(file.read())
    raw_entries = []
    block_start = html.find('<div class="normal">')
    block_end = html.find('<div style="display')
    html_block = html[block_start:block_end]
    while True:
        entry, end_entry = get_next_entry(html_block)
        if entry:
            raw_entries.append(entry)
            html_block = html_block[end_entry:]
        else:
            break
# Cleans up raw_entries and creates dictionary, adding location as key and date/url as value
    entries = {}
    for entry in raw_entries:
        start_loc = entry.find('ocated in')+10
        end_loc = entry.find('.',start_loc+1)
        if start_loc == -1:
            location = 'Unknown'
        else:
            location = entry[start_loc:end_loc]
        start_dat = entry.find('osted on')+9
        end_dat = entry.find('.',start_dat)
        if start_dat == -1:
            date = 'Unknown'
        else:
            date = entry[start_dat:end_dat]
        start_link = entry.find('<a href=')+2
        end_link = entry.find('"', start_link + 1)     
        url = entry[start_link:end_link]
        if location in entries:
            entries[location].append([date,url])
        else:
            entries[location]=[[date,url]]
# Selects San Diego and La Jolla location keys and adds to new dictionary
    sd_entries = {}
    for entry in entries:
        if 'iego' in entry:
            if entry in sd_entries:
                sd_entries[entry].append(entries[entry])
            if not entry in sd_entries:
                sd_entries[entry] = entries[entry]
        elif 'olla' in entry:
            if entry in sd_entries:
                sd_entries[entry].append(entries[entry])
            if not entry in sd_entries:
                sd_entries[entry] = entries[entry]  
# Saves the new day's sd_entries to file
    pickle.dump(sd_entries, open( "C:/Users/Dan Averbuj/Documents/Misc/Programming/save.p", "wb" ) )
    new=sd_entries
# Loads yesterday's sd_entries into variable
    old = pickle.load( open( "C:/Users/Dan Averbuj/Documents/Misc/Programming/save.p", "rb" ) )
# Finds any differences between yesterday's and today's sd_entries and adds to new dictionary
    diff = {}
    if old != new:
        keys = old.keys()
        for key in keys:
            if old[key] != new[key]:
                if not key in diff:
                    nt = [tuple(x) for x in new[key]]
                    ot = [tuple(x) for x in old[key]]
                    diff[key] = list(set(nt) - set(ot))
                else:
                    diff[key].append(list(set(nt) - set(ot)))
    else:
        return False
    pickle.dump(sd_entries, open( "C:/Users/Dan Averbuj/Documents/Misc/Programming/save.p", "wb" ) )
# Sends email with the results
    content = ''
    if diff:
        for entry in diff:
            for loc in diff[entry]:
                date = loc[0]
                location = entry
                url = loc[1]
                if content == '':
                    content = """Subject: New CDFW job(s) in San Diego!
    A job was added on %s at %s, here's the job description:
    %s""" % (date,location,url)
                else:
                    content = content + """\n    A job was added on %s at %s, here's the job description:
    %s""" % (date,location,url)
    else:
        content = """Subject: No New CDFW jobs

    No new jobs in San Diego were added today"""
    mail = smtplib.SMTP('smtp.gmail.com',587)
    mail.ehlo()
    mail.starttls()
    mail.login('daverbuj1@gmail.com','PASSWORDHERE')
    mail.sendmail('daverbuj1@gmail.com','dan.averbuj@gmail.com', content)
    mail.close()
