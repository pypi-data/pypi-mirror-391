#by hso
import requests
import uuid
import time
import random
import base64
import hashlib
import secrets
from random import choice,randint,randrange
import string,json
import user_agent
import re
from os import urandom
import binascii
from urllib.parse import urlencode
from MedoSigner import Argus, Gorgon, Ladon, md5
from requests import get,post
class GMAIL:
    @staticmethod
    def CheckEmail(email):
        if '@' in email:email=email.split('@')[0]
        if '..' in email or '_' in email or len(email) < 5 or len(email) > 30:
            return {"data":{"status":False,"email":email,"error_code":1,"programmer":"@ii33cc"}}
        try:
            name = ''.join(choice('abcdefghijklmnopqrstuvwxyz') for i in range(randrange(5,10)))
            birthday = randrange(1980,2010),randrange(1,12),randrange(1,28)
            s = requests.Session()
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'referer': 'https://accounts.google.com/',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
                'x-browser-channel': 'stable',
                'x-browser-copyright': 'Copyright 2024 Google LLC. All rights reserved.',
                'x-browser-year': '2024',
            }

            params = {
                'biz': 'false',
                'continue': 'https://mail.google.com/mail/u/0/',
                'ddm': '1',
                'emr': '1',
                'flowEntry': 'SignUp',
                'flowName': 'GlifWebSignIn',
                'followup': 'https://mail.google.com/mail/u/0/',
                'osid': '1',
                'service': 'mail',
            }

            r = s.get('https://accounts.google.com/lifecycle/flows/signup', params=params, headers=headers)
            tl=r.url.split('TL=')[1]
            s1= r.text.split('"Qzxixc":"')[1].split('"')[0]
            at = r.text.split('"SNlM0e":"')[1].split('"')[0]
            headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'origin': 'https://accounts.google.com',
                'referer': 'https://accounts.google.com/',
                'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
                'x-goog-ext-278367001-jspb': '["GlifWebSignIn"]',
                'x-goog-ext-391502476-jspb': '["'+s1+'"]',
                'x-same-domain': '1',
            }

            params = {
                'rpcids': 'E815hb',
                'source-path': '/lifecycle/steps/signup/name',
                'hl': 'en-US',
                'TL': tl,
                'rt': 'c',
            }

            data = 'f.req=%5B%5B%5B%22E815hb%22%2C%22%5B%5C%22{}%5C%22%2C%5C%22%5C%22%2Cnull%2Cnull%2Cnull%2C%5B%5D%2C%5B%5C%22https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F%5C%22%2C%5C%22mail%5C%22%5D%2C1%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&at={}&'.format(name,at)

            r = s.post(
            'https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute',
            params=params,
            headers=headers,
            data=data,
            ).text



            headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'origin': 'https://accounts.google.com',
                'referer': 'https://accounts.google.com/',
                'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
                'x-goog-ext-278367001-jspb': '["GlifWebSignIn"]',
                'x-goog-ext-391502476-jspb': '["'+s1+'"]',
                'x-same-domain': '1',
            }

            params = {
                'rpcids': 'eOY7Bb',
                'source-path': '/lifecycle/steps/signup/birthdaygender',
                'hl': 'en-US',
                'TL': tl,
                'rt': 'c',
            }
            data = 'f.req=%5B%5B%5B%22eOY7Bb%22%2C%22%5B%5B{}%2C{}%2C{}%5D%2C1%2Cnull%2Cnull%2Cnull%2C%5C%22%3Cf7Nqs-sCAAZfiOnPf4iN_32KOpLfQKL0ADQBEArZ1IBDTUyai2FYax3ViMI2wqBpWShhe-OPRhpMjnm9s14Yu65MknXEBWcyTyF3Jx0pzQAAAeGdAAAAC6cBB7EATZAxrowFF7vQ68oKqx7_sdcR_u8t8CJys-8G4opCIVySwUYaUnm-BovA8aThYLISPNMc8Pl3_B0GnkQJ_W4SIed6l6EcM7QLJ8AXVNAaVgbhsnD7q4lyQnlvR14HRW10oP85EU_bwG1E4QJH1V0KnVS4mIeoqB7zHOuxMuGifv6MB3GghUGTewh0tMN1jaf8yvX804tntlrlxm3OZgCZ2UxgDjUVOKFMv1Y3Txr16jJEJ56-T7qrPCtt6H1kmUvCIl_RDZzbt_sj5OLnbX1UvVA-VgG8-X9AJdvGhCKVhkf3iSkjy6_ZKsZSbsOsMjrm7ggnLdMStIf4AzbJIyMC7q4JMCaDaW_UI9SgquR8mHMpHGRmP7zY-WE47l7uRSpkI6oV93XJZ1zskJsxaDz7sDYHpzEL1RGPnkZU45XkIkwuc1ptU_AiM6SQyoZK7wFnhYxYfDQjSwaC7lOfngr6F2e4pDWkiC96QY4xLr6m2oUoDbyKR3ykccKEECEakFKzS-wSxIt9hK6nw-a9PEpVzhf6uIywZofNCs0KJOhhtv_ReG24DOC6NHX-FweCOkiYtT2sISrm6H8Wr4E89oU_mMWtpnXmhs8PB28SXw42-EdhRPsdcQkgKycOVT_IXwCc4Td9-t7715HP-L2XLk5i05aUrk-sHPPEz8SyL3odOb1SkwQ69bRQHfbPZr858iTDD0UaYWE_Jmb4wlGxYOSsvQ3EIljWDtj69cq3slKqMQu0ZC9bdqEh0p_T9zvsVwFiZThf19JL8PtqlXH5bgoEnPqdSfYbnJviQdUTAhuBPE-O8wgmdwl22wqkndacytncjwGR9cuXqAXUk_PbS-0fJGxIwI6-b7bhD7tS2DUAJk708UK5zFDLyqN6hFtj8AAjNM-XGIEqgTavCRhPnVT0u0l7p3iwtwKmRyAn42m3SwWhOQ6LDv-K2DyLl2OKfFu9Y-fPBh-2K2hIn2tKoGMgVbBR8AsVsYL7L6Bh5JIW7LCHaXNk3oDyHDx5QFaPtMmnIxcfFG90YSEPIgWV2nb67zDDacvvCkiPEQMXHJUcz1tuivaAgCTgW68wNYkUt89KJDhJTSWY2jcPsDIyCnS-SGESyR7mvbkvC3Robo0zVQm6q3Z73si9uqJiPmUGgBLycxUq2A_L3B-Hz35vBm5Oc5Hbe8hJToB03ilQzLa8Kld5BY8_kmmh6kfrOvi07uwfusHv3mKfijE2vaK3v2O2He41hCaOv3ExSfdPKb2V5nPPTw8ryyC5ZwlM_DLCU_k5xONsh4uplpRmydmJcit4aj5Ig0qLVF9MxIWU5xoDlvhKL9jHh-HVgIe-CPp4RMM5BfTxDgtESiF97RWjwrNeKn6Fc4311AdCrfZMcZ0F2JnQsfKAz4H-hoWbrOEVBkPcBt5umJ_iaCm0cQ2XTQMjzAtfWbRe6EGSxbkK-DXBl4EQM-6cnH1139MIHLzNou_Tltbl2HaomCS044CwhRNpe95KuYhM4Fz0Z_8rRjqy48tS_L4kQMX1CtxjBNfd4eUoaAIwAcz3LaL5BwL0DAYcV3xruTTuy6X8zFHe8fAIB9pJ_Pw0YJm3Ye28_tTg5xk0R4EU7_IPIHk6RrtSsG0Rfst3Qi5NRfWFg5h9LlmlHO_EUhdw1wbCICTqbS2A94aIBSCQzn7RmqOTTSIXwgFwnSBRKvoo0v9tKQ2rnMZsXRhzQgxwfmYOq29EUbuHmmWQjpRhfzX1Z6-5gXRPr4-PjrInsTiAi36xDyc8a1yTAhKMwnvf3GNqcK8lqx80VCASvcpYxGIAFl4QghroZbIJXlhccCWVF_xrzsw83QUdoZ5ExWi5f_cLvEXeZssdtan1orOaPJuWXT_0ryzpS9fOGtT68pL4HMAPLPpfwhiZ-wtZQU0oVy6T2L6oP1SIHQDU_QDaMR0MkStXNDj69r5cTDdYZiIbFkvWYeL1afTEljx1i2n2KKnDmpJfx2HeGCSZBMKZey24z_LDLA7MyJ2VBo4Zvmm23dwhWHOly56w9ul4sWzpHqgsqmKynRoaq9SXKrrmbR3f2GKBHSvy3Jm0Ln52zwIQfFSXpOjGXq5pkOXlvQc6MPuV3zADVmcUZs6ywI-ER3PkAaA-f-zG-ke_6jvOzGp6WF8UxnIk5tq3tus_R5pUjVQFjk6qZtWOP8VZd1TeJ54Oo_ywj8YAYCphkDtFYRMZSubmnI-F9LLlAfOiDwQ7r-iNvp8psduy9xrWdIpE_l23Y_qYJPHwvtopL3lB7juqEiFkhUts7NEugyWY-m6-9oEgsOY0lM4746V-XUxSeS7UkZkQZZM19g7GkWjJ61D98i0m2u_UYLnyDFQEaIxVhFcmS1Zq7OMsKm_gYpMt4LuD1F3N__Vj05QNyI59QNQADODveiHpfVva9Cd2AzBm9AKGwU4xDS_FyX3XRsRbfQFtqNzPf1LAERHlnHFn%5C%22%2C%5Bnull%2Cnull%2C%5C%22https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F%5C%22%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5C%22mail%5C%22%5D%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&at={}&'.format(birthday[0],birthday[1],birthday[2],at)
            r = s.post(
            'https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute',
            params=params,
            headers=headers,
            data=data,
            ).text
            headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'origin': 'https://accounts.google.com',
                'referer': 'https://accounts.google.com/',
                'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
                'x-goog-ext-278367001-jspb': '["GlifWebSignIn"]',
                'x-goog-ext-391502476-jspb': '["'+s1+'"]',
                'x-same-domain': '1',
            }
            params = {
                'rpcids': 'NHJMOd',
                'source-path': '/lifecycle/steps/signup/username',
                'hl': 'en-US',
                'TL': tl,
                'rt': 'c',
            }
            data = 'f.req=%5B%5B%5B%22NHJMOd%22%2C%22%5B%5C%22{}%5C%22%2C0%2C0%2Cnull%2C%5Bnull%2Cnull%2Cnull%2Cnull%2C1%2C152855%5D%2C0%2C40%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&at={}&'.format(email,at)
            r = s.post(
            'https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute',
            params=params,
            headers=headers,
            data=data,
            ).text
            if 'steps/signup/password'in r:
                return {"data":{"status":True,"email":email,"error_code":0,"programmer":"@ii33cc"}}
            else:
                return {"data":{"status":False,"email":email,"error_code":1,"programmer":"@ii33cc"}}
        except:""
