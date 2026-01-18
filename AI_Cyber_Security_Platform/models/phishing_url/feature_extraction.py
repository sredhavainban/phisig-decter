from urllib import parse
import re
import ipaddress
import posixpath
import os
import csv
from datetime import datetime
import requests
from urllib.parse import urlparse, parse_qs
import whois
from datetime import datetime
import requests

def attributes():
    """Output file attributes."""
    lexical = [
    'dot_url', 'hyphe_url', 'underline_url', 'bar_url', 'question_url',
    'equal_url', 'arroba_url', 'ampersand_url', 'exclamation_url',
    'blank_url', 'til_url', 'comma_url', 'plus_url', 'asterisk_url', 'hashtag_url',
    'money_sign_url', 'percentage_url', 'count_tld_url', 'len_url', 'alpha_url', 'timeresponse_url',
    'time_domain_activation_url', 'time_domain_expiration_url', 'Hasshortner_URL',
    'dot_host','hyphe_host', 'underline_host', 'bar_host', 'question_host', 'equal_host',
    'arroba_host', 'ampersand_host', 'exclamation_host', 'blank_host', 'til_host',
    'comma_host', 'plus_host', 'asterisk_host', 'hashtag_host', 'money_sign_host',
    'percentage_host', 'vowels_host', 'len_host', 'ip_exist', 'server_client',
    'dot_path', 'hyphe_path', 'underline_path', 'bar_path', 'question_path',
    'equal_path', 'arroba_path', 'ampersand_path', 'exclamation_path',
    'blank_path', 'til_path', 'comma_path', 'plus_path', 'asterisk_path',
    'hashtag_path', 'money_sign_path', 'percentage_path', 'len_path', 'dot_file',
    'hyphe_file', 'underline_file', 'bar_file', 'question_file', 'equal_file',
    'arroba_file', 'ampersand_file', 'exclamation_file', 'blank_file',
    'til_file', 'comma_file', 'plus_file', 'asterisk_file', 'hashtag_file',
    'money_sign_file', 'percentage_file', 'len_file', 'dot_params',
    'hyphe_params', 'underline_params', 'bar_params', 'question_params',
    'equal_params', 'arroba_params', 'ampersand_params', 'exclamation_params',
    'blank_params', 'til_params', 'comma_params', 'plus_params', 'asterisk_params',
    'hashtag_params', 'money_sign_params', 'percentage_params', 'len_params',
    'tld_params', 'number_params', 'email_exist', 'extension'
        ]


    list_attributes = []
    list_attributes.extend(lexical)

    return list_attributes




shortening_services = (
    r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|"
    r"yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|"
    r"short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|"
    r"doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|db\.tt|"
    r"qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|is\.gd|"
    r"po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|"
    r"prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|"
    r"tr\.im|link\.zip\.net|"
    r"0rz\.tw|1-url\.net|126\.am|1tk\.us|1un\.fr|1url\.com|1url\.cz|1wb2\.net|2\.gp|2\.ht|"
    r"2ad\.in|2doc\.net|2fear\.com|2tu\.us|2ty\.in|2u\.xf\.cz|3ra\.be|3x\.si|4i\.ae|4ks\.net|"
    r"4view\.me|5em\.cz|5url\.net|5z8\.info|6fr\.ru|6g6\.eu|7\.ly|76\.gd|77\.ai|7fth\.cc|"
    r"7li\.in|7vd\.cn|8u\.cz|944\.la|98\.to|L9\.fr|Lvvk\.com|To8\.cc|a0\.fr|abbr\.sk|ad-med\.cz|"
    r"ad5\.eu|ad7\.biz|adb\.ug|adf\.ly|adfa\.st|adfly\.fr|adli\.pw|adv\.li|ajn\.me|aka\.gr|"
    r"alil\.in|amzn\.to|any\.gs|aqva\.pl|ares\.tl|asso\.in|au\.ms|ayt\.fr|azali\.fr|b00\.fr|"
    r"b23\.ru|b54\.in|baid\.us|bc\.vc|beam\.to|bee4\.biz|bim\.im|bit\.do|bit\.ly|bitly\.com|"
    r"bitw\.in|blap\.net|ble\.pl|blip\.tv|boi\.re|bote\.me|bougn\.at|br4\.in|brk\.to|brzu\.net|"
    r"bul\.lu|bxl\.me|bzh\.me|cachor\.ro|captur\.in|cashfly\.com|cbs\.so|cbug\.cc|cc\.cc|ccj\.im|"
    r"cf\.ly|cf2\.me|cf6\.co|chilp\.it|cjb\.net|cli\.gs|clikk\.in|clk\.im|cn86\.org|couic\.fr|"
    r"cr\.tl|cudder\.it|cur\.lv|curl\.im|curte\.me|cut\.pe|cut\.sk|cutt\.eu|cutt\.us|cutu\.me|"
    r"cybr\.fr|cyonix\.to|d75\.eu|daa\.pl|dai\.ly|decenturl\.com\.br|dd\.ma|ddp\.net|dft\.ba|"
    r"digbig\.com|doiop\.com|dolp\.cc|dopice\.sk|droid\.ws|dv\.gd|dyo\.gs|e37\.eu|easyurl\.net|"
    r"ecra\.se|ely\.re|encurtador\.com\.br|erax\.cz|erw\.cz|esy\.es|ex9\.co|ezurl\.cc|fff\.re|"
    r"fff\.to|fff\.wf|filz\.fr|fnk\.es|foe\.hn|folu\.me|freze\.it|fur\.ly|fwdurl\.net|g00\.me|"
    r"gca\.sh|gg\.gg|goo\.gl|goo\.lu|grem\.io|guiama\.is|hadej\.co|hide\.my|hjkl\.fr|hops\.me|"
    r"href\.li|ht\.ly|i-2\.co|i99\.cz|icit\.fr|ick\.li|icks\.ro|iiiii\.in|iky\.fr|ilix\.in|"
    r"info\.ms|is\.gd|isra\.li|itm\.im|ity\.im|ix\.sk|j\.gs|j\.mp|jdem\.cz|jieb\.be|jp22\.net|"
    r"jqw\.de|kask\.us|kd2\.org|kfd\.pl|korta\.nu|kr3w\.de|krat\.si|kratsi\.cz|krod\.cz|kuc\.cz|"
    r"kxb\.me|l-k\.be|lc-s\.co|lc\.cx|lcut\.in|letop10\.|libero\.it|lick\.my|lien\.li|lien\.pl|"
    r"lin\.io|linkn\.co|linkbucks\.com|llu\.ch|lnk\.co|lnk\.ly|lnk\.sk|lnks\.fr|lnky\.fr|lnp\.sn|"
    r"lp25\.fr|m1p\.fr|m3mi\.com|make\.my|mcaf\.ee|mdl29\.net|mic\.fr|migre\.me|minu\.me|moour"
)


