import requests
from bs4 import BeautifulSoup as b
import re
import time
from random import randint

def pdfFileName(content):
    pattern = r'filename\*?=.*?(?:UTF-8\'\'|)([\w\.-]+)'

    # Perform the search
    match = re.search(pattern, content)

    # Extract the filename if a match is found
    if match:
        filename = match.group(1)
        return filename
    else:
        print("Filename not found.")
        return None

def getRefUrl(origin,params):
    req = requests.models.PreparedRequest()
    req.prepare_url(origin, params)
    return req.url
    

def getTitleSuggestions(title):
    base_url = 'https://api.crossref.org/works'
    params = {
            'query.bibliographic': title,
            'rows': 100
        }
    response = requests.get(base_url, params=params)
    return response


def sementic(query,pageNumber):
    params = {
        # "year[0]":2021,
        # "year[1]":2024,
        "q":query,
        "sort":"relevance",
        "pdf":True
    }
    origin = "https://www.semanticscholar.org/search"

    headers = {
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,hi;q=0.7,ta;q=0.6',
        'cache-control': 'no-cache,no-store,must-revalidate,max-age=-1',
        'content-type': 'application/json',
        # 'cookie': 's2Exp=new_ab_framework_aa%3D-control%26pdp_citation_and_reference_paper_cues%3D-enable_citation_and_reference_paper_cues%26venues%3D-enable_venues%26reader_link_styling%3D-control%26topics_beta3%3D-topics_beta3%26alerts_aa_test%3D-control%26personalized_author_card_cues%3D-control%26term_understanding%3D-control%26aa_user_based_test%3D-control%26paper_cues%3D-all_paper_cues%26new_ab_framework_mock_ab%3D-control%26aa_stable_hash_session_test%3Dtest; tid=rBIABmbicOaiowALBR+cAg==; _gcl_au=1.1.910869331.1726116071; sid=25b98024-8aac-4f8c-a343-c129368cac13; _ga=GA1.1.367588128.1726116071; __hstc=132950225.7980d4f9ab8f056700671ef23117af68.1726116071649.1726116071649.1726116071649.1; hubspotutk=7980d4f9ab8f056700671ef23117af68; __hssrc=1; pv2more=1726116085; pv2more10s=1726116085; aws-waf-token=7daa3c46-5225-4416-ab3e-389482151c2e:HgoAk8El+44AAAAA:55VpN/fU2CCPkHhi8K1b2TcAsm7dttSy53cvzy4VVyDkihrFrEO2g8g7GCe3QpzKRyxkqBIEpP8XRzmNSGKUtnVe4OXwKpy/lhLV4SSWOuR5JtoDGL4gcDO2nsHZ8NVxUrKBdRnuy00plUq+jJ6FcqgFmW8QC8vwwxyf3YaBx7/ZKqPmew1Z+tsndTANXZSIT9q5wab7RHM+qIO1xi5c90m21AEqhCUW; pvSession=5; tisestart=1726118941; _ga_H7P4ZT52H5=GS1.1.1726116071.1.1.1726118949.49.0.0',
        'origin': 'https://www.semanticscholar.org',
        'priority': 'u=1, i',
        'referer': getRefUrl(origin=origin,params=params),
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'x-s2-client': 'webapp-browser',
        'x-s2-ui-version': '53003fbcd5add31d1897996146f69e1495789ae8',
    }

    json_data = {
        'queryString': query,
        'page': pageNumber,
        'pageSize': 10,
        'sort': 'relevance',
        'authors': [],
        'coAuthors': [],
        'venues': [],
        'yearFilter':None,
        #   {
            # 'min': 2021,
            # 'max': 2024,
        # },
        'requireViewablePdf': True,
        'fieldsOfStudy': [],
        'hydrateWithDdb': True,
        'includeTldrs': True,
        'performTitleMatch': True,
        'includeBadges': True,
        'getQuerySuggestions': False,
        'cues': [
            'CitedByLibraryPaperCue',
            'CitesYourPaperCue',
            'CitesLibraryPaperCue',
        ],
        'includePdfVisibility': True,
    }

    response = requests.post('https://www.semanticscholar.org/api/1/search', headers=headers, json=json_data)
    return response