class instagram:
    @staticmethod
    def CheckEmail(email):
        if ("@")not in email:return {"data":{"status":"fail","message":"Error Email.","programmer":"@ii33cc"}}
        rnd=str(randint(150, 999))
        user_agent = "Instagram 311.0.0.32.118 Android (" + ["23/6.0", "24/7.0", "25/7.1.1", "26/8.0", "27/8.1", "28/9.0"][randint(0, 5)] + "; " + str(randint(100, 1300)) + "dpi; " + str(randint(200, 2000)) + "x" + str(randint(200, 2000)) + "; " + ["SAMSUNG", "HUAWEI", "LGE/lge", "HTC", "ASUS", "ZTE", "ONEPLUS", "XIAOMI", "OPPO", "VIVO", "SONY", "REALME"][randint(0, 11)] + "; SM-T" + rnd + "; SM-T" + rnd + "; qcom; en_US; 545986"+str(randint(111,999))+")"   
        files=[
    ]
        headers = {
    }        
        try:
            response = requests.post('https://www.instagram.com/api/v1/web/accounts/login/ajax/', headers=headers,files=files)
        except Exception as e:
            return e
        try:
            device_id = f"android-{secrets.token_hex(8)}",
            csrf = hashlib.md5(str(time.time()).encode()).hexdigest()
            mid = response.cookies["mid"]
            ig_did = response.cookies["ig_did"]
            ig_nrcb = response.cookies["ig_nrcb"]
            app = ''.join(choice('1234567890')for i in range(15))
        except Exception as f:""
        choice_ = choice("143")
        if choice_ == "1":
                from user_agent import generate_user_agent
                aa=str(generate_user_agent())
                data = {        'signed_body':'ef02f559b04e8d7cbe15fb8cf18e2b48fb686dafd056b7c9298c08f3e2007d43.{"_csrftoken":"dG4dEIkWvAWpIj1B2M2mutWtdO1LiPCK","adid":"5e7df201-a1ff-45ec-8107-31b10944e25c","guid":"b0382b46-1663-43a7-ba90-3949c43fd808","device_id":"android-71a5d65f74b8fcbc","query":"'f'{email}''"}',

            'ig_sig_key_version':'4',
        }	
                headers = {
            'X-Pigeon-Session-Id':'2b712457-ffad-4dba-9241-29ea2f472ac5',
            'X-Pigeon-Rawclienttime':'1707104597.347',
            'X-IG-Connection-Speed':'-1kbps',
            'X-IG-Bandwidth-Speed-KBPS':'-1.000',
            'X-IG-Bandwidth-TotalBytes-B':'0',
            'X-IG-Bandwidth-TotalTime-MS':'0',
            'X-IG-VP9-Capable':'false',
            'X-Bloks-Version-Id':'009f03b18280bb343b0862d663f31ac80c5fb30dfae9e273e43c63f13a9f31c0',
            'X-IG-Connection-Type':'WIFI',
            'X-IG-Capabilities':'3brTvw==',
            'X-IG-App-ID':'567067343352427',
            'User-Agent':aa,
            'Accept-Language':'ar-IQ, en-US',
            'Cookie':'mid=Zbu4xQABAAE0k2Ok6rVxXpTD8PFQ; csrftoken=dG4dEIkWvAWpIj1B2M2mutWtdO1LiPCK',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept-Encoding':'gzip, deflate',
            'Host':'i.instagram.com',
            'X-FB-HTTP-Engine':'Liger',
            'Connection':'keep-alive',
            'Content-Length':'364',
        }
                try:
                    re = requests.post('https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/',headers=headers,data=data)
                    if ('"can_recover_with_code"')in re.text:
                        return {"data":{"status":True,"programmer":"@ii33cc"}}
                    elif "ip"in re.text:
                        return  {"data":{"status":"ip_block run vpn or use proxy","programmer":"@ii33cc"}}            	             
                    else:
                        return {"data":{"status":False,"programmer":"@ii33cc"}}
                except Exception as e:""    
        elif choice_ == "3":
                url = 'https://www.instagram.com/api/v1/web/accounts/check_email/'
                headers = {	
                'Host': 'www.instagram.com',
                'origin': 'https://www.instagram.com',
                'referer': 'https://www.instagram.com/accounts/signup/email/',	
                'sec-ch-ua-full-version-list': '"Android WebView";v="119.0.6045.163", "Chromium";v="119.0.6045.163", "Not?A_Brand";v="24.0.0.0"',
                'user-agent': str(user_agent)}
                data = {
            'email': str(email)
            }
                try:
                    response = requests.post(url,headers=headers,data=data)
                    if 'email_is_taken' in response.text:
                        return {"data":{"status":True,"programmer":"@ii33cc"}}
                    elif '"spam":true' in response.text:
                        return  {"data":{"status":"ip_block run vpn or use proxy","programmer":"@ii33cc"}}
                    else:
                        return {"data":{"status":False,"programmer":"@ii33cc"}}
                except Exception as e:
                    ""
        elif choice_ == "4":
                url='https://i.instagram.com/api/v1/accounts/create/'
                headers={
                'Host': 'i.instagram.com',
                'cookie': f'mid={mid}',
                'x-ig-capabilities': 'AQ==',
                'cookie2': '$Version=1',
                'x-ig-connection-type': 'WIFI',
                'user-agent': "Instagram 136.0.0.34.124 Android (24/7.0; 640dpi; 1440x2560; HUAWEI; LON-L29; HWLON; hi3660; en_US; 208061712)",
                'content-type': 'application/x-www-form-urlencoded',
                'content-length': '159'
                }
                data={
    'password':'Topython',
    'device_id':str(uuid.uuid4()),
    'guid':str(uuid.uuid4()),
    'email': str(email),
    'username':email,}
                try:
                    response = requests.post(url,headers=headers,data=data)
                    if "Another account is using the same email" in response.text:
                    
                        return {"data":{"status":True,"programmer":"@ii33cc"}}
                    elif "ip" in response.text:
                        return {"data":{"status":"ip_block run vpn or use proxy","programmer":"@ii33cc"}}
                    else:
                        return {"data":{"status":False,"programmer":"@ii33cc"}}
                except Exception as e:""