def start_url(url):
    """Split URL into: protocol, host, path, params, query and fragment."""
    if not urlparse(url.strip()).scheme:
        url = 'http://' + url
    parsed_url = urlparse(url.strip())

    result = {
        'url': url,
        'protocol': parsed_url.scheme,
        'host': parsed_url.netloc,
        'path': parsed_url.path,
        'params': parsed_url.params,
        'query': parsed_url.query,
        'fragment': parsed_url.fragment
    }
    return result


def EnglishLetterCount(str):
    count = 0
    engletter = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    for num in str:
        if num in engletter:
            count = count + 1

    return count

def count(text, character):
    """Return the amount of certain character in the text."""
    return text.count(character)

def count_vowels(text):
    """Return the number of vowels."""
    vowels = ['a', 'e', 'i', 'o', 'u']
    count = 0
    for i in vowels:
        count += text.lower().count(i)
    return count

def length(text):
    """Return the length of a string."""
    return len(text)

def valid_ip(host):
    """Return if the domain has a valid IP format (IPv4 or IPv6)."""
    try:
        ipaddress.ip_address(host)
        return True
    except Exception:
        return False


def valid_email(text):
    """Return if there is an email in the text."""
    if re.findall(r'[\w\.-]+@[\w\.-]+', text):
        return True
    else:
        return False

def read_file(archive):
    """Read the file with the URLs."""
    with open(archive, 'r') as f:
        urls = ([line.rstrip() for line in f])
        return urls

def check_word_server_client(text):
    """Return whether the "server" or "client" keywords exist in the domain."""
    if "server" in text.lower() or "client" in text.lower():
        return True
    return False

def count_tld(text):
    """Return amount of Top-Level Domains (TLD) present in the URL."""
    file_path = './files/tlds.txt'
    file = open(file_path, 'r')
    count = 0
    pattern = re.compile("[a-zA-Z0-9.]")
    for line in file:
        i = (text.lower().strip()).find(line.strip())
        while i > -1:
            if ((i + len(line) - 1) >= len(text)) or not pattern.match(text[i + len(line) - 1]):
                count += 1
            i = text.find(line.strip(), i + 1)
    file.close()
    return count

def extract_extension(text):
    """Return file extension name."""
    file_path = './files/extensions.txt'
    file = open(file_path, 'r')

    pattern = re.compile("[a-zA-Z0-9.]")
    for extension in file:
        i = (text.lower().strip()).find(extension.strip())
        while i > -1:
            if ((i + len(extension) - 1) >= len(text)) or not pattern.match(text[i + len(extension) - 1]):
                file.close()
                return extension.rstrip().split('.')[-1]
            i = text.find(extension.strip(), i + 1)
    file.close()
    return -1

def check_tld(text):
    """Check for presence of Top-Level Domains (TLD)."""
    file_path = './files/tlds.txt'
    file = open(file_path, 'r')
    pattern = re.compile("[a-zA-Z0-9.]")
    for line in file:
        i = (text.lower().strip()).find(line.strip())
        while i > -1:
            if ((i + len(line) - 1) >= len(text)) or not pattern.match(text[i + len(line) - 1]):
                file.close()
                return True
            i = text.find(line.strip(), i + 1)
    file.close()
    return False

def count_params(text):
    """Return number of parameters."""
    return len(parse.parse_qs(text))
    
def read_csv_file(archive):
    """Read a CSV file and return its contents."""
    data = []
    with open(archive, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row)
    return data


def check_time_response(domain, timeout=3):
    """Return the response time in seconds."""
    try:
        response = requests.get(domain, headers={'Cache-Control': 'no-cache'}, timeout=timeout)
        latency = response.elapsed.total_seconds()
        return latency
    except requests.exceptions.Timeout:
        return -1  # Return 'l' if the request times out
    except requests.exceptions.RequestException:
        return -1  # Return '?' if an error occurs


def time_domain_activation(url):
    """Get the domain activation time (creation date) in days for a given URL."""
    try:
        domain = url.split('/')[2]
        domain_info = whois.whois(domain)

        if domain_info.creation_date:
            creation_date = domain_info.creation_date

            if isinstance(creation_date, list):
                creation_date = creation_date[0]

            current_date = datetime.now()
            activation_time_days = (current_date - creation_date).days

            return activation_time_days
        else:
            return -1

    except Exception as e:
        return -1