def get_list_of_dois(API_KEY,q,nextUrl):
    headers = {
        'X-ELS-APIKey': API_KEY,
        'Accept': 'application/json'
    }

    if q and not nextUrl :
        query = f'TITLE-ABS-KEY({q}) AND PUBYEAR > 2018 AND OPENACCESS(1)'
        url = f'https://api.elsevier.com/content/search/scopus?query={q}'
        response = requests.get(url, headers=headers)
    
    if nextUrl:
        response = requests.get(nextUrl)

    if response.status_code == 200:
        data = response.json()
        list_of_dois = [entry.get('prism:doi', 'No DOI') for entry in data['search-results']['entry']]
        for x in data["search-results"]["link"]:
            if x["@ref"] == "next":
                nextUrl = x["@href"]
        return list_of_dois,nextUrl

def hrefDOI(soup):
    try:
        href = soup.find("button")["onclick"]
        url_pattern = r"href='(/[^']+)'"
        match = re.search(url_pattern, href)
        if match:
            extracted_url = match.group(1)
            if "//" in extracted_url and "sci-hub.se" in extracted_url:
                extracted_url = "https:" + extracted_url
            else:
                extracted_url = "https://sci-hub.se"+extracted_url
            return extracted_url
        else:
            return None
    except:
        return None