#"spam":true

    @staticmethod
    def generateUsername2011() -> str:
        data = {
            "lsd": ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
            "variables": json.dumps({"id": int(random.randrange(10000, 17699999)), "render_surface": "PROFILE"}),
            "doc_id": "25618261841150840"
        }
        try:
            response = requests.post(
                "https://www.instagram.com/api/graphql",
                headers={"X-FB-LSD": data["lsd"]},
                data=data
            )
            username = response.json().get('data', {}).get('user', {}).get('username')
            fol= response.json().get("data",{}).get("user",{}).get("follower_count")
            return {"data":{"message":"ok","username":username,"follower_count":fol,"programmer":"@ii33cc"}}
        except:
            return{"data":{"Errur":"try agin"}}
    @staticmethod
    def generateUsername2012() -> str:
        data = {
            "lsd": ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
            "variables": json.dumps({"id": int(random.randrange(17699999, 263014407)), "render_surface": "PROFILE"}),
            "doc_id": "25618261841150840"
        }
        try:
            response = requests.post(
                "https://www.instagram.com/api/graphql",
                headers={"X-FB-LSD": data["lsd"]},
                data=data
            )
            username = response.json().get('data', {}).get('user', {}).get('username')
            fol= response.json().get("data",{}).get("user",{}).get("follower_count")
            return {"data":{"message":"ok","username":username,"follower_count":fol,"programmer":"@ii33cc"}}
        except:
            return{"data":{"Errur":"try agin"}}
    @staticmethod
    def generateUsername2013() -> str:
        data = {
            "lsd": ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
            "variables": json.dumps({"id": int(random.randrange(263014407, 361365133)), "render_surface": "PROFILE"}),
            "doc_id": "25618261841150840"
        }
        try:
            response = requests.post(
                "https://www.instagram.com/api/graphql",
                headers={"X-FB-LSD": data["lsd"]},
                data=data
            )
            username = response.json().get('data', {}).get('user', {}).get('username')
            fol= response.json().get("data",{}).get("user",{}).get("follower_count")
            return {"data":{"message":"ok","username":username,"follower_count":fol,"programmer":"@ii33cc"}}
        except:
            return{"data":{"Errur":"try agin"}}
    @staticmethod
    def generateUsername() -> str:
        data = {
            "lsd": ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
            "variables": json.dumps({"id": int(random.randrange(361365133, 1629010000)), "render_surface": "PROFILE"}),
            "doc_id": "25618261841150840"
        }
        try:
            response = requests.post(
                "https://www.instagram.com/api/graphql",
                headers={"X-FB-LSD": data["lsd"]},
                data=data
            )
            username = response.json().get('data', {}).get('user', {}).get('username')
            fol= response.json().get("data",{}).get("user",{}).get("follower_count")
            return {"data":{"message":"ok","username":username,"follower_count":fol,"programmer":"@ii33cc"}}
        except:
            return{"data":{"Errur":"try agin"}}
    @staticmethod
    def generateUsername():
        g=random.choice(
            [
                'azertyuiopmlkjhgfdsqwxcvbn', 
                'azertyuiopmlkjhgfdsqwxcvbn',
                'azertyuiopmlkjhgfdsqwxcvbn',
                'azertyuiopmlkjhgfdsqwxcvbn',
                'azertyuiopmlkjhgfdsqwxcvbn',
                'abcdefghijklmnopqrstuvwxyzéèêëàâäôùûüîïç',  
                'abcdefghijklmnopqrstuvwxyzéèêëàâäôùûüîïç',
                'abcdefghijklmnopqrstuvwxyzéèêëàâäôùûüîïç',
                
'abcdefghijklmnopqrstuvwxyzéèêëàâäôùûüîïç',                'abcdefghijklmnopqrstuvwxyzñ',  
                'abcdefghijklmnopqrstuvwxyzñ',
                'abcdefghijklmnopqrstuvwxyzñ',
                'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',  
                'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
                'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
                '的一是不了人我在有他这为之大来以个中上们到说时国和地要就出会可也你对生能而子那得于着下自之',  
                '的一是不了人我在有他这为之大来以个中上们到说时国和地要就出会可也你对生能而子那得于着下自之',
                '的一是不了人我在有他这为之大来以个中上们到说时国和地要就出会可也你对生能而子那得于着下自之',
                'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン',  
                'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン',
                'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん', 
                'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん',
                'אבגדהוזחטיכלמנסעפצקרשת',
                'אבגדהוזחטיכלמנסעפצקרשת',
                'αβγδεζηθικλμνξοπρστυφχψω',  
                'αβγδεζηθικλμνξοπρστυφχψω',
                'abcdefghijklmnopqrstuvwxyzç', 
                'abcdefghijklmnopqrstuvwxyzç',
                'กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤฤลฦวศษสหฬอฮ',  
                'กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤฤลฦวศษสหฬอฮ',
                'अआइईउऊऋएऐओऔअंअःकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहक्षत्रज्ञ',  
                'अआइईउऊऋएऐओऔअंअःकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहक्षत्रज्ञ',
            ]

        )
        keyword=''.join((random.choice(g) for i in range(random.randrange(4,9))))
        cookies = {
            'rur': '"LDC\\05467838469205\\0541758153066:01f72be7578ed09a57bfe3e41c19af58848e0e965e0549f6d1f5a0168a652d2bfa28cd9a"',
        }

        headers = {
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.instagram.com',
            'priority': 'u=1, i',
            'referer': 'https://www.instagram.com/',
            'sec-ch-prefers-color-scheme': 'light',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-full-version-list': '"Chromium";v="128.0.6613.138", "Not;A=Brand";v="24.0.0.0", "Google Chrome";v="128.0.6613.138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"15.0.0"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': str(user_agent.generate_user_agent()),
            'x-asbd-id': '129477',
            'x-bloks-version-id': '235c9483d007713b45fc75b34c76332d68d579a4300a1db1da94670c3a05089f',
            'x-csrftoken': 'mf3zd6qWxnKgh9BaNRI5Ldpms2NrH62X',
            'x-fb-friendly-name': 'PolarisSearchBoxRefetchableQuery',
            'x-fb-lsd': 'BslibIYRWxn19hyIaPyrZV',
            'x-ig-app-id': '936619743392459',
        }

        data = {
            'variables': '{"data":{"context":"blended","include_reel":"true","query":"'+keyword+'","rank_token":"","search_surface":"web_top_search"},"hasQuery":true}',
            'doc_id': '7935512656557707',
        }
        try:
            response = requests.post('https://www.instagram.com/graphql/query', cookies=cookies, headers=headers, data=data).json()['data']['xdt_api__v1__fbsearch__topsearch_connection']['users']
            for i in response:
                us=i['user']['username']
                return {"data":{"message":"ok","username":us,"programmer":"@ii33cc"}}
        except:
            return{"data":{"Errur":"try agin"}}
    @staticmethod
    def Reset(email):
        try:
            import requests
            import user_agent
        except:
            o=["requests","user_agent"]
            for i in o:
                import os
                os.system("pip install {}".format(i))
        data = {
        'signed_body':'ef02f559b04e8d7cbe15fb8cf18e2b48fb686dafd056b7c9298c08f3e2007d43.{"_csrftoken":"dG4dEIkWvAWpIj1B2M2mutWtdO1LiPCK","adid":"5e7df201-a1ff-45ec-8107-31b10944e25c","guid":"b0382b46-1663-43a7-ba90-3949c43fd808","device_id":"android-71a5d65f74b8fcbc","query":"'f'{email}''"}',

        'ig_sig_key_version':'4',
    }	
        headers = {
        'X-Pigeon-Session-Id':'2b712457-ffad-4dba-9241-29ea2f472ac5',
        'X-Pigeon-Rawclienttime':'1707104597.347',
        'X-IG-Connection-Speed':'-1kbps',
        'X-IG-Bandwidth-Speed-KBPS':'-1.000',
        'X-IG-Bandwidth-TotalBytes-B':'0',
        'X-IG-Bandwidth-TotalTime-MS':'0',
        'X-IG-VP9-Capable':'false',
        'X-Bloks-Version-Id':'009f03b18280bb343b0862d663f31ac80c5fb30dfae9e273e43c63f13a9f31c0',
        'X-IG-Connection-Type':'WIFI',
        'X-IG-Capabilities':'3brTvw==',
        'X-IG-App-ID':'567067343352427',
        'User-Agent':str(user_agent.generate_user_agent()),
        'Accept-Language':'ar-IQ, en-US',
        'Cookie':'mid=Zbu4xQABAAE0k2Ok6rVxXpTD8PFQ; csrftoken=dG4dEIkWvAWpIj1B2M2mutWtdO1LiPCK',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Host':'i.instagram.com',
        'X-FB-HTTP-Engine':'Liger',
        'Connection':'keep-alive',
        'Content-Length':'364',
    }
        res = requests.post('https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/',headers=headers,data=data)
        if ('"can_recover_with_code"')in res.text:
            sdd=res.json()["email"]
            return {"data":{"status":True,"email_or_user":email,"reset":sdd,"programmer":"@ii33cc"}}
        elif "user_not_found"in res.text:
            return {"data":{"status":True,"email_or_user":email,"reset":"user_not_found","programmer":"@ii33cc"}} 	       
        elif "ip" or "Please wait a few minutes before you try again"in  res.text:  
            return {"data":{"status":False,"result":"ip block run vpn or use proxy","programmer":"@ii33cc"}} 	 
        else:
            return {"data":{"status":None,"email_or_user":email,"reset":None,"programmer":"@ii33cc"}}
    @staticmethod
    def GetData(Id):
        try:
            if int(Id) >1 and int(Id)<1279000:
                d= 2010
            elif int(Id)>1279001 and int(Id)<17750000:
                d= 2011
            elif int(Id) > 17750001 and int(Id)<279760000:
                d= 2012
            elif int(Id)>279760001 and int(Id)<900990000:
                d= 2013
            elif int(Id)>900990001 and int(Id)< 1629010000:
                d= 2014
            elif int(Id)>1900000000 and int(Id)<2500000000:
                d= 2015
            elif int(Id)>2500000000 and int(Id)<3713668786:
                d= 2016
            elif int(Id)>3713668786 and int(Id)<5699785217:
                d= 2017
            elif int(Id)>5699785217 and int(Id)<8507940634:
                d= 2018
            elif int(Id)>8507940634 and int(Id)<21254029834:
                d= 2019
            else:
                d= "2020-2025"
            return {"message":{"status":True,"data":d,"programmer":"@ii33cc"}}
        except:
            return {"message":{"status":False,"data":False,"programmer":"@ii33cc"}}
    @staticmethod
    def loginweb(username,password):
        a=str(time.time()).split(".")[1]
        headers = {
            'accept': '*/*',
            'accept-language': 'ar,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.instagram.com',
            'priority': 'u=1, i',
            'referer': 'https://www.instagram.com/',
            'sec-ch-prefers-color-scheme': 'light',
            'sec-ch-ua': '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
            'sec-ch-ua-full-version-list': '"Not(A:Brand";v="99.0.0.0", "Microsoft Edge";v="133.0.3065.92", "Chromium";v="133.0.6943.142"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"10.0.0"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': str(user_agent.generate_user_agent()),
            'x-asbd-id': '359341',
            'x-csrftoken': 'JwprPHIEz6Ay9speTWqA0wCqFw9hHARt',
            'x-ig-app-id': '936619743392459',
            'x-ig-www-claim': '0',
            'x-instagram-ajax': '1020778632',
            'x-requested-with': 'XMLHttpRequest',
            'x-web-session-id': 'rhcefi:mkhs1v:b6t13o',
        }
        data = {
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{a}:{password}',
            'caaF2DebugGroup': '0',
            'loginAttemptSubmissionCount': '0',
            'optIntoOneTap': 'false',
            'queryParams': '{}',
            'trustedDeviceRecords': '{}',
            'username': username,
        }

        response = requests.post('https://www.instagram.com/api/v1/web/accounts/login/ajax/', headers=headers, data=data)
        if "userId" and '"authenticated":true' in response.text:
            ses=response.cookies.get_dict()['sessionid']
            return {"data":{"status":True,"username":username,"paswerd":password,"login":True,"sessionId":ses,"programmer":"@ii33cc"}}
        elif '{"user":true,"authenticated":false,"error_type":"UserInvalidCredentials","status":"ok"}'in response.text:
            return {"data":{"status":True,"username":username,"paswerd":password,"login":"bad_password","programmer":"@ii33cc"}}
        elif "two_factor_required"in response.text:
            return {"data":{"status":True,"username":username,"paswerd":password,"login":"two_factor_required","programmer":"@ii33cc"}}
        elif "challenge_required" or "checkpoint_required"in response.text:
            return {"data":{"status":True,"username":username,"paswerd":password,"login":"sceure","programmer":"@ii33cc"}}
        elif '"spam":true'or "ip" or "Please wait a few minutes before you try again"in response.text:
            return {"data":{"status":False,"username":username,"paswerd":password,"login":"ip block run vpn or use proxy","programmer":"@ii33cc"}}
        else:
            return response.text