def time_domain_expiration(url):
    """Get the domain expiration time (expiration date) in days for a given URL."""
    try:
        domain = url.split('/')[2]
        domain_info = whois.whois(domain)

        if domain_info.expiration_date:
            expiration_date = domain_info.expiration_date

            if isinstance(expiration_date, list):
                expiration_date = expiration_date[0]

            current_date = datetime.now()
            time_until_expiration_days = (expiration_date - current_date).days

            return time_until_expiration_days
        else:
            print(f"Failed to retrieve expiration date for the domain: {domain}")
            return -1

    except Exception as e:
        print(f"Error occurred while fetching domain expiration time: {e}")
        return -1


def qty_redirects(url):
    """Check if a URL is redirected."""
    try:
        response = requests.head(url, allow_redirects=True)
        if response.status_code in (301, 302):
            return True
        else:
            return False

    except requests.RequestException as e:
        print(f"Error occurred while checking URL redirection: {e}")
        return None


def shortner_URL(url):
    match = re.search(shortening_services, url)
    if match:
        return True
    else:
        return False


def main(url):
    dict_url = start_url(url)

    dot_url = str(count(dict_url['url'],'.'))
    hyphe_url = str(count(dict_url['url'],'-'))
    underline_url = str(count(dict_url['url'],'_'))
    bar_url = str(count(dict_url['url'],'/'))
    question_url = str(count(dict_url['url'],'?'))
    equal_url = str(count(dict_url['url'],'='))
    arroba_url = str(count(dict_url['url'],'@'))
    ampersand_url = str(count(dict_url['url'],'&'))
    exclamation_url = str(count(dict_url['url'], '!'))
    blank_url = str(count(dict_url['url'], ' '))
    til_url = str(count(dict_url['url'], '~'))
    comma_url = str(count(dict_url['url'], ','))
    plus_url = str(count(dict_url['url'], '+'))
    asterisk_url = str(count(dict_url['url'], '*'))
    hashtag_url = str(count(dict_url['url'], '#'))
    money_sign_url = str(count(dict_url['url'], '$'))
    percentage_url = str(count(dict_url['url'], '%'))
    len_url = str(length(dict_url['url']))
    email_exist = str(valid_email(dict_url['url']))
    count_tld_url = str(count_tld(dict_url['url']))
    count_alpha_url=str(EnglishLetterCount(dict_url['url']))
    timeresponse_url=str(check_time_response(dict_url['url']))
    time_domain_activation_url=str(time_domain_activation(dict_url['url']))
    time_domain_expiration_url=str(time_domain_expiration(dict_url['url']))
    Hasshortner_URL=str(shortner_URL(dict_url['url']))
    dot_host = str(count(dict_url['host'], '.'))
    hyphe_host = str(count(dict_url['host'], '-'))
    underline_host = str(count(dict_url['host'], '_'))
    bar_host = str(count(dict_url['host'], '/'))
    question_host = str(count(dict_url['host'], '?'))
    equal_host = str(count(dict_url['host'], '='))
    arroba_host = str(count(dict_url['host'], '@'))
    ampersand_host = str(count(dict_url['host'], '&'))
    exclamation_host = str(count(dict_url['host'], '!'))
    blank_host = str(count(dict_url['host'], ' '))
    til_host = str(count(dict_url['host'], '~'))
    comma_host = str(count(dict_url['host'], ','))
    plus_host = str(count(dict_url['host'], '+'))
    asterisk_host = str(count(dict_url['host'], '*'))
    hashtag_host = str(count(dict_url['host'], '#'))
    money_sign_host = str(count(dict_url['host'], '$'))
    percentage_host = str(count(dict_url['host'], '%'))
    vowels_host = str(count_vowels(dict_url['host']))
    len_host = str(length(dict_url['host']))
    ip_exist = str(valid_ip(dict_url['host']))
    server_client = str(check_word_server_client(dict_url['host']))
    if dict_url['path']:
        dot_path = str(count(dict_url['path'], '.'))
        hyphe_path = str(count(dict_url['path'], '-'))
        underline_path = str(count(dict_url['path'], '_'))
        bar_path = str(count(dict_url['path'], '/'))
        question_path = str(count(dict_url['path'], '?'))
        equal_path = str(count(dict_url['path'], '='))
        arroba_path = str(count(dict_url['path'], '@'))
        ampersand_path = str(count(dict_url['path'], '&'))
        exclamation_path = str(count(dict_url['path'], '!'))
        blank_path = str(count(dict_url['path'], ' '))
        til_path = str(count(dict_url['path'], '~'))
        comma_path = str(count(dict_url['path'], ','))
        plus_path = str(count(dict_url['path'], '+'))
        asterisk_path = str(count(dict_url['path'], '*'))
        hashtag_path = str(count(dict_url['path'], '#'))
        money_sign_path = str(count(dict_url['path'], '$'))
        percentage_path = str(count(dict_url['path'], '%'))
        len_path = str(length(dict_url['path']))
    else:
        dot_path = -1
        hyphe_path = -1
        underline_path = -1
        bar_path = -1
        question_path = -1
        equal_path = -1
        arroba_path = -1
        ampersand_path = -1
        exclamation_path = -1
        blank_path = -1
        til_path = -1
        comma_path = -1
        plus_path = -1
        asterisk_path = -1
        hashtag_path = -1
        money_sign_path = -1
        percentage_path = -1
        len_path = -1
    if dict_url['path']:
        dot_file = str(count(posixpath.basename(dict_url['path']), '.'))
        hyphe_file = str(count(posixpath.basename(dict_url['path']), '-'))
        underline_file = str(count(posixpath.basename(dict_url['path']), '_'))
        bar_file = str(count(posixpath.basename(dict_url['path']), '/'))
        question_file = str(count(posixpath.basename(dict_url['path']), '?'))
        equal_file = str(count(posixpath.basename(dict_url['path']), '='))
        arroba_file = str(count(posixpath.basename(dict_url['path']), '@'))
        ampersand_file = str(count(posixpath.basename(dict_url['path']), '&'))
        exclamation_file = str(count(posixpath.basename(dict_url['path']), '!'))
        blank_file = str(count(posixpath.basename(dict_url['path']), ' '))
        til_file = str(count(posixpath.basename(dict_url['path']), '~'))
        comma_file = str(count(posixpath.basename(dict_url['path']), ','))
        plus_file = str(count(posixpath.basename(dict_url['path']), '+'))
        asterisk_file = str(count(posixpath.basename(dict_url['path']), '*'))
        hashtag_file = str(count(posixpath.basename(dict_url['path']), '#'))
        money_sign_file = str(count(posixpath.basename(dict_url['path']), '$'))
        percentage_file = str(count(posixpath.basename(dict_url['path']), '%'))
        len_file = str(length(posixpath.basename(dict_url['path'])))
        extension = str(extract_extension(posixpath.basename(dict_url['url'])))
    else:
        dot_file = -1
        hyphe_file = -1
        underline_file = -1
        bar_file = -1
        question_file = -1
        equal_file = -1
        arroba_file = -1
        ampersand_file = -1
        exclamation_file = -1
        blank_file = -1
        til_file = -1
        comma_file = -1
        plus_file = -1
        asterisk_file = -1
        hashtag_file = -1
        money_sign_file = -1
        percentage_file = -1
        len_file = -1
        extension = -1
    if dict_url['query']:
        dot_params = str(count(dict_url['query'], '.'))
        hyphe_params = str(count(dict_url['query'], '-'))
        underline_params = str(count(dict_url['query'], '_'))
        bar_params = str(count(dict_url['query'], '/'))
        question_params = str(count(dict_url['query'], '?'))
        equal_params = str(count(dict_url['query'], '='))
        arroba_params = str(count(dict_url['query'], '@'))
        ampersand_params = str(count(dict_url['query'], '&'))
        exclamation_params = str(count(dict_url['query'], '!'))
        blank_params = str(count(dict_url['query'], ' '))
        til_params = str(count(dict_url['query'], '~'))
        comma_params = str(count(dict_url['query'], ','))
        plus_params = str(count(dict_url['query'], '+'))
        asterisk_params = str(count(dict_url['query'], '*'))
        hashtag_params = str(count(dict_url['query'], '#'))
        money_sign_params = str(count(dict_url['query'], '$'))
        percentage_params = str(count(dict_url['query'], '%'))
        len_params = str(length(dict_url['query']))
        tld_params = str(check_tld(dict_url['query']))
        number_params = str(count_params(dict_url['query']))
    else:
        dot_params = -1
        hyphe_params = -1
        underline_params = -1
        bar_params = -1
        question_params = -1
        equal_params = -1
        arroba_params = -1
        ampersand_params = -1
        exclamation_params = -1
        blank_params = -1
        til_params = -1
        comma_params = -1
        plus_params = -1
        asterisk_params = -1
        hashtag_params = -1
        money_sign_params = -1
        percentage_params = -1
        len_params = -1
        tld_params = -1
        number_params = -1


    _lexical = [ dot_url, hyphe_url, underline_url, bar_url, question_url,
                        equal_url, arroba_url, ampersand_url, exclamation_url, blank_url, 
                        til_url, comma_url, plus_url, asterisk_url, hashtag_url,
                        money_sign_url, percentage_url, count_tld_url, len_url, count_alpha_url,
                        timeresponse_url, time_domain_activation_url, time_domain_expiration_url, Hasshortner_URL, dot_host,
                        hyphe_host, underline_host, bar_host, question_host, equal_host,
                        arroba_host, ampersand_host, exclamation_host, blank_host, til_host,
                        comma_host, plus_host, asterisk_host, hashtag_host, money_sign_host,
                        percentage_host, vowels_host, len_host, ip_exist, server_client,
                        dot_path, hyphe_path, underline_path, bar_path, question_path,
                        equal_path, arroba_path, ampersand_path, exclamation_path,   blank_path, 
                        til_path, comma_path, plus_path, asterisk_path,  hashtag_path, 
                        money_sign_path, percentage_path, len_path, dot_file,      hyphe_file,
                        underline_file, bar_file, question_file, equal_file, arroba_file,
                        ampersand_file, exclamation_file, blank_file, til_file, comma_file,
                        plus_file, asterisk_file, hashtag_file, money_sign_file, percentage_file, 
                        len_file, dot_params, hyphe_params, underline_params, bar_params, 
                        question_params,equal_params, arroba_params, ampersand_params, exclamation_params,
                        blank_params, til_params, comma_params, plus_params, asterisk_params,
                        hashtag_params, money_sign_params, percentage_params, len_params, number_params, email_exist]
                
    return _lexical