def getdoi(title):
    url = "https://api.crossref.org/works"
    params = {
        "query.title": title
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    if data["message"]["items"]:
        return data["message"]["items"][0]["DOI"]
    else:
        return None
    
def responseforDOI(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = b(response.content)
        return soup
    else:return None


def getFromSciHub(data):
    cookies = {
        '__ddg1_': 'Gu8nULx25N7uBsj5PgDB',
        'session': '9622fc55e5adafc75a339005ab0e870d',
        'refresh': '1722575229.7413',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,hi;q=0.7,ta;q=0.6',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        # 'cookie': '__ddg1_=Gu8nULx25N7uBsj5PgDB; session=9622fc55e5adafc75a339005ab0e870d; refresh=1722575229.7413',
        'origin': 'https://sci-hub.se',
        'priority': 'u=0, i',
        'referer': 'https://sci-hub.se/',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }

    response = requests.post('https://sci-hub.se/', cookies=cookies, headers=headers, data=data)
    
    return response

def processShihub(soup):
    if soup.find("embed")["id"] == "pdf":
        src = str(soup.find("embed")["src"])
        print(src)
        if "sci-hub.se" in src:
            src = "https:" + src
        else:
            src = "https://sci-hub.se/"+src
        pattern = r"https?://[^\s]+?\.pdf"
        url = re.search(pattern, src).group()
        return url+"?download=true"

def schiHub(link):
    try:
        response = getFromSciHub(data={'request': link,})
        while response.status_code != 200:
            print("I AM GOING TO SLEEP AS I AM NOT GETTING THE PROPER RESPONSE FROM SCIHUB")
            time.sleep(randint(15,20))
            response = getFromSciHub(data={'request': link})
        soupObj = getSoupObject(response.content)
        url = processShihub(soupObj)
        return url
    except Exception as e:
        print(link)
        print(e)
        return None


def requestGoogleScholar(q,start):
    cookies = {
    'SEARCH_SAMESITE': 'CgQIz5sB',
    'GSP': 'LM=1721320033:S=sOcZ5ASf37IEyhQZ',
    'HSID': 'Aglz7LCwUFNeMO0JL',
    'SSID': 'AAVUiDI-nNttOibZP',
    'APISID': 'mZ6ddqfyC4F_pzK5/AP-_qUut_ZgW-yicG',
    'SAPISID': 'BU1c_Pnut09wwfrP/A--924K1uxvl_F-4O',
    '__Secure-1PAPISID': 'BU1c_Pnut09wwfrP/A--924K1uxvl_F-4O',
    '__Secure-3PAPISID': 'BU1c_Pnut09wwfrP/A--924K1uxvl_F-4O',
    'OGPC': '19031986-1:',
    'SID': 'g.a000nwjdidtZCyzj8NW1TmTqDlLGC-6nS1wU2okkJrTvpbesq4LKsxEPPxDCPoDrKhMugwLWNAACgYKARwSARMSFQHGX2MiEWCT-xtJPhPIqykp6PYRZRoVAUF8yKrrXr_YoeDL5kzQli2FM7SX0076',
    '__Secure-1PSID': 'g.a000nwjdidtZCyzj8NW1TmTqDlLGC-6nS1wU2okkJrTvpbesq4LKVAre8bdVcO7j4oITq_QPEgACgYKARESARMSFQHGX2MiBES2xlssiAgAcyYWIl6FHRoVAUF8yKrhJpnd5IslBxTvC24LC8St0076',
    '__Secure-3PSID': 'g.a000nwjdidtZCyzj8NW1TmTqDlLGC-6nS1wU2okkJrTvpbesq4LKj2ziQ0UpQEQ_NyYYGYfLUgACgYKARMSARMSFQHGX2MiQER7xlcxl1beQ9tGCDdUtRoVAUF8yKq9Tbq2FJR8SG15dv6WEbJ00076',
    'AEC': 'AVYB7cro0GT772XV8vs1MRTiO1SfSkqJ2V_plXPYrbaA2HTzgBYUk4B8tqg',
    '__Secure-1PSIDTS': 'sidts-CjIBQlrA-ENJGrDU0o2iB22L_-JBICcp_F5nuRg3sSVnp28SfgwQuY71vEOzOoX-IJMfPBAA',
    '__Secure-3PSIDTS': 'sidts-CjIBQlrA-ENJGrDU0o2iB22L_-JBICcp_F5nuRg3sSVnp28SfgwQuY71vEOzOoX-IJMfPBAA',
    'NID': '517=E0CQk8ZZbTfZurpJ4Ib7l0jHQLe5jzkJIUd_LXfxIKTaVUMFoqz3ldTuYigV55ow00esVfsdp1wB3d8Lfyvf8n9pzHfylCd4081tQk28XGjlqIUCBy1iU0mBENoeuTeJDRsUEPuJeVsig8iYb1s9AjMyAVOHRX-dW-Fgaib-5xDrol0pfrZW9Gpj7sWkyGu6joTq6eXCkpPKE-EfeRdaji5x9jNZUbEfTs4e98xIKckXX2LJwlAYX1GeekGHU-tMN9J4TMNyIK5p-4_gmiXWP5fS40l6-ApiDG7dqX7Bs5pCxjwRNIRNtJ8zgpDq71ieQ3lnYgsC-YFven8XukaHnNoULA8N9PTe0BaqFG13cTvoyeCDpEu156hMWMqauYsdqRpz6ZoUQVk57Y4jr3NY2QEoLVfcYT_M-uZZFa5xI7qRQm0MHIWluRDVJ9-_VBfdfzRg73T_s7hcA18mdcjolBwSgvJOY4SStHxF-FRD8vzrOwH7HcwPSb7arRzzJGNQfmW3zGtqfJIX4XDbce37hxxGe3PNP9TenfShmXP8DO6H_zTSzlth9pwRtWBN3T5Khrsg_wcA72Yxm8GyCRxvUHfdiy6J1SAqJCgPnKvV32_BG0RPbbN542vXxV6Jvm_FZ14FT-ohiV4B9L2mt__rDBBiYjgbfr_B7WR0IwIbSHENYMXM6R-R09X4mlR4Eqc7z7JyM8pO58yDcZB7XD7UQyohhNcaa0MQEXBbpfkF1Cw3FGYnJem4z98-PdTTKUdbugPOUM-3Mq8mKik5PG2iOUcbKLJvn011IeMKC-2SIoDMA3LEuQu77rOpk6UeYw4oDrrpRwPRBnqi0lTrWPZZ-L84W6v5X-b9mQfXDMqqJAnvd0cnaK3rUS_gihG6d4-2jEqVJRQmiAwToSR8Pw_62gXS2YbDXVO6PcpcSrTeYcsaD1Da-Zfs3jVeNNCi6f7wWO9wuCWQNigm8D_-VKD9dSgdV-XM2VJzNdVQ8qJ4aFpR9h1qHbNQBYKw5-lT914k_bcufFXh-VQIbjS5yru_Nh5ua_k3rWfGil24w5gd47IZPQ3lnVSyjVkmdw4-RGVoy32Gk10g1q8dWDgKqEKhJGz3UUL8GZ-WdZG5i-6gH7DvMA14W6UQHNzHWFgnP2B3tZ8r46u2clFXejG244ZV3T43myzSlUAVMFNibPpDfI6tfxuOR5yzFA9Nw3xLmUvpWbvKMHF75Lq5Lba1xhFjsdSXj0PhNXCr3y_YhrY7l_iFOaDJDqiyLm3n9U5EoKGqIO8P_oURy8yIdsSNhPcJ6KG_JXEZmA',
    'SIDCC': 'AKEyXzUeznFJFFkd44FnqaCbO6tM-VGd848eZbrwQ_KaCdljpDiUFT0n62mvjGyPCvLmmJXKlTzq',
    '__Secure-1PSIDCC': 'AKEyXzXG5Wm_OVaQ0WiH0whvEiBd1zENJvLHY7hfE2kkH2I_kBfnIa9TLDH80Vbdrx2B1l640s0',
    '__Secure-3PSIDCC': 'AKEyXzWhagyMbpyxZltfL1amDWojg2eDGika8OeEXsqvmCLnSX4TAOfPPlNkVL-OvFY43Nqkymg',
    }
    # cookies = {
    #     'SEARCH_SAMESITE': 'CgQIz5sB',
    #     'SID': 'g.a000lwjdiTeS8gzovagXU7DAcImQU34FudJKrB7QeHQu6mnoxDlKkeYcGTrffPiL7c-iy8nkPwACgYKAc4SARMSFQHGX2Mi0lHmlHoE2tp4-QzF7BNbTxoVAUF8yKpb7CjEiCsmUHH1pThSyeH00076',
    #     '__Secure-1PSID': 'g.a000lwjdiTeS8gzovagXU7DAcImQU34FudJKrB7QeHQu6mnoxDlKEPVK7rc-gb_m2Rij-EG9zwACgYKAdMSARMSFQHGX2MiS8Ao17Mo6wUTSnvVT3YSoxoVAUF8yKpC6K9VoydeSGpVYcwtdbwb0076',
    #     '__Secure-3PSID': 'g.a000lwjdiTeS8gzovagXU7DAcImQU34FudJKrB7QeHQu6mnoxDlK-OS4H5q53fjOLcyNz7q7BAACgYKAQASARMSFQHGX2Mi8qUo3PabJevpiokGgQbXzxoVAUF8yKp-3_qlwdpDQSs3EM_khsdf0076',
    #     'HSID': 'ANLuzn3oG0EfezD0Z',
    #     'SSID': 'APlH5NZz3WJwxFIgY',
    #     'APISID': 'yLPoDuk4-553ur2l/ASzeFrpdj1Trty2pu',
    #     'SAPISID': '04u2xb9Hc1jSRW9T/AGcoaIZoJQvaGyTvj',
    #     '__Secure-1PAPISID': '04u2xb9Hc1jSRW9T/AGcoaIZoJQvaGyTvj',
    #     '__Secure-3PAPISID': '04u2xb9Hc1jSRW9T/AGcoaIZoJQvaGyTvj',
    #     'GSP': 'LM=1721320033:S=sOcZ5ASf37IEyhQZ',
    #     'AEC': 'AVYB7cp3p4zdFCvDauDedKlqzJaFiYMJsFPetETYHiVyDEBawo3dwNi1iec',
    #     'NID': '516=brb1CFQMcZZQLFlEy6AlzRCwAM467_JbMUHoezD54Ww7ca9Q2oql8eh-MPmrrmuLcKBTVHxuuAFgJKKxynW1waxOg8jW2hLl_2Sz-EaHNiH3INPw4qcnkirsOBo-Hc9VRy2gMyfZrcIcud_LbF4zaTyO9L57qbO5vQCDvKk4zZccc491p0VFGXeGcss95vHyGyiQWlDkJBzGZmJ2Ky5JCVBhLuKMwYfIZNINha2myyOVBMyLqk62w0crLfeFhtX0tFi3k_vriOxrFhMrOZRfiNyqNZ4NGyZ87j9SnfQKTcvGH1lyapeIni0ZCxf40IMVr-9jFWCtTYh-6_srlcYeK4520FX9Hy4ExRAvLQUKfO__AEHXMdXYyiWMjpNMlkKUoOtNnrmaFV9H6BPU5c7468uvyxjAhU0W98famy6PrcFPAmpxiaMMeURlC3sHdZwHBqgdLQdd3tIlLNH-vrCGFO7_wqAC9pJ81Rgkf9dBtBh3v5-mW2AHQen4kIZvqacn4YAkulQcsxGUsqXiSLaldjFQiW7Vj0reM1DqkAzfSXE0HJ-tVsVjobkwv3NXEBpbDNBfj3dYPrwHMuCAvUT7AcPs_9vZuBpXCgWylNYQc5PsAppfTCcjFKRUKwz4cLKvZ4KPdcSM4-Dq89hGjr4YimFrRSb3rqpTFbHfOIaoMmdmJekMLBbzsEKWsikaAhEVowTC7JZBXRCdKZvtBuV2ZDbwFYij9VSIAzwyMgJ47jWsrvLwVh7UTeXC9q0j45wMnIimd_MOB-vX4Gq5qoC60OqCBLgM6NbzHsnexNENavGvs9CNmMX519VhvxN6T35hOzLTel2MzgCP_9LKjEcgX4FFXFza7s07FvSUpbWZa61xEpVy2cc-4cc55vLTzJJTVSms7uOl_QxGAi_GGe40Miz95DzUaCE3OMLF9He1U8_UtrcCZfL8FYaD0Y3TiITOADv-8q7XInGUvXNsQ9WOqlPy0z_Oy4bevL_G5dwzOJwDxgMW8Xrse6gXuP3jBvbOG_XNDF07ySsjht4s_TVmGZibz4LxFUpQfYtND3MqdOOHGUJwu7nS1sy32Hf6xOn-Z8VxGazP4qSbd8CmBIigZ4xL9ed99Im19Ab2PZ35VUH75BVFPHRLObTVunPzkICCAX3B0vQm2bxZyiwsJ70dYqfjwXD7FpuUQWUOwgcKYb7txq9AvlQJvF6OgYGfAivkZ7hQ1VH3RWQZhen7BMrDwP-Vidb9wxuswaw9',
    #     '__Secure-1PSIDTS': 'sidts-CjIB4E2dkbZDfal6UhARPaA5S2QF3pfPesEEELCjyChPPok6M6J-8sR3q2jtPtG-2TCoyRAA',
    #     '__Secure-3PSIDTS': 'sidts-CjIB4E2dkbZDfal6UhARPaA5S2QF3pfPesEEELCjyChPPok6M6J-8sR3q2jtPtG-2TCoyRAA',
    #     'SIDCC': 'AKEyXzUHq4nCF5gXSxOA8ClKd2nznsmwMOy6gbdbXNlnWxXqJok32phmhjUS4rfuC-eHVjBhqEk',
    #     '__Secure-1PSIDCC': 'AKEyXzUsRVWsVn7eNB2k2LLCPjqMegbPnK4Z96alLC5qCmutFYH-h5rlcI3-eQZjUPggmMS9_w',
    #     '__Secure-3PSIDCC': 'AKEyXzUXNzSTo4MfTmMxoZ97008tkfJPfbs06-RuIpx-smnJxlnofLgmzpDc4zhmJ40W1YlynA',
    # }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,hi;q=0.7,ta;q=0.6',
        # 'cookie': 'SEARCH_SAMESITE=CgQIz5sB; SID=g.a000lwjdiTeS8gzovagXU7DAcImQU34FudJKrB7QeHQu6mnoxDlKkeYcGTrffPiL7c-iy8nkPwACgYKAc4SARMSFQHGX2Mi0lHmlHoE2tp4-QzF7BNbTxoVAUF8yKpb7CjEiCsmUHH1pThSyeH00076; __Secure-1PSID=g.a000lwjdiTeS8gzovagXU7DAcImQU34FudJKrB7QeHQu6mnoxDlKEPVK7rc-gb_m2Rij-EG9zwACgYKAdMSARMSFQHGX2MiS8Ao17Mo6wUTSnvVT3YSoxoVAUF8yKpC6K9VoydeSGpVYcwtdbwb0076; __Secure-3PSID=g.a000lwjdiTeS8gzovagXU7DAcImQU34FudJKrB7QeHQu6mnoxDlK-OS4H5q53fjOLcyNz7q7BAACgYKAQASARMSFQHGX2Mi8qUo3PabJevpiokGgQbXzxoVAUF8yKp-3_qlwdpDQSs3EM_khsdf0076; HSID=ANLuzn3oG0EfezD0Z; SSID=APlH5NZz3WJwxFIgY; APISID=yLPoDuk4-553ur2l/ASzeFrpdj1Trty2pu; SAPISID=04u2xb9Hc1jSRW9T/AGcoaIZoJQvaGyTvj; __Secure-1PAPISID=04u2xb9Hc1jSRW9T/AGcoaIZoJQvaGyTvj; __Secure-3PAPISID=04u2xb9Hc1jSRW9T/AGcoaIZoJQvaGyTvj; GSP=LM=1721320033:S=sOcZ5ASf37IEyhQZ; AEC=AVYB7cp3p4zdFCvDauDedKlqzJaFiYMJsFPetETYHiVyDEBawo3dwNi1iec; NID=516=brb1CFQMcZZQLFlEy6AlzRCwAM467_JbMUHoezD54Ww7ca9Q2oql8eh-MPmrrmuLcKBTVHxuuAFgJKKxynW1waxOg8jW2hLl_2Sz-EaHNiH3INPw4qcnkirsOBo-Hc9VRy2gMyfZrcIcud_LbF4zaTyO9L57qbO5vQCDvKk4zZccc491p0VFGXeGcss95vHyGyiQWlDkJBzGZmJ2Ky5JCVBhLuKMwYfIZNINha2myyOVBMyLqk62w0crLfeFhtX0tFi3k_vriOxrFhMrOZRfiNyqNZ4NGyZ87j9SnfQKTcvGH1lyapeIni0ZCxf40IMVr-9jFWCtTYh-6_srlcYeK4520FX9Hy4ExRAvLQUKfO__AEHXMdXYyiWMjpNMlkKUoOtNnrmaFV9H6BPU5c7468uvyxjAhU0W98famy6PrcFPAmpxiaMMeURlC3sHdZwHBqgdLQdd3tIlLNH-vrCGFO7_wqAC9pJ81Rgkf9dBtBh3v5-mW2AHQen4kIZvqacn4YAkulQcsxGUsqXiSLaldjFQiW7Vj0reM1DqkAzfSXE0HJ-tVsVjobkwv3NXEBpbDNBfj3dYPrwHMuCAvUT7AcPs_9vZuBpXCgWylNYQc5PsAppfTCcjFKRUKwz4cLKvZ4KPdcSM4-Dq89hGjr4YimFrRSb3rqpTFbHfOIaoMmdmJekMLBbzsEKWsikaAhEVowTC7JZBXRCdKZvtBuV2ZDbwFYij9VSIAzwyMgJ47jWsrvLwVh7UTeXC9q0j45wMnIimd_MOB-vX4Gq5qoC60OqCBLgM6NbzHsnexNENavGvs9CNmMX519VhvxN6T35hOzLTel2MzgCP_9LKjEcgX4FFXFza7s07FvSUpbWZa61xEpVy2cc-4cc55vLTzJJTVSms7uOl_QxGAi_GGe40Miz95DzUaCE3OMLF9He1U8_UtrcCZfL8FYaD0Y3TiITOADv-8q7XInGUvXNsQ9WOqlPy0z_Oy4bevL_G5dwzOJwDxgMW8Xrse6gXuP3jBvbOG_XNDF07ySsjht4s_TVmGZibz4LxFUpQfYtND3MqdOOHGUJwu7nS1sy32Hf6xOn-Z8VxGazP4qSbd8CmBIigZ4xL9ed99Im19Ab2PZ35VUH75BVFPHRLObTVunPzkICCAX3B0vQm2bxZyiwsJ70dYqfjwXD7FpuUQWUOwgcKYb7txq9AvlQJvF6OgYGfAivkZ7hQ1VH3RWQZhen7BMrDwP-Vidb9wxuswaw9; __Secure-1PSIDTS=sidts-CjIB4E2dkbZDfal6UhARPaA5S2QF3pfPesEEELCjyChPPok6M6J-8sR3q2jtPtG-2TCoyRAA; __Secure-3PSIDTS=sidts-CjIB4E2dkbZDfal6UhARPaA5S2QF3pfPesEEELCjyChPPok6M6J-8sR3q2jtPtG-2TCoyRAA; SIDCC=AKEyXzUHq4nCF5gXSxOA8ClKd2nznsmwMOy6gbdbXNlnWxXqJok32phmhjUS4rfuC-eHVjBhqEk; __Secure-1PSIDCC=AKEyXzUsRVWsVn7eNB2k2LLCPjqMegbPnK4Z96alLC5qCmutFYH-h5rlcI3-eQZjUPggmMS9_w; __Secure-3PSIDCC=AKEyXzUXNzSTo4MfTmMxoZ97008tkfJPfbs06-RuIpx-smnJxlnofLgmzpDc4zhmJ40W1YlynA',
        'priority': 'u=0, i',
        'referer': 'https://scholar.google.com/scholar?start=120&q=polyphenol+based+color+pdf&hl=en&as_sdt=0,5',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-full-version-list': '"Not/A)Brand";v="8.0.0.0", "Chromium";v="126.0.6478.182", "Google Chrome";v="126.0.6478.182"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Linux"',
        'sec-ch-ua-platform-version': '"6.5.0"',
        'sec-ch-ua-wow64': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'x-client-data': 'CIu2yQEIprbJAQipncoBCLbgygEIkqHLAQiPossBCPaYzQEIh6DNAQiyns4BCKyizgEI06bOAQjZp84BCICozgEIoq3OAQjkr84BCIyyzgEYoZ3OARjEn84BGLmuzgEYnbHOAQ==',
    }

    params = {
        "q":q,
        "hl":"en",
        "as_std":"0,5",
        "start":str(start)
    }

    response = requests.get(
        'https://scholar.google.com/scholar',
        params=params,
        headers=headers,
    )
    return response


def getRequestURL(q,start):
    params = {
        "q":q,
        "hl":"en",
        "as_std":"0,5",
        "start":str(start)
    }
    req = requests.models.PreparedRequest()
    req.prepare_url("https://scholar.google.com/scholar", params)
    return req.url

def getSoupObject(response):
    try:return b(response)
    except:return None

def forEachSoup(soup):
    try:authors = [author.text for author in soup.find('div', class_='gs_a').find_all('a')]
    except:authors = []
    linkTag = soup.find('a', href=True)
    try:
        data = {
        "title": soup.find('h3', class_='gs_rt').text.replace("[PDF]","").strip() or "",
        "link": soup.find('h3', class_='gs_rt').a['href'] or "",
        "downloadableLink":soup.find("a")["href"],
        "linkTag":linkTag['data-clk-atid'] if linkTag else None
        }
    except:
        data  = {
        "title": "",
        "link": "",
        "downloadableLink":"",
        "linkTag":""
        }
    return data

def schiHubDownload(url):

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,hi;q=0.7,ta;q=0.6',
        # 'cookie': 'SEARCH_SAMESITE=CgQIz5sB; SID=g.a000lwjdiTeS8gzovagXU7DAcImQU34FudJKrB7QeHQu6mnoxDlKkeYcGTrffPiL7c-iy8nkPwACgYKAc4SARMSFQHGX2Mi0lHmlHoE2tp4-QzF7BNbTxoVAUF8yKpb7CjEiCsmUHH1pThSyeH00076; __Secure-1PSID=g.a000lwjdiTeS8gzovagXU7DAcImQU34FudJKrB7QeHQu6mnoxDlKEPVK7rc-gb_m2Rij-EG9zwACgYKAdMSARMSFQHGX2MiS8Ao17Mo6wUTSnvVT3YSoxoVAUF8yKpC6K9VoydeSGpVYcwtdbwb0076; __Secure-3PSID=g.a000lwjdiTeS8gzovagXU7DAcImQU34FudJKrB7QeHQu6mnoxDlK-OS4H5q53fjOLcyNz7q7BAACgYKAQASARMSFQHGX2Mi8qUo3PabJevpiokGgQbXzxoVAUF8yKp-3_qlwdpDQSs3EM_khsdf0076; HSID=ANLuzn3oG0EfezD0Z; SSID=APlH5NZz3WJwxFIgY; APISID=yLPoDuk4-553ur2l/ASzeFrpdj1Trty2pu; SAPISID=04u2xb9Hc1jSRW9T/AGcoaIZoJQvaGyTvj; __Secure-1PAPISID=04u2xb9Hc1jSRW9T/AGcoaIZoJQvaGyTvj; __Secure-3PAPISID=04u2xb9Hc1jSRW9T/AGcoaIZoJQvaGyTvj; GSP=LM=1721320033:S=sOcZ5ASf37IEyhQZ; AEC=AVYB7cp3p4zdFCvDauDedKlqzJaFiYMJsFPetETYHiVyDEBawo3dwNi1iec; NID=516=brb1CFQMcZZQLFlEy6AlzRCwAM467_JbMUHoezD54Ww7ca9Q2oql8eh-MPmrrmuLcKBTVHxuuAFgJKKxynW1waxOg8jW2hLl_2Sz-EaHNiH3INPw4qcnkirsOBo-Hc9VRy2gMyfZrcIcud_LbF4zaTyO9L57qbO5vQCDvKk4zZccc491p0VFGXeGcss95vHyGyiQWlDkJBzGZmJ2Ky5JCVBhLuKMwYfIZNINha2myyOVBMyLqk62w0crLfeFhtX0tFi3k_vriOxrFhMrOZRfiNyqNZ4NGyZ87j9SnfQKTcvGH1lyapeIni0ZCxf40IMVr-9jFWCtTYh-6_srlcYeK4520FX9Hy4ExRAvLQUKfO__AEHXMdXYyiWMjpNMlkKUoOtNnrmaFV9H6BPU5c7468uvyxjAhU0W98famy6PrcFPAmpxiaMMeURlC3sHdZwHBqgdLQdd3tIlLNH-vrCGFO7_wqAC9pJ81Rgkf9dBtBh3v5-mW2AHQen4kIZvqacn4YAkulQcsxGUsqXiSLaldjFQiW7Vj0reM1DqkAzfSXE0HJ-tVsVjobkwv3NXEBpbDNBfj3dYPrwHMuCAvUT7AcPs_9vZuBpXCgWylNYQc5PsAppfTCcjFKRUKwz4cLKvZ4KPdcSM4-Dq89hGjr4YimFrRSb3rqpTFbHfOIaoMmdmJekMLBbzsEKWsikaAhEVowTC7JZBXRCdKZvtBuV2ZDbwFYij9VSIAzwyMgJ47jWsrvLwVh7UTeXC9q0j45wMnIimd_MOB-vX4Gq5qoC60OqCBLgM6NbzHsnexNENavGvs9CNmMX519VhvxN6T35hOzLTel2MzgCP_9LKjEcgX4FFXFza7s07FvSUpbWZa61xEpVy2cc-4cc55vLTzJJTVSms7uOl_QxGAi_GGe40Miz95DzUaCE3OMLF9He1U8_UtrcCZfL8FYaD0Y3TiITOADv-8q7XInGUvXNsQ9WOqlPy0z_Oy4bevL_G5dwzOJwDxgMW8Xrse6gXuP3jBvbOG_XNDF07ySsjht4s_TVmGZibz4LxFUpQfYtND3MqdOOHGUJwu7nS1sy32Hf6xOn-Z8VxGazP4qSbd8CmBIigZ4xL9ed99Im19Ab2PZ35VUH75BVFPHRLObTVunPzkICCAX3B0vQm2bxZyiwsJ70dYqfjwXD7FpuUQWUOwgcKYb7txq9AvlQJvF6OgYGfAivkZ7hQ1VH3RWQZhen7BMrDwP-Vidb9wxuswaw9; __Secure-1PSIDTS=sidts-CjIB4E2dkbZDfal6UhARPaA5S2QF3pfPesEEELCjyChPPok6M6J-8sR3q2jtPtG-2TCoyRAA; __Secure-3PSIDTS=sidts-CjIB4E2dkbZDfal6UhARPaA5S2QF3pfPesEEELCjyChPPok6M6J-8sR3q2jtPtG-2TCoyRAA; SIDCC=AKEyXzUHq4nCF5gXSxOA8ClKd2nznsmwMOy6gbdbXNlnWxXqJok32phmhjUS4rfuC-eHVjBhqEk; __Secure-1PSIDCC=AKEyXzUsRVWsVn7eNB2k2LLCPjqMegbPnK4Z96alLC5qCmutFYH-h5rlcI3-eQZjUPggmMS9_w; __Secure-3PSIDCC=AKEyXzUXNzSTo4MfTmMxoZ97008tkfJPfbs06-RuIpx-smnJxlnofLgmzpDc4zhmJ40W1YlynA',
        'priority': 'u=0, i',
        'referer': 'https://scholar.google.com/scholar?start=120&q=polyphenol+based+color+pdf&hl=en&as_sdt=0,5',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-full-version-list': '"Not/A)Brand";v="8.0.0.0", "Chromium";v="126.0.6478.182", "Google Chrome";v="126.0.6478.182"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Linux"',
        'sec-ch-ua-platform-version': '"6.5.0"',
        'sec-ch-ua-wow64': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'x-client-data': 'CIu2yQEIprbJAQipncoBCLbgygEIkqHLAQiPossBCPaYzQEIh6DNAQiyns4BCKyizgEI06bOAQjZp84BCICozgEIoq3OAQjkr84BCIyyzgEYoZ3OARjEn84BGLmuzgEYnbHOAQ==',
    }


    response = requests.get(
        url,
        headers=headers
    )
    return response