class HOTMAIL:
    @staticmethod
    def CheckEmail(email):
        if not "@"in email:
            return {"data":{"status":None,"message":"use @hotmail.com or @outlook.com in email","error_code":3,"programmer":"@ii33cc"}}
        reqz=requests.Session()
        try:
            headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
            "Host": "signup.live.com",
            "Connection": "keep-alive",
            "X-Requested-With": "XMLHttpRequest"
            }
            url="https://signup.live.com/signup.aspx?lic=1"
            response=reqz.get(url, headers=headers)
            apiCanary = re.search("apiCanary\":\"(.+?)\",", str(response.content)).group(1)
            apiCanary = str.encode(apiCanary).decode("unicode_escape").encode("ascii").decode("unicode_escape").encode("ascii").decode("ascii");url  = "https://signup.live.com/API/CheckAvailableSigninNames";json = {
            "signInName": email,
            "includeSuggestions": True}
            res = reqz.post(url, headers={
            "Content-Type":"application/x-www-form-urlencoded; charset=utf-8",
            "canary":apiCanary
            }, json=json)
            if res.json()['isAvailable']==False:
                return {"data":{"status":False,"email":email,"error_code":0,"programmer":"@ii33cc"}}
            


            elif res.json()['isAvailable']==True:



                return {"data":{"status":True,"email":email,"error_code":1,"programmer":"@ii33cc"}}
        except:""