from urllib import parse
import re
import ipaddress
import posixpath
import csv
from datetime import datetime
import requests
from urllib.parse import urlparse, parse_qs
import whois
from datetime import datetime
import requests
#from googlesearch import search
#import ssl
#import socket
#import dns.resolver

def attributes():
    """Output file attributes."""
    lexical = [
    'dot_url', 'hyphe_url', 'underline_url', 'bar_url', 'question_url',
    'equal_url', 'arroba_url', 'ampersand_url', 'exclamation_url',
    'blank_url', 'til_url', 'comma_url', 'plus_url', 'asterisk_url', 'hashtag_url',
    'money_sign_url', 'percentage_url', 'count_tld_url', 'len_url', 'alpha_url', 'timeresponse_url',
    'time_domain_activation_url', 'time_domain_expiration_url', 'Hasshortner_URL',
    'dot_host','hyphe_host', 'underline_host', 'bar_host', 'question_host', 'equal_host',
    'arroba_host', 'ampersand_host', 'exclamation_host', 'blank_host', 'til_host',
    'comma_host', 'plus_host', 'asterisk_host', 'hashtag_host', 'money_sign_host',
    'percentage_host', 'vowels_host', 'len_host', 'ip_exist', 'server_client',
    'dot_path', 'hyphe_path', 'underline_path', 'bar_path', 'question_path',
    'equal_path', 'arroba_path', 'ampersand_path', 'exclamation_path',
    'blank_path', 'til_path', 'comma_path', 'plus_path', 'asterisk_path',
    'hashtag_path', 'money_sign_path', 'percentage_path', 'len_path', 'dot_file',
    'hyphe_file', 'underline_file', 'bar_file', 'question_file', 'equal_file',
    'arroba_file', 'ampersand_file', 'exclamation_file', 'blank_file',
    'til_file', 'comma_file', 'plus_file', 'asterisk_file', 'hashtag_file',
    'money_sign_file', 'percentage_file', 'len_file', 'dot_params',
    'hyphe_params', 'underline_params', 'bar_params', 'question_params',
    'equal_params', 'arroba_params', 'ampersand_params', 'exclamation_params',
    'blank_params', 'til_params', 'comma_params', 'plus_params', 'asterisk_params',
    'hashtag_params', 'money_sign_params', 'percentage_params', 'len_params',
    'tld_params', 'number_params', 'email_exist', 'extension'
        ]


    list_attributes = []
    list_attributes.extend(lexical)

    return list_attributes





shortening_services = (
    r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|"
    r"yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|"
    r"short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|"
    r"doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|db\.tt|"
    r"qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|is\.gd|"
    r"po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|"
    r"prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|"
    r"tr\.im|link\.zip\.net|"
    r"0rz\.tw|1-url\.net|126\.am|1tk\.us|1un\.fr|1url\.com|1url\.cz|1wb2\.net|2\.gp|2\.ht|"
    r"2ad\.in|2doc\.net|2fear\.com|2tu\.us|2ty\.in|2u\.xf\.cz|3ra\.be|3x\.si|4i\.ae|4ks\.net|"
    r"4view\.me|5em\.cz|5url\.net|5z8\.info|6fr\.ru|6g6\.eu|7\.ly|76\.gd|77\.ai|7fth\.cc|"
    r"7li\.in|7vd\.cn|8u\.cz|944\.la|98\.to|L9\.fr|Lvvk\.com|To8\.cc|a0\.fr|abbr\.sk|ad-med\.cz|"
    r"ad5\.eu|ad7\.biz|adb\.ug|adf\.ly|adfa\.st|adfly\.fr|adli\.pw|adv\.li|ajn\.me|aka\.gr|"
    r"alil\.in|amzn\.to|any\.gs|aqva\.pl|ares\.tl|asso\.in|au\.ms|ayt\.fr|azali\.fr|b00\.fr|"
    r"b23\.ru|b54\.in|baid\.us|bc\.vc|beam\.to|bee4\.biz|bim\.im|bit\.do|bit\.ly|bitly\.com|"
    r"bitw\.in|blap\.net|ble\.pl|blip\.tv|boi\.re|bote\.me|bougn\.at|br4\.in|brk\.to|brzu\.net|"
    r"bul\.lu|bxl\.me|bzh\.me|cachor\.ro|captur\.in|cashfly\.com|cbs\.so|cbug\.cc|cc\.cc|ccj\.im|"
    r"cf\.ly|cf2\.me|cf6\.co|chilp\.it|cjb\.net|cli\.gs|clikk\.in|clk\.im|cn86\.org|couic\.fr|"
    r"cr\.tl|cudder\.it|cur\.lv|curl\.im|curte\.me|cut\.pe|cut\.sk|cutt\.eu|cutt\.us|cutu\.me|"
    r"cybr\.fr|cyonix\.to|d75\.eu|daa\.pl|dai\.ly|decenturl\.com|dd\.ma|ddp\.net|dft\.ba|"
    r"digbig\.com|doiop\.com|dolp\.cc|dopice\.sk|droid\.ws|dv\.gd|dyo\.gs|e37\.eu|easyurl\.net|"
    r"ecra\.se|ely\.re|encurtador\.com\.br|erax\.cz|erw\.cz|esy\.es|ex9\.co|ezurl\.cc|fff\.re|"
    r"fff\.to|fff\.wf|filz\.fr|fnk\.es|foe\.hn|folu\.me|freze\.it|fur\.ly|fwdurl\.net|g00\.me|"
    r"gca\.sh|gg\.gg|goo\.gl|goo\.lu|grem\.io|guiama\.is|hadej\.co|hide\.my|hjkl\.fr|hops\.me|"
    r"href\.li|ht\.ly|i-2\.co|i99\.cz|icit\.fr|ick\.li|icks\.ro|iiiii\.in|iky\.fr|ilix\.in|"
    r"info\.ms|is\.gd|isra\.li|itm\.im|ity\.im|ix\.sk|j\.gs|j\.mp|jdem\.cz|jieb\.be|jp22\.net|"
    r"jqw\.de|kask\.us|kd2\.org|kfd\.pl|korta\.nu|kr3w\.de|krat\.si|kratsi\.cz|krod\.cz|kuc\.cz|"
    r"kxb\.me|l-k\.be|lc-s\.co|lc\.cx|lcut\.in|letop10\.|libero\.it|lick\.my|lien\.li|lien\.pl|"
    r"lin\.io|linkn\.co|linkbucks\.com|llu\.ch|lnk\.co|lnk\.ly|lnk\.sk|lnks\.fr|lnky\.fr|lnp\.sn|"
    r"lp25\.fr|m1p\.fr|m3mi\.com|make\.my|mcaf\.ee|mdl29\.net|mic\.fr|migre\.me|minu\.me|moour"
)