class AOL:
    @staticmethod
    #by l7n - asyncio
    def cookis():
        user_agent = "Mozilla/5.0 (" + ["Windows NT 10.0; Win64; x64", "Macintosh; Intel Mac OS X 11_3", "iPhone; CPU iPhone OS 15_2 like Mac OS X", "iPad; CPU OS 14_4 like Mac OS X"][random.randint(0, 3)] + ") AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + str(random.randint(90, 120)) + ".0." + str(random.randint(4000, 5000)) + "." + str(random.randint(100, 999)) + " Safari/537.36 Edg/" + str(random.randint(100, 125)) + ".0.0.0"
        headers={'user-agent': str(user_agent)}
        response=requests.get('https://login.aol.com/account/create',headers=headers)
        AS=response.cookies.get_dict()['AS']
        A1=response.cookies.get_dict()['A1']
        A3=response.cookies.get_dict()['A3']
        A1S=response.cookies.get_dict()['A1S']
        specData=response.text.split('''name="attrSetIndex">
        <input type="hidden" value="''')[1].split(f'" name="specData">')[0]
        specId=response.text.split('''name="browser-fp-data" id="browser-fp-data" value="" />
        <input type="hidden" value="''')[1].split(f'" name="specId">')[0]
        crumb=response.text.split('''name="cacheStored">
        <input type="hidden" value="''')[1].split(f'" name="crumb">')[0]
        sessionIndex=response.text.split('''"acrumb">
        <input type="hidden" value="''')[1].split(f'" name="sessionIndex">')[0]
        acrumb=response.text.split('''name="crumb">
        <input type="hidden" value="''')[1].split(f'" name="acrumb">')[0]
        return AS, A1, A3, A1S, specData, specId, crumb , sessionIndex, acrumb
    @staticmethod
    def CheckEmail(email):
        if '@' in email:email=email.split('@')[0]
        if '..' in email or '_' in email or len(email) < 5 or len(email) > 30:
            return {"data":{"status":False,"email":email,"error_code":1,"programmer":"@ii33cc"}}
        AS, A1, A3, A1S, specData, specId, crumb , sessionIndex, acrumb = AOL.cookis()
        cookies = {
            'gpp': 'DBAA',
            'gpp_sid': '-1',
            'A1':A1,
            'A3':A3,
            'A1S':A1S,
            '__gads': 'ID=c0M0fd00676f0ea1:T='+'4'+':RT='+'5'+':S=ALNI_MaEGaVTSG6nQFkSJ-RnxSZrF5q5XA',
            '__gpi': 'UID=00000cf0e8904e94:T='+'7'+':RT='+'6'+':S=ALNI_MYCzPrYn9967HtpDSITUe5Z4ZwGOQ',
            'cmp': 't='+'0'+'&j=0&u=1---',
            'AS': AS,
            }
        headers = {
            'authority': 'login.aol.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://login.aol.com',
            'referer': f'https://login.aol.com/account/create?specId={specId}&done=https%3A%2F%2Fwww.aol.com',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'x-requested-with': 'XMLHttpRequest',
            }
        params = {
            'validateField': 'userId',
        }
        data = f'browser-fp-data=%7B%22language%22%3A%22en-US%22%2C%22colorDepth%22%3A24%2C%22deviceMemory%22%3A8%2C%22pixelRatio%22%3A1%2C%22hardwareConcurrency%22%3A4%2C%22timezoneOffset%22%3A-60%2C%22timezone%22%3A%22Africa%2FCasablanca%22%2C%22sessionStorage%22%3A1%2C%22localStorage%22%3A1%2C%22indexedDb%22%3A1%2C%22cpuClass%22%3A%22unknown%22%2C%22platform%22%3A%22Win32%22%2C%22doNotTrack%22%3A%22unknown%22%2C%22plugins%22%3A%7B%22count%22%3A5%2C%22hash%22%3A%222c14024bf8584c3f7f63f24ea490e812%22%7D%2C%22canvas%22%3A%22canvas%20winding%3Ayes~canvas%22%2C%22webgl%22%3A1%2C%22webglVendorAndRenderer%22%3A%22Google%20Inc.%20(Intel)~ANGLE%20(Intel%2C%20Intel(R)%20HD%20Graphics%204000%20(0x00000166)%20Direct3D11%20vs_5_0%20ps_5_0%2C%20D3D11)%22%2C%22adBlock%22%3A0%2C%22hasLiedLanguages%22%3A0%2C%22hasLiedResolution%22%3A0%2C%22hasLiedOs%22%3A0%2C%22hasLiedBrowser%22%3A0%2C%22touchSupport%22%3A%7B%22points%22%3A0%2C%22event%22%3A0%2C%22start%22%3A0%7D%2C%22fonts%22%3A%7B%22count%22%3A33%2C%22hash%22%3A%22edeefd360161b4bf944ac045e41d0b21%22%7D%2C%22audio%22%3A%22124.04347527516074%22%2C%22resolution%22%3A%7B%22w%22%3A%221600%22%2C%22h%22%3A%22900%22%7D%2C%22availableResolution%22%3A%7B%22w%22%3A%22860%22%2C%22h%22%3A%221600%22%7D%2C%22ts%22%3A%7B%22serve%22%3A1704793094844%2C%22render%22%3A1704793096534%7D%7D&specId={specId}&cacheStored=&crumb={crumb}&acrumb={acrumb}&sessionIndex={sessionIndex}&done=https%3A%2F%2Fwww.aol.com&googleIdToken=&authCode=&attrSetIndex=0&specData={specData}&multiDomain=&tos0=oath_freereg%7Cus%7Cen-US&firstName=&lastName=&userid-domain=yahoo&userId={email}&password=&mm=&dd=&yyyy=&signup='
        response = requests.post('https://login.aol.com/account/module/create', params=params,  headers=headers, data=data,cookies=cookies).text
        if '{"errors":[{"name":"firstName","error":"FIELD_EMPTY"},{"name":"lastName","error":"FIELD_EMPTY"},{"name":"birthDate","error":"INVALID_BIRTHDATE"},{"name":"password","error":"FIELD_EMPTY"}]}' in response:
                return {"data":{"status":True,"email":email,"error_code":0,"programmer":"@ii33cc"}}
        else:
                return {"data":{"status":False,"email":email,"error_code":1,"programmer":"@ii33cc"}}