"""
def start_url(url):
    #Split URL into: protocol, host, path, params, query and fragment.
    if not parse.urlparse(url.strip()).scheme:
        url = 'http://' + url
    protocol, host, path, params, query, fragment = parse.urlparse(url.strip())

    result = {
        'url': url,
        'protocol': protocol,
        'host': host,
        'path': path,
        'params': params,
        'query': query,
        'fragment': fragment
    }
    return result
"""

def start_url(url):
    """Split URL into: protocol, host, path, params, query and fragment."""
    if not urlparse(url.strip()).scheme:
        url = 'http://' + url
    parsed_url = urlparse(url.strip())

    result = {
        'url': url,
        'protocol': parsed_url.scheme,
        'host': parsed_url.netloc,
        'path': parsed_url.path,
        'params': parsed_url.params,
        'query': parsed_url.query,
        'fragment': parsed_url.fragment
    }
    return result



def EnglishLetterCount(str):
    count = 0
    engletter = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    for num in str:
        if num in engletter:
            count = count + 1

    return count

def count(text, character):
    """Return the amount of certain character in the text."""
    return text.count(character)

def count_vowels(text):
    """Return the number of vowels."""
    vowels = ['a', 'e', 'i', 'o', 'u']
    count = 0
    for i in vowels:
        count += text.lower().count(i)
    return count

def length(text):
    """Return the length of a string."""
    return len(text)

def valid_ip(host):
    """Return if the domain has a valid IP format (IPv4 or IPv6)."""
    try:
        ipaddress.ip_address(host)
        return True
    except Exception:
        return False


def valid_email(text):
    """Return if there is an email in the text."""
    if re.findall(r'[\w\.-]+@[\w\.-]+', text):
        return True
    else:
        return False

def read_file(archive):
    """Read the file with the URLs."""
    with open(archive, 'r') as f:
        urls = ([line.rstrip() for line in f])
        return urls

def check_word_server_client(text):
    """Return whether the "server" or "client" keywords exist in the domain."""
    if "server" in text.lower() or "client" in text.lower():
        return True
    return False

def count_tld(text):
    """Return amount of Top-Level Domains (TLD) present in the URL."""
    file_path = os.path.join(os.path.dirname(__file__), 'files', 'tlds.txt')
    file = open(file_path, 'r')
    count = 0
    pattern = re.compile("[a-zA-Z0-9.]")
    for line in file:
        i = (text.lower().strip()).find(line.strip())
        while i > -1:
            if ((i + len(line) - 1) >= len(text)) or not pattern.match(text[i + len(line) - 1]):
                count += 1
            i = text.find(line.strip(), i + 1)
    file.close()
    return count

def extract_extension(text):
    """Return file extension name."""
    file_path = os.path.join(os.path.dirname(__file__), 'files', 'extensions.txt')
    file = open(file_path, 'r')

    pattern = re.compile("[a-zA-Z0-9.]")
    for extension in file:
        i = (text.lower().strip()).find(extension.strip())
        while i > -1:
            if ((i + len(extension) - 1) >= len(text)) or not pattern.match(text[i + len(extension) - 1]):
                file.close()
                return extension.rstrip().split('.')[-1]
            i = text.find(extension.strip(), i + 1)
    file.close()
    return '?'

def check_tld(text):
    """Check for presence of Top-Level Domains (TLD)."""
    file_path = os.path.join(os.path.dirname(__file__), 'files', 'tlds.txt')
    file = open(file_path, 'r')
    pattern = re.compile("[a-zA-Z0-9.]")
    for line in file:
        i = (text.lower().strip()).find(line.strip())
        while i > -1:
            if ((i + len(line) - 1) >= len(text)) or not pattern.match(text[i + len(line) - 1]):
                file.close()
                return True
            i = text.find(line.strip(), i + 1)
    file.close()
    return False

def count_params(text):
    """Return number of parameters."""
    return len(parse.parse_qs(text))
    

def read_csv_file(archive):
    """Read a CSV file and return its contents."""
    data = []
    with open(archive, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row)
    return data


def check_time_response(domain, timeout=3):
    """Return the response time in seconds."""
    try:
        response = requests.get(domain, headers={'Cache-Control': 'no-cache'}, timeout=timeout)
        latency = response.elapsed.total_seconds()
        return latency
    except requests.exceptions.Timeout:
        return '>3'  # Return 'l' if the request times out
    except requests.exceptions.RequestException:
        return '?'  # Return '?' if an error occurs


def time_domain_activation(url):
    """Get the domain activation time (creation date) in days for a given URL."""
    try:
        # Parse the URL to extract the domain
        domain = url.split('/')[2]  # Extract domain from URL (assuming URL is in valid format)

        # Fetch WHOIS information for the domain
        domain_info = whois.whois(domain)

        if domain_info.creation_date:
            # Get the domain creation date
            creation_date = domain_info.creation_date

            if isinstance(creation_date, list):
                # Use the first creation date if multiple dates are returned (common for some domains)
                creation_date = creation_date[0]

            # Calculate the number of days since the domain was created
            current_date = datetime.now()
            activation_time_days = (current_date - creation_date).days

            return activation_time_days
        else:
            #print(f"Failed to retrieve creation date for the domain: {domain}")
            return '?'

    except Exception as e:
        #print(f"Error occurred while fetching domain activation time: {e}")
        return '?'


def time_domain_expiration(url):
    """Get the domain expiration time (expiration date) in days for a given URL."""
    try:
        # Parse the URL to extract the domain
        domain = url.split('/')[2]  # Extract domain from URL (assuming URL is in valid format)

        # Fetch WHOIS information for the domain
        domain_info = whois.whois(domain)

        if domain_info.expiration_date:
            # Get the domain expiration date
            expiration_date = domain_info.expiration_date

            if isinstance(expiration_date, list):
                # Use the first expiration date if multiple dates are returned (common for some domains)
                expiration_date = expiration_date[0]

            # Calculate the number of days until the domain expires
            current_date = datetime.now()
            time_until_expiration_days = (expiration_date - current_date).days

            return time_until_expiration_days
        else:
            print(f"Failed to retrieve expiration date for the domain: {domain}")
            return '?'

    except Exception as e:
        print(f"Error occurred while fetching domain expiration time: {e}")
        return '?'


def qty_redirects(url):
    """Check if a URL is redirected."""
    try:
        # Send an HTTP HEAD request to the URL
        response = requests.head(url, allow_redirects=True)

        # Check if the response has a redirect status code
        if response.status_code in (301, 302):
            return True  # URL is redirected
        else:
            return False  # URL is not redirected

    except requests.RequestException as e:
        print(f"Error occurred while checking URL redirection: {e}")
        return None


def shortner_URL(url):
    match = re.search(shortening_services, url)
    if match:
        return True
    else:
        return False