class TIKTOK:
    @staticmethod
    def sign(params, payload: str = None, sec_device_id: str = "", cookie: str or None = None, aid: int = 1233, license_id: int = 1611921764, sdk_version_str: str = "2.3.1.i18n", sdk_version: int =2, platform: int = 19, unix: int = None):
        x_ss_stub = md5(payload.encode('utf-8')).hexdigest() if payload != None else None
        data=payload
        if not unix: unix = int(time.time())
        return Gorgon(params, unix, payload, cookie).get_value() | { "x-ladon"   : Ladon.encrypt(unix, license_id, aid),"x-argus"   : Argus.get_sign(params, x_ss_stub, unix,platform        = platform,aid             = aid,license_id      = license_id,sec_device_id   = sec_device_id,sdk_version     = sdk_version_str, sdk_version_int = sdk_version)}
    @staticmethod
    def CheckEmail(email,st):
        secret = secrets.token_hex(16)
        session = requests.Session()
        cookies = {
            "passport_csrf_token": secret,
            "passport_csrf_token_default": secret,
            "sessionid": st
        }
        session.cookies.update(cookies)
        device_brands = ["samsung", "huawei", "xiaomi", "apple", "oneplus"]
        device_types = ["SM-S928B", "P40", "Mi 11", "iPhone12,1", "OnePlus9"]
        regions = ["AE", "IQ", "US", "FR", "DE"]
        languages = [ "en"]
        params = {
        'passport-sdk-version': "6030790",
        'iid': str(random.randint(1, 10**19)),
        'device_id': str(random.randint(1, 10**19)),
        'ac': "WIFI",
        'channel': "googleplay",
        'aid': "1233",
        'app_name': "musical_ly",
        'version_code': "360505",
        'version_name': "36.5.5",
        'device_platform': "android",
        'os': "android",
        'ab_version': "36.5.5",
        'ssmix': "a",
        'device_type': random.choice(device_types),
        'device_brand': random.choice(device_brands),
        'language': random.choice(languages),
        'os_api': str(random.randint(28, 34)),
        'os_version': str(random.randint(10, 14)),
        'openudid': str(binascii.hexlify(urandom(8)).decode()),
        'manifest_version_code': "2023605050",
        'resolution': "1440*2969",
        'dpi': str(random.choice([420, 480, 532])),
        'update_version_code': "2023605050",
        '_rticket': str(round(random.uniform(1.2, 1.6) * 100000000) * -1) + "4632",
        'is_pad': "0",
        'app_type': "normal",
        'sys_region': random.choice(regions),
        'last_install_time': str(random.randint(1600000000, 1700000000)),
        'mcc_mnc': "41820",
        'timezone_name': "Asia/Baghdad",
        'carrier_region_v2': "418",
        'app_language': random.choice(languages),
        'carrier_region': random.choice(regions),
        'ac2': "wifi",
        'uoo': "0",
        'op_region': random.choice(regions),
        'timezone_offset': str(random.randint(0, 14400)),
        'build_number': "36.5.5",
        'host_abi': "arm64-v8a",
        'locale': random.choice(languages),
        'region': random.choice(regions),
        'ts': str(round(random.uniform(1.2, 1.6) * 100000000) * -1),
        'cdid': str(uuid.uuid4()),
        'support_webview': "1",
        'reg_store_region': random.choice(regions).lower(),
        'user_selected_region': "0",
        'cront_version': "1c651b66_2024-08-30",
        'ttnet_version': "4.2.195.8-tiktok",
        'use_store_region_cookie': "1"
    }
        m=TIKTOK.sign(params=urlencode(params),payload="",cookie="")
        device_type = params["device_type"]
        app_name = "com.zhiliaoapp.musically"
        app_version = f"{random.randint(2000000000, 3000000000)}"
        platform = "Linux"
        os = f"Android {random.randint(10, 15)}"
        locales = ["ar_AE", "en_US", "fr_FR", "es_ES"]
        locale = random.choice(locales)
        device_types = ["phone", "tablet", "tv"]
        device_type = random.choice(device_types)
        build = f"UP1A.{random.randint(200000000, 300000000)}"
        cronet_version = f"{random.randint(10000000, 20000000)}"
        cronet_date = f"{random.randint(2023, 2025)}-{random.randint(1, 12):02}-{random.randint(1, 28):02}"
        quic_version = f"{random.randint(10000000, 20000000)}"
        quic_date = f"{random.randint(2023, 2025)}-{random.randint(1, 12):02}-{random.randint(1, 28):02}"

        user_agent = (f"{app_name}/{app_version} ({platform}; U; {os}; {locale}; {device_type}; "
                    f"Build/{build}; Cronet/{cronet_version} {cronet_date}; "
                    f"QuicVersion:{quic_version} {quic_date})")
        headers = {
                'User-Agent': user_agent,
                'x-tt-passport-csrf-token': secret,
                'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
                'x-argus': m["x-argus"],
                'x-gorgon': m["x-gorgon"],
                'x-khronos': m["x-khronos"],
                'x-ladon': m["x-ladon"]
                }

        url = "https://api16-normal-c-alisg.tiktokv.com/passport/email/bind_without_verify/"
        try:
            res = session.post(url, params=params, data="email={}".format(email), headers=headers).json()
            errur_code=res.get('data').get('error_code')
            description=res.get('data').get("description")
            if int(errur_code)==1023:
                return{"data":{"status":True,"description":description,"error_code":errur_code,"programmer":"@ii33cc"}}
            elif int(errur_code)==1:
                return{"data":{"status":description,"error_code":errur_code,"programmer":"@ii33cc"}}
            else:
                return{"data":{"status":False,"description":description,"error_code":errur_code,"programmer":"@ii33cc"}}
        except Exception as e:
            return{"data":{"status":"Error {}".format(e),"programmer":"@ii33cc"}}
    @staticmethod
    def info(user):
        he={
        'X-RapidAPI-Host': 'tiktok-video-no-watermark2.p.rapidapi.com',
        'X-RapidAPI-Key': '54eb4910e1msh0b7d1211a1be475p12c3aejsnd55f85d359f3',
        'Host': 'tiktok-video-no-watermark2.p.rapidapi.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.14.7',
        }
        try:
            url=f'https://tiktok-video-no-watermark2.p.rapidapi.com/user/info?unique_id={user}&user_id='
            r=requests.get(url,headers=he).json()
            ids = r['data']['user']['id']
            user = user  
            name=r['data']['user']['nickname']
            folon = r['data']['stats']['followingCount']
            folos = r['data']['stats']['followerCount']
            lik =  r['data']['stats']['heartCount']
            vid = r['data']['stats']['videoCount']
            priv = r['data']['user']['privateAccount']
            return{"data":{"status":True,"username":user,"id":ids,"name":name,"following":folon,"follower":folos,"like":lik,"video":vid,"'private":priv,"programmer":"@ii33cc"}}
        except:
            return{"data":{"status":"user not found ","programmer":"@ii33cc"}}