def main(url):
    #with open(dataset, "w") as output:
        #writer = csv.writer(output)
        #writer.writerow(attributes())
        #count_url = 0
        #for url in read_file(urls):
        #    count_url = count_url + 1
            dict_url = start_url(url)

            """LEXICAL"""
            # URL
            dot_url = str(count(dict_url['url'],'.'))
            hyphe_url = str(count(dict_url['url'],'-'))
            underline_url = str(count(dict_url['url'],'_'))
            bar_url = str(count(dict_url['url'],'/'))
            question_url = str(count(dict_url['url'],'?'))
            equal_url = str(count(dict_url['url'],'='))
            arroba_url = str(count(dict_url['url'],'@'))
            ampersand_url = str(count(dict_url['url'],'&'))
            exclamation_url = str(count(dict_url['url'], '!'))
            blank_url = str(count(dict_url['url'], ' '))
            til_url = str(count(dict_url['url'], '~'))
            comma_url = str(count(dict_url['url'], ','))
            plus_url = str(count(dict_url['url'], '+'))
            asterisk_url = str(count(dict_url['url'], '*'))
            hashtag_url = str(count(dict_url['url'], '#'))
            money_sign_url = str(count(dict_url['url'], '$'))
            percentage_url = str(count(dict_url['url'], '%'))
            len_url = str(length(dict_url['url']))
            email_exist = str(valid_email(dict_url['url']))
            count_tld_url = str(count_tld(dict_url['url']))
            count_alpha_url=str(EnglishLetterCount(dict_url['url']))
            timeresponse_url=str(check_time_response(dict_url['url']))
            time_domain_activation_url=str(time_domain_activation(dict_url['url']))
            time_domain_expiration_url=str(time_domain_expiration(dict_url['url']))
            Hasshortner_URL=str(shortner_URL(dict_url['url']))
             # DOMAIN
            dot_host = str(count(dict_url['host'], '.'))
            hyphe_host = str(count(dict_url['host'], '-'))
            underline_host = str(count(dict_url['host'], '_'))
            bar_host = str(count(dict_url['host'], '/'))
            question_host = str(count(dict_url['host'], '?'))
            equal_host = str(count(dict_url['host'], '='))
            arroba_host = str(count(dict_url['host'], '@'))
            ampersand_host = str(count(dict_url['host'], '&'))
            exclamation_host = str(count(dict_url['host'], '!'))
            blank_host = str(count(dict_url['host'], ' '))
            til_host = str(count(dict_url['host'], '~'))
            comma_host = str(count(dict_url['host'], ','))
            plus_host = str(count(dict_url['host'], '+'))
            asterisk_host = str(count(dict_url['host'], '*'))
            hashtag_host = str(count(dict_url['host'], '#'))
            money_sign_host = str(count(dict_url['host'], '$'))
            percentage_host = str(count(dict_url['host'], '%'))
            vowels_host = str(count_vowels(dict_url['host']))
            len_host = str(length(dict_url['host']))
            ip_exist = str(valid_ip(dict_url['host']))
            server_client = str(check_word_server_client(dict_url['host']))
             # DIRECTORY
            if dict_url['path']:
                dot_path = str(count(dict_url['path'], '.'))
                hyphe_path = str(count(dict_url['path'], '-'))
                underline_path = str(count(dict_url['path'], '_'))
                bar_path = str(count(dict_url['path'], '/'))
                question_path = str(count(dict_url['path'], '?'))
                equal_path = str(count(dict_url['path'], '='))
                arroba_path = str(count(dict_url['path'], '@'))
                ampersand_path = str(count(dict_url['path'], '&'))
                exclamation_path = str(count(dict_url['path'], '!'))
                blank_path = str(count(dict_url['path'], ' '))
                til_path = str(count(dict_url['path'], '~'))
                comma_path = str(count(dict_url['path'], ','))
                plus_path = str(count(dict_url['path'], '+'))
                asterisk_path = str(count(dict_url['path'], '*'))
                hashtag_path = str(count(dict_url['path'], '#'))
                money_sign_path = str(count(dict_url['path'], '$'))
                percentage_path = str(count(dict_url['path'], '%'))
                len_path = str(length(dict_url['path']))
            else:
                dot_path = '?'
                hyphe_path = '?'
                underline_path = '?'
                bar_path = '?'
                question_path = '?'
                equal_path = '?'
                arroba_path = '?'
                ampersand_path = '?'
                exclamation_path = '?'
                blank_path = '?'
                til_path = '?'
                comma_path = '?'
                plus_path = '?'
                asterisk_path = '?'
                hashtag_path = '?'
                money_sign_path = '?'
                percentage_path = '?'
                len_path = '?'
            # FILE
            if dict_url['path']:
                dot_file = str(count(posixpath.basename(dict_url['path']), '.'))
                hyphe_file = str(count(posixpath.basename(dict_url['path']), '-'))
                underline_file = str(count(posixpath.basename(dict_url['path']), '_'))
                bar_file = str(count(posixpath.basename(dict_url['path']), '/'))
                question_file = str(count(posixpath.basename(dict_url['path']), '?'))
                equal_file = str(count(posixpath.basename(dict_url['path']), '='))
                arroba_file = str(count(posixpath.basename(dict_url['path']), '@'))
                ampersand_file = str(count(posixpath.basename(dict_url['path']), '&'))
                exclamation_file = str(count(posixpath.basename(dict_url['path']), '!'))
                blank_file = str(count(posixpath.basename(dict_url['path']), ' '))
                til_file = str(count(posixpath.basename(dict_url['path']), '~'))
                comma_file = str(count(posixpath.basename(dict_url['path']), ','))
                plus_file = str(count(posixpath.basename(dict_url['path']), '+'))
                asterisk_file = str(count(posixpath.basename(dict_url['path']), '*'))
                hashtag_file = str(count(posixpath.basename(dict_url['path']), '#'))
                money_sign_file = str(count(posixpath.basename(dict_url['path']), '$'))
                percentage_file = str(count(posixpath.basename(dict_url['path']), '%'))
                len_file = str(length(posixpath.basename(dict_url['path'])))
                extension = str(extract_extension(posixpath.basename(dict_url['url'])))
            else:
                dot_file = '?'
                hyphe_file = '?'
                underline_file = '?'
                bar_file = '?'
                question_file = '?'
                equal_file = '?'
                arroba_file = '?'
                ampersand_file = '?'
                exclamation_file = '?'
                blank_file = '?'
                til_file = '?'
                comma_file = '?'
                plus_file = '?'
                asterisk_file = '?'
                hashtag_file = '?'
                money_sign_file = '?'
                percentage_file = '?'
                len_file = '?'
                extension = '?'
            # PARAMETERS
            if dict_url['query']:
                dot_params = str(count(dict_url['query'], '.'))
                hyphe_params = str(count(dict_url['query'], '-'))
                underline_params = str(count(dict_url['query'], '_'))
                bar_params = str(count(dict_url['query'], '/'))
                question_params = str(count(dict_url['query'], '?'))
                equal_params = str(count(dict_url['query'], '='))
                arroba_params = str(count(dict_url['query'], '@'))
                ampersand_params = str(count(dict_url['query'], '&'))
                exclamation_params = str(count(dict_url['query'], '!'))
                blank_params = str(count(dict_url['query'], ' '))
                til_params = str(count(dict_url['query'], '~'))
                comma_params = str(count(dict_url['query'], ','))
                plus_params = str(count(dict_url['query'], '+'))
                asterisk_params = str(count(dict_url['query'], '*'))
                hashtag_params = str(count(dict_url['query'], '#'))
                money_sign_params = str(count(dict_url['query'], '$'))
                percentage_params = str(count(dict_url['query'], '%'))
                len_params = str(length(dict_url['query']))
                tld_params = str(check_tld(dict_url['query']))
                number_params = str(count_params(dict_url['query']))
            else:
                dot_params = '?'
                hyphe_params = '?'
                underline_params = '?'
                bar_params = '?'
                question_params = '?'
                equal_params = '?'
                arroba_params = '?'
                ampersand_params = '?'
                exclamation_params = '?'
                blank_params = '?'
                til_params = '?'
                comma_params = '?'
                plus_params = '?'
                asterisk_params = '?'
                hashtag_params = '?'
                money_sign_params = '?'
                percentage_params = '?'
                len_params = '?'
                tld_params = '?'
                number_params = '?'



            _lexical = [
            dot_url, hyphe_url, underline_url, bar_url, question_url,
            equal_url, arroba_url, ampersand_url, exclamation_url,
            blank_url, til_url, comma_url, plus_url, asterisk_url, hashtag_url,
            money_sign_url, percentage_url, count_tld_url, len_url,count_alpha_url,timeresponse_url,time_domain_activation_url,time_domain_expiration_url,Hasshortner_URL,dot_host,
            hyphe_host, underline_host, bar_host, question_host, equal_host,
            arroba_host, ampersand_host, exclamation_host, blank_host, til_host,
            comma_host, plus_host, asterisk_host, hashtag_host, money_sign_host,
            percentage_host, vowels_host, len_host, ip_exist, server_client,
            dot_path, hyphe_path, underline_path, bar_path, question_path,
            equal_path, arroba_path, ampersand_path, exclamation_path,
            blank_path, til_path, comma_path, plus_path, asterisk_path,
            hashtag_path, money_sign_path, percentage_path, len_path, dot_file,
            hyphe_file, underline_file, bar_file, question_file, equal_file,
            arroba_file, ampersand_file, exclamation_file, blank_file,
            til_file, comma_file, plus_file, asterisk_file, hashtag_file,
            money_sign_file, percentage_file, len_file, dot_params,
            hyphe_params, underline_params, bar_params, question_params,
            equal_params, arroba_params, ampersand_params, exclamation_params,
            blank_params, til_params, comma_params, plus_params, asterisk_params,
            hashtag_params, money_sign_params, percentage_params, len_params, number_params, email_exist
            ]
                
            return _lexical

