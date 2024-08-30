import chromedriver_binary
import calendar, copy, datetime, json, os, requests, sys, threading, time, traceback, re, gzip, io, hmac, hashlib, base64, urllib.parse, random
from collections import Counter, defaultdict
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver
from requests_oauthlib import OAuth1Session


TIME334 = [3, 34]
KEYWORD = '334'
PHP_URL = os.environ['PHP_URL']
TOKENS = os.environ['TOKENS']
API_KEYS = os.environ['KEYS']
HTML_URL = 'https://abshrimp.github.io/334ranker/'
HTML_URL2 = 'https://abshrimp.github.io/334ranker/index2.html'
ANDROID_AUTH = os.environ['AUTH']
clients = ['Twitter for iPhone',  'Twitter for Android',  'Twitter Web Client',  'TweetDeck',  'TweetDeck Web App',  'Twitter for iPad',  'Twitter for Mac',  'Twitter Web App',  'Twitter Lite',  'Mobile Web (M2)',  'Twitter for Windows',  'Janetter',  'Janetter for Android',  'Janetter Pro for iPhone',  'Janetter for Mac',  'Janetter Pro for Android',  'Tweetbot for iΟS',  'Tweetbot for iOS',  'Tweetbot for Mac',  'twitcle plus',  'ツイタマ',  'ツイタマ for Android',  'ツイタマ+ for Android',  'Sobacha',  'SobaCha',  'Metacha',  'MetaCha',  'MateCha',  'ツイッターするやつ',  'ツイッターするやつγ',  'ツイッターするやつγ pro',  'jigtwi',  'feather for iOS',  'hamoooooon',  'Hel2um on iOS',  'Hel1um Pro on iOS',  'Hel1um on iOS',  'undefined']

records_rank, today_result, driver, request_body, request_header = {}, {}, {}, {}, {}
past_records, rep_accounts, search_accounts = [], [], []
today_joined = 0
joined_num = {'max_pt_rank': 0, 'now_pt_rank': 0}
prepare_flag = False

# main_account = [name, token, secret, auth_token]
# rep_accounts = [[name, token, secret], ...]
# search_accounts = [[token, secret], ...]
# name$token$secret$auth_token|name$token$secret|token$secret#token$secret#...

split_tokens = TOKENS.split('|')
main_account = split_tokens[0].split('$')
tokens = split_tokens[1].split("#")
for account in tokens:
    rep_accounts.append(account.split("$"))
tokens = split_tokens[2].split("#")
for account in tokens:
    search_accounts.append(account.split("$"))

CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET = API_KEYS.split("|")[:4]
oauth1 = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
consumer_key, consumer_secret, kdt, x_twitter_client_adid, x_client_uuid, x_twitter_client_deviceid = ANDROID_AUTH.split("|")

android_headers = {
    'Host': 'api.twitter.com',
    'Timezone': 'Asia/Tokyo',
    'Os-Security-Patch-Level': '2021-08-05',
    'Optimize-Body': 'true',
    'Accept': 'application/json',
    'X-Twitter-Client': 'TwitterAndroid',
    'X-Attest-Token': 'no_token',
    'User-Agent': 'TwitterAndroid/10.53.2-release.0 (310532000-r-0)',
    'X-Twitter-Client-Adid': x_twitter_client_adid,
    'X-Twitter-Client-Language': 'en-US',
    'X-Client-Uuid': x_client_uuid,
    'X-Twitter-Client-Deviceid': x_twitter_client_deviceid,
    'X-Twitter-Client-Version': '10.53.2-release.0',
    'Cache-Control': 'no-store',
    'X-Twitter-Active-User': 'yes',
    'X-Twitter-Api-Version': '5',
    'Kdt': kdt,
    'X-Twitter-Client-Limit-Ad-Tracking': '0',
    'Accept-Language': 'en-US',
    'X-Twitter-Client-Flavor': ''
}


def print_log():
    logs = driver.get_log('browser')
    for log in logs:
        if all(k in log for k in ['message', 'timestamp']) and not any(x in log['message'] for x in ['Please make sure it has an appropriate', 'keyregistry', 'live_pipeline', 'all.json']):
            print(datetime.datetime.fromtimestamp(log['timestamp'] / 1000))
            print(log)
            print()

def TweetIdTime(id):
    """ツイートIDを投稿時刻に変換"""
    return datetime.datetime.fromtimestamp(((id >> 22) + 1288834974657) / 1000.0)

def js_geturl(graphql_id):
    return """
    function get_queryid(name, defaultId) {
        try {
            let queryids = webpackChunk_twitter_responsive_web;
            for (let i = 0; i < queryids.length; i++) {
                for (let key in queryids[i][1]) {
                    try {
                        if (queryids[i][1][key].length === 1) {
                            let tmp = {};
                            queryids[i][1][key](tmp);
                            if (tmp.exports.operationName === name) return tmp.exports.queryId;
                        }
                    } catch { }
                }
            }
            return defaultId;
        } catch {
            return defaultId;
        }
    }
    let queryid = get_queryid('"""+graphql_id+"""', '')
    let url = 'https://x.com/i/api/graphql/' + queryid + '/"""+graphql_id+"""';
    """

def js_setxhr(method = 'POST'):
    js = """
    var cookie = document.cookie.replaceAll(" ", "").split(";");
    var token = "";
    cookie.forEach(function (value) {
        let content = value.split('=');
        if (content[0] == "ct0") token = content[1];
    })
    var xhr = new XMLHttpRequest();
    xhr.open('""" + method + """', url);
    xhr.setRequestHeader('Authorization', 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA');
    xhr.setRequestHeader('x-csrf-token', token);
    xhr.setRequestHeader('x-twitter-active-user', 'yes');
    xhr.setRequestHeader('x-twitter-auth-type', 'OAuth2Session');
    xhr.setRequestHeader('x-twitter-client-language', 'ja');
    xhr.withCredentials = true;
    """
    if method == 'POST': js += "xhr.setRequestHeader('Content-Type', 'application/json');"
    return js

def request_php(url, data = None):
    for attempt in range(5):
        try:
            if data != None:
                response = requests.post(PHP_URL + url + '.php', headers={'Content-Type': 'application/json'}, data=json.dumps(data))
                return response
            else:
                response = requests.get(PHP_URL + url + '.php')
                return response.json()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < 5 - 1:
                print(f"Retrying in {60} seconds...")
                time.sleep(60)
            else:
                print("All attempts failed.")
                return None


def prepare_main():
    """メインのアカウントの準備"""

    def login_twitter(auth_token):
        """Twitterにログインする"""

        driver.get('https://x.com/i/flow/login')
        driver.maximize_window()
        element = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.NAME, 'text')))
        time.sleep(1)
        cookie = {
                'name': 'auth_token',
                'value': auth_token,
                'domain': '.x.com',
                'path': '/'
        }
        driver.add_cookie(cookie)
        time.sleep(1)
        driver.get('https://x.com')
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[role=textbox]')))

    def get_request_body(url, graphql_id):
        """graphqlのxhr用のbodyを取得する"""

        request_body[graphql_id] = {}
        driver.get(url)
        for _ in range(5):
            time.sleep(5)
            for request in driver.requests:
                if request.response:
                    if graphql_id in request.url and 'graphql' in request.url:
                        request_body[graphql_id + '_url'] = request.url.split('?')[0]
                        if request.body != b'':
                            body = json.loads(request.body)
                            time.sleep(0.5)
                            if 'variables' in body:
                                request_body[graphql_id] = body
                                break
                        else:
                            body = request.params
                            if 'variables' in body:
                                for key in body:
                                    body[key] = json.loads(body[key])
                                time.sleep(0.5)
                                request_body[graphql_id] = body
                                break
            if request_body[graphql_id] != {}:
                print('SET ' + graphql_id)
                time.sleep(1)
                break
        else:
            print('CANNOT SET ' + graphql_id)

    def get_request_body2(url, json_url):
        """非graphqlのxhr用のbodyを取得する"""

        json_name = json_url.split('.')[0]
        request_body[json_name] = {}
        driver.get(url)
        for _ in range(5):
            time.sleep(5)
            for request in driver.requests:
                if request.response:
                    if json_url in request.url:
                        request_body[json_name + '_url'] = request.url.split('?')[0]
                        if request.body != b'': request_body[json_name] = json.loads(request.body)
                        else: request_body[json_name] = request.params
                        print('SET ' + json_name)
                        break
            if request_body[json_name] != {}:
                time.sleep(1)
                break
        else:
            print('CANNOT SET ' + json_name)

    def interceptor(request):
        """APIのlimitを食うものを阻害"""

        BLOCK_URLS = [
            "https://x.com/i/api/2/notifications/all.json"
        ]
        if any([request.url.find(bloc_url) != -1 for bloc_url in BLOCK_URLS]):
            request.abort()

    def interceptor2(request):
        """CreateTweetを盗聴"""

        global request_header
        BLOCK_URLS = [
            "CreateTweet"
        ]
        if any([request.url.find(bloc_url) != -1 for bloc_url in BLOCK_URLS]):
            request.abort()
            request_body['CreateTweet'] = json.loads(request.body)
            request_body['CreateTweet_url'] = request.url.split('?')[0]
            request_header = dict(request.headers)
            if 'x-client-transaction-id' in request_header: del request_header['x-client-transaction-id']
            if 'Accept-Encoding' in request_header: del request_header['Accept-Encoding']
            driver.request_interceptor = interceptor
            print('SET CreateTweet')

    def get_tweet_request_body():
        """ツイートのxhr用のbodyを取得する"""

        driver.get('https://x.com/home')
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[role=textbox]')))
        time.sleep(1)
        element_box = driver.find_element(By.CSS_SELECTOR, '[role=textbox]')
        element_box.send_keys('working')
        driver.request_interceptor = interceptor2
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR, '[data-testid=tweetButtonInline]').click()

    for _ in range(5):
        try:
            driver.request_interceptor = interceptor
            get_request_body('https://x.com/user/status/1', 'TweetResultByRestId')
            login_twitter(main_account[3])
            get_request_body('https://x.com/home', 'Timeline')
            get_request_body('https://x.com/intent/user?user_id=1', 'UserByRestId')
            get_request_body2('https://x.com/notifications/mentions', 'mentions.json')
            get_request_body('https://x.com/search?q=' + KEYWORD + '&src=typed_query&f=live', 'SearchTimeline')
            get_tweet_request_body()
        except Exception as e:
            traceback.print_exc()
            time.sleep(2)
        else:
            break


def create_tweet(text, oauth_token, token_secret, rep_id = None):
    """Androidクライアントでのツイート"""

    url = 'https://api.twitter.com/graphql/B8zcLvy-DN84y11pB2NObA/CreateTweet'
    oauth_nonce = ''.join([str(random.randint(0, 9)) for _ in range(32)])
    oauth_timestamp = str(int(time.time()))

    http_method = "POST"
    parameters = {
        "oauth_consumer_key": consumer_key,
        "oauth_token": oauth_token,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": oauth_timestamp,
        "oauth_nonce": oauth_nonce,
        "oauth_version": "1.0"
    }

    parameter_string = '&'.join(f"{urllib.parse.quote(k, '')}={urllib.parse.quote(v, '')}" for k, v in sorted(parameters.items()))
    signature_base_string = f"{http_method}&{urllib.parse.quote(url, '')}&{urllib.parse.quote(parameter_string, '')}"
    signing_key = f"{consumer_secret}&{token_secret}"
    digest = hmac.new(signing_key.encode(), signature_base_string.encode(), hashlib.sha1).digest()
    oauth_signature = base64.b64encode(digest).decode()
    parameters['oauth_signature'] = oauth_signature

    reply_str = f',"reply":{{"exclude_reply_user_ids":[],"in_reply_to_tweet_id":{rep_id}}}' if rep_id is not None else ''
    json_data = {
        'features': '{"longform_notetweets_inline_media_enabled":true,"super_follow_badge_privacy_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"super_follow_user_api_enabled":true,"super_follow_tweet_api_enabled":true,"articles_api_enabled":true,"android_graphql_skip_api_media_color_palette":true,"creator_subscriptions_tweet_preview_api_enabled":true,"freedom_of_speech_not_reach_fetch_enabled":true,"tweetypie_unmention_optimization_enabled":true,"longform_notetweets_consumption_enabled":true,"subscriptions_verification_info_enabled":true,"blue_business_profile_image_shape_enabled":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"immersive_video_status_linkable_timestamps":true,"super_follow_exclusive_tweet_notifications_enabled":true}',
        'variables': '{"nullcast":false,"includeTweetImpression":true,"includeHasBirdwatchNotes":false,"includeEditPerspective":false,"includeEditControl":true,"includeCommunityTweetRelationship":false' + reply_str + ',"includeTweetVisibilityNudge":true,"tweet_text":"' + text + '"}'
    }
    json_bytes = json.dumps(json_data).encode('utf-8')
    gzip_buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=gzip_buffer, mode='wb') as f:
        f.write(json_bytes)
    gzip_data = gzip_buffer.getvalue()

    post_headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Authorization': 'OAuth realm="http://api.twitter.com/", ' + ', '.join(f'{urllib.parse.quote(k)}="{urllib.parse.quote(v)}"' for k, v in parameters.items()),
        'Content-Encoding': 'gzip',
        'Content-Type': 'application/json',
        'Content-Length': str(len(gzip_data))
    }
    headers = {**android_headers, **post_headers}
    response = requests.post(url, headers=headers, data=gzip_data)
    return response

def search_timeline(text, oauth_token, token_secret, cursor = None):
    """Androidクライアントでの検索"""

    url = 'https://api.twitter.com/graphql/4NfkwyiViTLQw7ZcJmxtKg/SearchTimeline'
    oauth_nonce = ''.join([str(random.randint(0, 9)) for _ in range(32)])
    oauth_timestamp = str(int(time.time()))
    cursor_param = f'cursor%22%3A%22{cursor}%22%2C%22' if cursor is not None else ''

    http_method = "GET"
    parameters = {
        "oauth_consumer_key": consumer_key,
        "oauth_token": oauth_token,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": oauth_timestamp,
        "oauth_nonce": oauth_nonce,
        "oauth_version": "1.0",
        'variables': "%7B%22" + cursor_param + "includeTweetImpression%22%3Atrue%2C%22query_source%22%3A%22typed_query%22%2C%22includeHasBirdwatchNotes%22%3Afalse%2C%22includeEditPerspective%22%3Afalse%2C%22includeEditControl%22%3Atrue%2C%22query%22%3A%22" + urllib.parse.quote(text) + "%22%2C%22timeline_type%22%3A%22Latest%22%7D",
        'features': "%7B%22longform_notetweets_inline_media_enabled%22%3Atrue%2C%22super_follow_badge_privacy_enabled%22%3Atrue%2C%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C%22super_follow_user_api_enabled%22%3Atrue%2C%22unified_cards_ad_metadata_container_dynamic_card_content_query_enabled%22%3Atrue%2C%22super_follow_tweet_api_enabled%22%3Atrue%2C%22articles_api_enabled%22%3Atrue%2C%22android_graphql_skip_api_media_color_palette%22%3Atrue%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Atrue%2C%22tweetypie_unmention_optimization_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22subscriptions_verification_info_enabled%22%3Atrue%2C%22blue_business_profile_image_shape_enabled%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Atrue%2C%22immersive_video_status_linkable_timestamps%22%3Atrue%2C%22super_follow_exclusive_tweet_notifications_enabled%22%3Atrue%7D"
    }

    parameter_string = '&'.join(f"{k}={v}" for k, v in sorted(parameters.items()))
    signature_base_string = f"{http_method}&{urllib.parse.quote(url, '')}&{urllib.parse.quote(parameter_string, '')}"
    signing_key = f"{consumer_secret}&{token_secret}"

    digest = hmac.new(signing_key.encode(), signature_base_string.encode(), hashlib.sha1).digest()
    oauth_signature = base64.b64encode(digest).decode()
    parameters['oauth_signature'] = oauth_signature

    url += '?variables=' + parameters['variables'] +'&features=' + parameters['features']
    del parameters['variables']
    del parameters['features']
    headers = {**android_headers, **{'Authorization': 'OAuth realm="http://api.twitter.com/", ' + ', '.join(f'{urllib.parse.quote(k)}="{urllib.parse.quote(v)}"' for k, v in parameters.items())}}
    response = requests.get(url, headers=headers)
    return response

def tweet_from_main(payload):
    """メインアカウントでのツイート"""

    print('tweet at ', datetime.datetime.now())
    tweet_response = oauth1.post('https://api.twitter.com/2/tweets', json=payload, headers={'Content-Type': 'application/json'})

twcount = 0 #返信用アカウント振り分け用カウンター

def reply(text, rep_id):
    """ツイート（サブ垢）"""

    global twcount
    twcount += 1
    index = twcount % (len(rep_accounts) + 1)
    if index == len(rep_accounts):
        print('reply ' + main_account[0] + ' at ', datetime.datetime.now())
        response = create_tweet(text, main_account[1], main_account[2], rep_id)
        response_json = response.json()
        if response.status_code != 200 or 'errors' in response_json:
            print(response_json)
    else:
        print('reply ' + rep_accounts[index][0] + ' at ', datetime.datetime.now())
        response = create_tweet(text, rep_accounts[index][1], rep_accounts[index][2], rep_id)
        response_json = response.json()
        if response.status_code != 200 or 'errors' in response_json:
            print(response_json)
            if 'errors' in response_json:
                response = create_tweet(text, main_account[1], main_account[2], rep_id)
                response_json = response.json()
                if response.status_code != 200 or 'errors' in response_json:
                    print(response_json)


idlist = [] #返信済みのツイートID

def receive(reps):
    """メンションを受け取ったとき"""

    def get_kyui(pt):
        if pt < 500: rank = 'E'
        elif pt < 1000: rank = 'E+'
        elif pt < 1500: rank = 'D'
        elif pt < 2000: rank = 'D+'
        elif pt < 2500: rank = 'C'
        elif pt < 3000: rank = 'C+'
        elif pt < 3500: rank = 'B'
        elif pt < 4000: rank = 'B+'
        elif pt < 4500: rank = 'A'
        elif pt < 5000: rank = 'A+'
        elif pt < 5500: rank = 'S1'
        elif pt < 6000: rank = 'S2'
        elif pt < 6500: rank = 'S3'
        elif pt < 7000: rank = 'S4'
        elif pt < 7500: rank = 'S5'
        elif pt < 8000: rank = 'S6'
        elif pt < 8500: rank = 'S7'
        elif pt < 9000: rank = 'S8'
        elif pt < 9500: rank = 'S9'
        else: rank = 'RoR'
        return rank

    def get_rank(key, name):
        """ランク返信文章生成"""

        if prepare_flag: return 'ランキングは準備中です\\nしばらくお待ちください'
        if key in records_rank:
            d = records_rank[key]
            def s(key): return f"{round(d[key], 2):.2f}"
            rep_text2 = '\\n参考記録: ' + s('refer_pt') if d['now_pt'] != d['refer_pt'] else ''
            rank, rank2 = get_kyui(d['max_pt']), get_kyui(d['now_pt'])
            return name + f"\\n\\n級位: {rank}\\n　最高pt: {s('max_pt')}\\n　歴代: {d['max_pt_rank']} / {str(joined_num['max_pt_rank'])}\\n　現在pt: {s('now_pt')} ({rank2}帯)\\n　世界ランク: {d['now_pt_rank']} / {str(joined_num['now_pt_rank'])}{rep_text2}\\n1s以内出場数: {str(d['count'])}\\n自己ベスト: {d['best']} ({str(d['best_count'])}回)\\n戦績: 🥇×{str(d['f'])} 🥈×{str(d['s'])} 🥉×{str(d['t'])} 📋×{str(d['rankin'])}"
        return name + f"\\n\\n最高pt: -\\n歴代: - / {str(joined_num['max_pt_rank'])}\\n現在pt: -\\n世界ランク: - / {str(joined_num['now_pt_rank'])}\\n1s以内出場数: 0\\n自己ベスト: -\\n戦績: 🥇×0 🥈×0 🥉×0 📋×0"

    def has_rank(key, name, data):
        """ランクを要求しているか判定"""
        """return ランク返信文章 or False"""

        text = data['full_text'].lower()
        mentions = data['entities']['user_mentions']
        for user in mentions: text = text.replace('@' + user['screen_name'].lower(), '')
        if any(x in text for x in ['ランク', 'ﾗﾝｸ', 'らんく', 'rank', 'ランキング', 'ﾗﾝｷﾝｸﾞ']): return get_rank(key, name)
        return False

    def get_result(key, name):
        """当日の結果返信文章生成"""

        previous = datetime.datetime.now() - datetime.timedelta(hours=3, minutes=33)
        if prepare_flag: return 'ランキングは準備中です\\nしばらくお待ちください'
        if key in today_result: return name + f"\\n\\n{previous.date().strftime('%Y/%m/%d')}の334結果\\nresult: +{today_result[key][1]} [sec]\\nrank: {str(today_result[key][0])} / {str(today_joined)}"
        return name + f"\\n\\n{previous.date().strftime('%Y/%m/%d')}の334結果\\nresult: DQ\\nrank: DQ / {str(today_joined)}"

    follow_queue_ids = [] #フォロー待ちのユーザーID

    def following(id):
        """フォローする"""

        nonlocal follow_queue_ids
        driver.execute_script("""
        if (window.following === undefined) window.following = {};
        var id = arguments[0];
        window.following[id] = "";
        var url = "https://x.com/i/api/1.1/friendships/create_all.json?user_id=" + id;
        """ + js_setxhr() + """
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4) {
                if (xhr.status == 200) window.following[id] = true;
                else window.followed[id] = false;
            }
        }
        xhr.send();
        """, id)
        while True:
            time.sleep(0.1)
            res = driver.execute_script('return window.following["' + id + '"]')
            if res != '':
                driver.execute_script('window.following["' + id + '"] = ""')
                follow_queue_ids.remove(id)
                return res

    def follow_request(data, mentions = []):
        """フォローリクエスト"""
        """return フォローした or ランク返信文章 or False"""

        nonlocal follow_queue_ids
        user = data['user']
        user_id = user['id_str']
        text = data['full_text'].lower()
        for mention in mentions:
            text = text.replace('@' + mention['screen_name'].lower(), '')
        if any(x in text for x in ['ふぉろー', 'フォロー', 'follow', 'ふぉろば', 'フォロバ']):
            if any(x in text for x in ['してもいいですか', 'しても大丈夫ですか']): return False
            if 'following' in user and user['following']: return '既にフォローしています'
            else:
                print('フォロー : ' + user['name'] + '  @' + user['screen_name'])
                if user_id in follow_queue_ids: return False
                follow_queue_ids.append(user_id)

                driver.execute_script("""
                if (window.followed === undefined) window.followed = {};
                var id = arguments[2];
                window.followed[id] = "";
                var data = arguments[0];
                data.variables.userId = id;
                var url2 = arguments[1].split("?")[0];
                var url = url2 + "?" + Object.entries(data).map((e) => { return `${e[0].replaceAll("%22", "")}=${encodeURIComponent(JSON.stringify(e[1]))}` }).join("&");
                """ + js_setxhr('GET') + """
                xhr.onreadystatechange = function () {
                    if (xhr.readyState == 4) {
                        if (xhr.status == 200) {
                            try {
                                out = JSON.parse(xhr.responseText);
                                if ("followed_by" in out.data.user.result.legacy) {
                                    if (out.data.user.result.legacy.followed_by) window.followed[id] = 1;
                                    else window.followed[id] = 2;
                                } else window.followed[id] = 2;
                            } catch (e) {
                                console.error(e);
                                window.followed[id] = 3;
                            }
                        } else window.followed[id] = 3;
                    }
                }
                xhr.send();
                """, request_body['UserByRestId'], request_body['UserByRestId_url'], user_id)
                while True:
                    time.sleep(0.1)
                    res = driver.execute_script('return window.followed["' + user_id + '"]')
                    if res != '':
                        driver.execute_script('window.followed["' + user_id + '"] = ""')
                        if res == 1:
                            if following(user_id): return 'フォローしました'
                            else: return 'エラーが発生しました🙇\\n時間をおいてもう一度お試しください'
                        else:
                            follow_queue_ids.remove(user_id)
                            if res == 2: return '334Rankerをフォローしてからお試しください'
                            return 'エラーが発生しました🙇\\n時間をおいてもう一度お試しください'

        else: return has_rank(user_id, '@ ' + user['screen_name'], data)


    global idlist
    rep_accounts_ids = [main_account[1].split('-')[0]] + [account[1].split('-')[0] for account in rep_accounts]
    for rep in reps:
        data = rep['status']['data']
        user = data['user']
        mentions = data['entities']['user_mentions']
        if user['id_str'] not in rep_accounts_ids and data['id_str'] not in idlist:
            rep_text = False
            idlist.append(data['id_str'])
            if 'in_reply_to_status_id_str' not in data or data['in_reply_to_status_id_str'] == None:
                rep_text = follow_request(data, mentions) #リプライ先がリプライでない場合
                if not rep_text: rep_text = get_result(user['id_str'], user['screen_name'])
            else: #リプライ先がリプライの場合
                if data['in_reply_to_user_id_str'] in rep_accounts_ids: rep_text = follow_request(data, mentions) #Rankerへのリプライの場合
                else: #Ranker以外へのリプライの場合
                    user_id = data['in_reply_to_user_id_str']
                    user_name = ''
                    text_range = data['display_text_range']
                    flag = False 
                    for user2 in mentions:
                        if user2["id_str"] in rep_accounts_ids and text_range[0] <= user2["indices"][0] and user2["indices"][1] <= text_range[1]: flag = True
                        if user2["id_str"] == user_id: user_name = user2["name"]
                    if flag:
                        if user_name == '':
                            if user_id == user['id_str']: user_name = '@ ' + data['in_reply_to_screen_name']
                            if user_name == '': user_name = '@ ' + data['in_reply_to_screen_name']
                        rep_text = has_rank(user_id, user_name, data)
                        if not rep_text:
                            d = TweetIdTime(int(data['in_reply_to_status_id_str']))
                            rep_text = "ツイート時刻：" + f'{d.hour:02d}:{d.minute:02d}:{d.second:02d}.{int(d.microsecond / 1000):03d}'
            if rep_text:
                print(user['name'])
                threading.Thread(target=reply, args=(rep_text, data['id_str'],)).start()



def get_mention_from_notion(since, end):
    """通知欄からメンションを取得"""

    screen_names = [main_account[0]] + [account[0] for account in rep_accounts]

    while True:
        if since < datetime.datetime.now():
            driver.execute_script("""
var cookie = document.cookie.replaceAll(" ", "").split(";");
var token = "";
cookie.forEach(function (value) {
    let content = value.split('=');
    if (content[0] == "ct0") token = content[1];
});
function setheader(xhr) {
    xhr.setRequestHeader('Authorization', 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA');
    xhr.setRequestHeader('x-csrf-token', token);
    xhr.setRequestHeader('x-twitter-active-user', 'yes');
    xhr.setRequestHeader('x-twitter-auth-type', 'OAuth2Session');
    xhr.setRequestHeader('x-twitter-client-language', 'ja');
    xhr.withCredentials = true;
}
window.adaptive = [];
let from = new Date(arguments[0] * 1000),
    until = new Date(arguments[1] * 1000),
    screen_names = arguments[4],
    refresh = "",
    param = "?" + Object.entries(arguments[3]).map((e) => { return `${e[0]}=${encodeURIComponent(JSON.stringify(e[1]))}` }).join("&").replaceAll("%22", ""),
    not = setInterval(function (arguments) {
        if (until < new Date()) clearInterval(not);
        get_notifications("&cursor=" + refresh, arguments);
    }, 5000, arguments);
function get_notifications(cursor, arguments) {
    try {
        let xhr = new XMLHttpRequest();
        let url = arguments[2].split("?")[0] + param + cursor;
        xhr.open('GET', url);
        get_tweets(cursor, xhr);
    } catch(e) {
        console.error("err at mention: ", error.message);
    }
}
function get_tweets(cursor, xhr) {
    setheader(xhr);
    xhr.send();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            let res = JSON.parse(xhr.responseText);
            let tweets = res.globalObjects.tweets;
            let users = res.globalObjects.users;
            let timelines = res.timeline.instructions;
            let timeline = [];
            for (let j = 0; j < timelines.length; j++) {
                if ("addEntries" in timelines[j]) timeline = timeline.concat(timelines[j].addEntries.entries);
                else if ("replaceEntry" in timelines[j]) timeline.push(timelines[j].replaceEntry.entry);
            }
            for (let i = 0; i < timeline.length; i++) {
                try {
                    if (!timeline[i].entryId.includes("cursor")) {
                        let id = timeline[i].content.item.content.tweet.id;
                        let tweet = tweets[id];
                        if (screen_names.every(str => !tweet.full_text.toLowerCase().includes(str))) continue;
                        if (new Date(tweet.created_at) < from) continue;
                        if (until <= new Date(tweet.created_at)) {
                            clearInterval(not);
                            continue;
                        }
                        tweet["user"] = users[tweet.user_id_str];
                        let status = {
                            "status": {
                                "data": tweet
                            }
                        }
                        window.adaptive.push(status);
                    }
                    else if (timeline[i].entryId.includes("top")) refresh = timeline[i].content.operation.cursor.value;
                } catch { }
            }
        }
    }
}
""", int(since.timestamp()), int(end.timestamp()), request_body['mentions_url'], request_body['mentions'], screen_names)
            while True:
                time.sleep(0.01)
                out = driver.execute_script("""
    let adaptive = JSON.parse(JSON.stringify(window.adaptive));
    window.adaptive = [];
    return adaptive;
                """)
                if out != []:
                    threading.Thread(target=receive, args=(out,)).start()
                else:
                    if end + datetime.timedelta(seconds=20) < datetime.datetime.now():
                        print_log()
                        break
            break
        time.sleep(0.01)

def get_mention_from_search(start, end, counter = 1):
    """検索からメンションを取得"""

    index = counter % len(search_accounts)
    until = start + datetime.timedelta(seconds = counter)
    def convert(data):
        instructions = data['data']['search']['timeline_response']['timeline']['instructions']
        screen_names = [f'@{main_account[0]}'] + [f'@{account[0]}' for account in rep_accounts]
        out = []
        for instruction in instructions:
            if 'entries' in instruction: entries = instruction['entries']
            elif 'entry' in instruction: entries = [instruction['entry']]
            else: continue
            for entry in entries:
                if 'promoted' in entry['entryId'] or 'cursor' in entry['entryId']: continue
                try:
                    res = entry['content']['content']['tweetResult']['result']
                    if 'tweet' in res:
                        res = res['tweet']
                    legacy = res['legacy']
                    legacy['id_str'] = res['rest_id']
                    if start <= TweetIdTime(int(legacy['id_str'])) <= end:
                        if not any(element in legacy['full_text'].lower() for element in screen_names): continue
                        legacy['user'] = res['core']['user_result']['result']['legacy']
                        out.append({'status': {'data': legacy}})
                except Exception as e:
                    traceback.print_exc()
        receive(out)

    while True:
        if until < datetime.datetime.now():
            if until + datetime.timedelta(seconds = 1) <= end:
                threading.Thread(target=get_mention_from_search, args=(start, end, counter + 1,)).start()

            text = f'@{main_account[0]} -filter:retweets -from:{main_account[0]} ' + ' '.join([f'-from:{account[0]}' for account in rep_accounts])
            response = search_timeline(text, search_accounts[index][0], search_accounts[index][1])
            try:
                response_json = response.json()
                if 'data' in response_json:
                    convert(response_json)
                else:
                    print(datetime.datetime.now(), f'Search Error occurred at index {index} : {response_json}')
            except:
                print(datetime.datetime.now(), f'Search Error occurred at index {index}', response)

            break
        time.sleep(0.01)



def make_world_rank():
    """級位ポイント計算"""

    def sort_and_rank(input, output, records):
        """ソートして順位をつける"""

        global joined_num
        sorted_items = sorted(records.items(), key=lambda item: item[1][input], reverse=True)
        current_rank = 1
        previous_value = None
        index = 0
        for i, (key, value) in enumerate(sorted_items):
            if value[input] == 0:
                records[key][output] = '-'
                continue
            index += 1
            if value[input] != previous_value: current_rank = index
            records[key][output] = str(current_rank)
            previous_value = value[input]
        joined_num[output] = index

    def time_to_point(date, result):
        """タイムをポイントに変換"""

        days = (datetime.datetime.now() - date).days
        b = 10000 * 2 ** (-10 * float(result))
        if days >= 30: b *= (91 - days) / 61
        return b

    user_data = defaultdict(lambda: {'valid': [], 'all': []})
    for entry in past_records:
        userid, date, value, source = entry
        transformed_value = time_to_point(date, value)
        user_data[userid]['all'].append(transformed_value)
        if source in clients: user_data[userid]['valid'].append(transformed_value)

    def get_top_10(values):
        top_values = sorted(values, reverse=True)[:10]
        while len(top_values) < 10:
            top_values.append(0)
        return top_values

    top_values = {}
    for userid, entries in user_data.items():
        top_valid_values = get_top_10(entries['valid'])
        top_all_values = get_top_10(entries['all'])
        top_values[userid] = {
            'valid': top_valid_values,
            'all': top_all_values
        }

    for id in records_rank:
        if id in top_values:
            records_rank[id]['now_pt'] = sum(top_values[id]['valid']) / 10
            if records_rank[id]['max_pt'] < records_rank[id]['now_pt']: records_rank[id]['max_pt'] = records_rank[id]['now_pt']
            records_rank[id]['refer_pt'] = sum(top_values[id]['all']) / 10
        else:
            records_rank[id]['now_pt'] = 0
            records_rank[id]['refer_pt'] = 0

    sort_and_rank('max_pt', 'max_pt_rank', records_rank)
    sort_and_rank('now_pt', 'now_pt_rank', records_rank)



def make_ranking(results_dict_arr, _driver):
    """当日分のランキングの作成"""

    def make_month_rank():
        month_record, month_source = {}, {}
        n = datetime.datetime.now()
        month_days = calendar.monthrange(n.year, n.month)[1]
        response = request_php('get')
        for record in response:
            record_time = datetime.datetime.strptime(record['date'], '%Y-%m-%d') + datetime.timedelta(hours=TIME334[0], minutes=TIME334[1])
            days = (datetime.datetime.now() - record_time).days
            if days < month_days and record['source'] in clients:
                id = record['userid']
                if id not in month_record:
                    month_record[id], month_source[id] = [], []
                pt = 10000 * 2 ** (-10 * float(record['result']))
                if len(month_record[id]) < 10:
                    month_record[id].append(pt)
                elif min(month_record[id]) < pt:
                    month_record[id].remove(min(month_record[id]))
                    month_record[id].append(pt)
                month_source[id].append(record['source'])

        month_data = []
        for id in month_record:
            month_data.append([id, sum(month_record[id]) / 10])
        sorted_items = sorted(month_data, key=lambda x: x[1], reverse=True)
        rankdata = []
        current_rank = 1
        previous_value = None
        index = 0
        for value in sorted_items:
            index += 1
            if index > 30: break
            if value[1] != previous_value: current_rank = index
            params = copy.deepcopy(request_body['UserByRestId'])
            params['variables']['userId'] = value[0]
            for key in params:
                params[key] = json.dumps(params[key])
            counter = Counter(month_source[value[0]])
            headers = { "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA" }
            try:
                response = requests.get(request_body['UserByRestId_url'].replace('x.com/i/api', 'api.x.com'), params=params, headers=headers)
                legacy = response.json()['data']['user']['result']['legacy']
                name = legacy['name']
                if name == '': name = '@' + legacy['screen_name']
                rankdata.append([current_rank, legacy['profile_image_url_https'], legacy['name'], value[1], len(month_source[value[0]]), counter.most_common(1)[0][0]])
            except:
                rankdata.append([current_rank, '', 'unknown', value[1], len(month_source[value[0]]), counter.most_common(1)[0][0]])
            previous_value = value[1]

        _driver.get(HTML_URL2)
        wait = WebDriverWait(_driver, 20).until(EC.alert_is_present())
        Alert(_driver).accept()
        for _ in range(5):
            try:
                _driver.execute_script('document.getElementById("input").value = arguments[0]; start();', str(rankdata))
                wait = WebDriverWait(_driver, 20).until(EC.alert_is_present())
            except Exception as e:
                traceback.print_exc()
                _driver.get(HTML_URL2)
                time.sleep(1)
            else:
                Alert(_driver).accept()
                bin = _driver.execute_script('return window.res')
                print('GET IMG2')
                upload_response = oauth1.post('https://upload.twitter.com/1.1/media/upload.json', data={'media_data': bin})
                media_id = upload_response.json().get('media_id_string')
                payload = {
                    'text': "This month's top 30",
                    'media': {
                        'media_ids': [media_id]
                    }
                }
                print("POST RANK2 :")
                tweet_from_main(payload)
                _driver.quit()
                break

    def retweet(id, screen_name):
        """リツイート"""
        
        payload = {
            'text': "Today's winner https://x.com/" + screen_name + "/status/" + id
        }
        print("RETWEET :")
        tweet_from_main(payload)

    def make_img(tweets):
        """ランキング画像の生成とアップロード"""

        for _ in range(5):
            try:
                _driver.execute_script('document.getElementById("input").value = arguments[0]; start();', tweets)
                wait = WebDriverWait(_driver, 20).until(EC.alert_is_present())
            except Exception as e:
                traceback.print_exc()
                _driver.get(HTML_URL)
                time.sleep(1)
            else:
                Alert(_driver).accept()
                bin = _driver.execute_script('return window.res')
                print('GET IMG')
                upload_response = oauth1.post('https://upload.twitter.com/1.1/media/upload.json', data={'media_data': bin})
                media_id = upload_response.json().get('media_id_string')
                payload = {
                    'text': "Today's top 30",
                    'media': {
                        'media_ids': [media_id]
                    }
                }
                print("POST RANK :")
                tweet_from_main(payload)

                next_day = datetime.datetime.now() + datetime.timedelta(days=1)
                if next_day.day == 1:
                    while prepare_flag:
                        time.sleep(1)
                    make_month_rank()
                else:
                    _driver.quit()
                break
    
    tweet_from_id_gt = ''

    def tweet_from_id(tweet_id):

        nonlocal tweet_from_id_gt
        if tweet_from_id_gt == '':
            headers = { "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36" }
            response = requests.get("https://x.com/?mx=2", headers=headers)
            tweet_from_id_gt = re.findall(r'gt=(.*?);', response.text)[0]
        
        params = copy.deepcopy(request_body['TweetResultByRestId'])
        params['variables']['tweetId'] = tweet_id
        for key in params:
            params[key] = json.dumps(params[key])
        headers = {
            "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
            "x-guest-token": tweet_from_id_gt
        }
        try:
            response = requests.get(request_body['TweetResultByRestId_url'], params=params, headers=headers)
            return response.json()['data']['tweetResult']['result']['source']
        except:
            return 'undefined'


    #生データを扱いやすい形に変換

    global records_rank, today_result, today_joined, prepare_flag
    now = datetime.datetime.now()
    today_str = now.date().strftime('%Y-%m-%d')
    time_334 = datetime.datetime.combine(now.date(), datetime.time(TIME334[0], TIME334[1]))
    joined_users = ['1173558244607852545']
    results_for_img = []
    update_records_rank = []
    update_past_records = []
    results_dict_arr = sorted(results_dict_arr, key=lambda x: int(x['id_str']))
    current_rank = 1
    today_joined = 0
    previous_value = None
    for item in results_dict_arr:
        if item['text'] == KEYWORD and item['user']['id_str'] not in joined_users:
            joined_users.append(item['user']['id_str'])
            result_time = (TweetIdTime(int(item['id_str'])) - time_334).total_seconds()
            if 0 <= result_time < 1:
                result_str = '{:.3f}'.format(result_time)

                img_src = 'https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png'
                if item['user']['profile_image_url_https'] != '': img_src = item['user']['profile_image_url_https']

                if item['source'] == 'undefined': item['source'] = tweet_from_id(item['id_str'])
                match = re.search(r'<a[^>]*>([^<]*)</a>', item['source'])
                source = match.group(1) if match else item['source']

                id = item['user']['id_str']

                results_for_img.append([
                    img_src,
                    item['user']['name'],
                    result_str,
                    source,
                    item['id_str'],
                    '@' + item['user']['screen_name'],
                    id
                ])

                today_joined += 1
                if result_str != previous_value: current_rank = today_joined
                previous_value = result_str
                today_result[id] = [current_rank, result_str]
                if id not in records_rank:
                    records_rank[id] = {
                        'best': result_str,
                        'best_count': 0,
                        'max_pt': 0.0,
                        'count': 0,
                        'f': 0,
                        's': 0,
                        't': 0,
                        'rankin': 0
                    }
                records_rank[id]['count'] += 1
                if result_time < float(records_rank[id]['best']):
                    records_rank[id]['best'] = result_str
                    records_rank[id]['best_count'] = 1
                elif result_time == float(records_rank[id]['best']):
                    records_rank[id]['best_count'] += 1
                match current_rank:
                    case 1:
                        records_rank[id]['f'] += 1
                        threading.Thread(target=retweet, args=(item['id_str'], item['user']['screen_name'],)).start()
                    case 2: records_rank[id]['s'] += 1
                    case 3: records_rank[id]['t'] += 1
                if current_rank <= 30: records_rank[id]['rankin'] += 1

                update_list = list(records_rank[id].values())[:8]
                update_list.insert(0, id)
                update_records_rank.append(update_list)

                past_records.append([id, now, result_str, source])
                update_past_records.append([id, today_str, result_str, source]) #JSONにできるよう文字列に

    print(str(results_for_img))
    threading.Thread(target=make_img, args=(str(results_for_img),)).start()
    
    make_world_rank()
    for update_record in update_records_rank:
        update_record[3] = records_rank[update_record[0]]['max_pt']

    prepare_flag = False

    response = request_php('add_rank', update_records_rank)
    print("Response:", response.status_code, response.text)
    response = request_php('add', update_past_records)
    print("Response:", response.status_code, response.text)



def get334(_driver):

    get334_from_sub_arr = ''
    now = datetime.datetime.now()
    time1 = datetime.datetime(now.year, now.month, now.day, TIME334[0], TIME334[1], 59) - datetime.timedelta(minutes=1)
    time2 = datetime.datetime(now.year, now.month, now.day, TIME334[0], TIME334[1], 1)
    screen_names = f'-from:{main_account[0]} ' + ' '.join([f'-from:{account[0]}' for account in rep_accounts])
    out = []

    def get334_from_sub(cursor):

        def final(arr):
            nonlocal get334_from_sub_arr
            print('GET334 FROM SUB ACCOUNT')
            get334_from_sub_arr = arr

        text = KEYWORD + ' -filter:retweets -filter:quote ' + screen_names + ' since:' + time1.strftime('%Y-%m-%d_%H:%M:%S_JST') + ' until:' + time2.strftime('%Y-%m-%d_%H:%M:%S_JST')
        response = search_timeline(text, rep_accounts[-1][1], rep_accounts[-1][2], cursor)
        response_json = response.json()
        if response.status_code == 200 and 'errors' not in response_json:
            try:
                flag = True
                flag2 = True
                instructions = response_json['data']['search']['timeline_response']['timeline']['instructions']
                for instruction in instructions:
                    if 'entries' in instruction: entries = instruction['entries']
                    elif 'entry' in instruction: entries = [instruction['entry']]
                    else: continue
                    for entry in entries:
                        if "promoted" not in entry['entryId'] and "cursor" not in entry['entryId']:
                            try:
                                flag2 = False
                                res = entry['content']['content']['tweetResult']['result']
                                if 'tweet' in res:
                                    res = res['tweet']
                                legacy = res['legacy']
                                legacy['id_str'] = str(int(res['rest_id']) + 1)
                                
                                if TweetIdTime(int(legacy['id_str'])) < time1:
                                    if "home" in entry['entryId']:
                                        continue
                                    else:
                                        flag = False
                                        final(out)
                                        return
                                legacy['text'] = legacy['full_text']
                                if legacy['text'] != KEYWORD:
                                    continue
                                legacy['source'] = 'undefined'
                                legacy['index'] = int(bin(int(legacy['id_str']))[2:-22], 2) + 1288834974657
                                legacy['user'] = res['core']['user_result']['result']['legacy']
                                out.append(legacy)
                                continue
                            except Exception as e:
                                print(e)
                        
                        if "bottom" in entry['entryId']:
                            flag = False
                            if flag2:
                                final(out)
                            else:
                                get334_from_sub(entry['content']['value'])
                            return
                if flag:
                    final(out)
            except Exception as e:
                traceback.print_exc()
                final(out)
        else:
            print(f'Search 334 Error occurred: {response_json}')
            final(out)


    get_time = datetime.datetime(now.year, now.month, now.day, TIME334[0], TIME334[1], 2)
    while True:
        if get_time < datetime.datetime.now():
            print("GET334 start: ", datetime.datetime.now())
            driver.execute_script("""
window.data = "";
var cookie = document.cookie.replaceAll(" ", "").split(";");
var token = "";
cookie.forEach(function (value) {
    let content = value.split('=');
    if (content[0] == "ct0") token = content[1];
})
let time1 = new Date().setHours(""" + str(TIME334[0]) + """, """ + str(TIME334[1]) + """, 0, 0);

function get_queryid(name, defaultId) {
    try {
        let queryids = webpackChunk_twitter_responsive_web;
        for (let i = 0; i < queryids.length; i++) {
            for (let key in queryids[i][1]) {
                try {
                    if (queryids[i][1][key].length === 1) {
                        let tmp = {};
                        queryids[i][1][key](tmp);
                        if (tmp.exports.operationName === name) return tmp.exports.queryId;
                    }
                } catch { }
            }
        }
        return defaultId;
    } catch {
        return defaultId;
    }
}

var data = arguments[0];
data.variables["cursor"] = "";
data.variables.seenTweetIds = [];
let queryid = get_queryid("HomeLatestTimeline", "");
data.queryId = queryid;
var data2 = arguments[1];
data2.variables["cursor"] = "";
data2.variables["rawQuery"] = '""" + KEYWORD + """ -filter:retweets -filter:quote """ + screen_names + """ since:""" + time1.strftime('%Y-%m-%d_%H:%M:%S_JST') + """ until:""" + time2.strftime('%Y-%m-%d_%H:%M:%S_JST') + """'
let queryid2 = get_queryid("SearchTimeline", "");
var count = 0;
get_tweets(data);
get_tweets2(data2, 0);
setTimeout(function() { get_tweets2(data2, 1) }, 2000);

function setheader(xhr) {
    xhr.setRequestHeader('Authorization', 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA');
    xhr.setRequestHeader('x-csrf-token', token);
    xhr.setRequestHeader('x-twitter-active-user', 'yes');
    xhr.setRequestHeader('x-twitter-auth-type', 'OAuth2Session');
    xhr.setRequestHeader('x-twitter-client-language', 'ja');
    xhr.withCredentials = true;
}

var out = [];
function get_tweets(d) {
    try {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', 'https://x.com/i/api/graphql/' + queryid + '/HomeLatestTimeline');
        setheader(xhr);
        xhr.setRequestHeader('content-type', 'application/json');
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4) {
                console.error("get from timeline");
                if (xhr.status === 200) {
                    try {
                        var flag = true;
                        let entries = JSON.parse(xhr.responseText).data.home.home_timeline_urt.instructions[0].entries;
                        for (let i = 0; i < entries.length; i++) {
                            if (!entries[i].entryId.includes("promoted") && !entries[i].entryId.includes("cursor")) {
                                try {
                                    if (entries[i].entryId.includes("home")) var res = entries[i].content.items[0].item.itemContent.tweet_results.result;
                                    else var res = entries[i].content.itemContent.tweet_results.result;
                                    if ("tweet" in res) res = res.tweet;
                                    let legacy = res.legacy;
                                    if (new Date(legacy.created_at) < time1) {
                                        if (entries[i].entryId.includes("home")) continue;
                                        else {
                                            flag = false;
                                            final(out);
                                            break;
                                        }
                                    }
                                    legacy["text"] = legacy.full_text;
                                    if (legacy.text != '""" + KEYWORD + """') continue;
                                    legacy["source"] = res.source;
                                    legacy["index"] = parseInt(BigInt(legacy.id_str).toString(2).slice(0, -22), 2) + 1288834974657;
                                    legacy["user"] = res.core.user_results.result.legacy;
                                    legacy.user["id_str"] = legacy.user_id_str;
                                    out.push(legacy);
                                    continue;
                                } catch (e) {
                                    console.error(e);
                                }
                            }
                            if (entries[i].entryId.includes("bottom")) {
                                let data3 = Object.assign({}, data);
                                data3.variables.cursor = entries[i].content.value;
                                flag = false;
                                get_tweets3(data3);
                                break;
                            }
                        }
                        if (flag) final(out);
                    } catch (e) {
                        console.error(e);
                        final(out);
                    }
                } else final(out);
            }
        }
        xhr.send(JSON.stringify(d));
    } catch (e) {
        console.error(e);
        final(out);
    }
}

var out2 = [[], []];
function get_tweets2(d, index) {
    try {
        let param = "?" + Object.entries(d).map((e) => {
            return `${e[0].replaceAll("%22", "")}=${encodeURIComponent(JSON.stringify(e[1]))}`
        }).join("&")
        var xhr = new XMLHttpRequest();
        xhr.open('GET', 'https://x.com/i/api/graphql/' + queryid2 + '/SearchTimeline' + param);
        setheader(xhr);
        xhr.setRequestHeader('content-type', 'application/json');
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4) {
                console.error("get from search");
                if (xhr.status === 200) {
                    try {
                        var flag = true;
                        let instructions = JSON.parse(xhr.responseText).data.search_by_raw_query.search_timeline.timeline.instructions;
                        var flag2 = true;
                        loop: for (let j = 0; j < instructions.length; j++) {
                            if ("entries" in instructions[j]) var entries = instructions[j].entries;
                            else if ("entry" in instructions[j]) var entries = [instructions[j].entry];
                            else continue;
                            for (let i = 0; i < entries.length; i++) {
                                if (!entries[i].entryId.includes("promoted") && !entries[i].entryId.includes("cursor")) {
                                    try {
                                        flag2 = false;
                                        var res = entries[i].content.itemContent.tweet_results.result;
                                        if ("tweet" in res) res = res.tweet;
                                        let legacy = res.legacy;
                                        if (new Date(legacy.created_at) < time1) {
                                            if (entries[i].entryId.includes("home")) continue;
                                            else {
                                                flag = false;
                                                final(out2[index]);
                                                break loop;
                                            }
                                        }
                                        legacy["text"] = legacy.full_text;
                                        if (legacy.text != '""" + KEYWORD + """') continue;
                                        legacy["source"] = res.source;
                                        legacy["index"] = parseInt(BigInt(legacy.id_str).toString(2).slice(0, -22), 2) + 1288834974657;
                                        legacy["user"] = res.core.user_results.result.legacy;
                                        legacy.user["id_str"] = legacy.user_id_str;
                                        out2[index].push(legacy);
                                        continue;
                                    } catch (e) {
                                        console.error(e);
                                    }
                                }
                                if (entries[i].entryId.includes("bottom")) {
                                    let data3 = JSON.parse(JSON.stringify(data2));
                                    data3.variables.cursor = entries[i].content.value;
                                    flag = false;
                                    if (flag2) final(out2[index]);
                                    else get_tweets2(data3, index);
                                    break loop;
                                }
                            }
                        }
                        if (flag) final(out2[index]);
                    } catch (e) {
                        console.error(e);
                        final(out2[index]);
                    }
                } else final(out2[index]);
            }
        }
        xhr.send();
    } catch (e) {
        console.error(e);
        final(out2[index]);
    }
}

function final(out6) {
    out = out.concat(out6);
    count++;
    console.log(count)
    console.log(out)
    if (count < 3) return;
    let out5 = []
    let ids = [];
    out.sort((a, b) => a.index - b.index);
    for (let i = 0; i < out.length; i++) {
        if (!ids.includes(out[i].id_str)) {
            out5.push(out[i]);
            ids.push(out[i].id_str);
        }
    }
    window.data = out5;
}
            """, request_body['Timeline'], request_body['SearchTimeline'])
            threading.Thread(target=get334_from_sub, args=(None,)).start()
            while True:
                time.sleep(0.1)
                res = driver.execute_script("return window.data")
                if res != "":
                    print("GET334 conplete: ", datetime.datetime.now())
                    if res != []:
                        while get334_from_sub_arr == '':
                            time.sleep(0.01)
                        make_ranking(res + get334_from_sub_arr, _driver)
                    break
            break
        time.sleep(0.01)



def notice():
    global today_result, prepare_flag
    today = datetime.datetime.now().date()
    notice_time = datetime.datetime.combine(today, datetime.time(TIME334[0], TIME334[1])) - datetime.timedelta(minutes=2)
    while True:
        if notice_time < datetime.datetime.now():
            today_result = {}
            prepare_flag = True
            print("NOTICE :")
            threading.Thread(target=tweet_from_main, args=({'text': '334観測中 (' + today.strftime('%Y/%m/%d') + ')'},)).start()
            _driver = {}
            
            for _ in range(5):
                try:
                    options=Options()
                    #options.add_argument('--headless')
                    options.add_argument('--no-sandbox')
                    options.add_argument("--disable-extensions")
                    options.add_argument("--disable-gpu")
                    options.add_argument('--disable-dev-shm-usage')
                    _driver = webdriver.Chrome(options = options)
                    _driver.set_window_size(589, 1)
                    _driver.get(HTML_URL)
                    wait = WebDriverWait(_driver, 20).until(EC.alert_is_present())
                    Alert(_driver).accept()
                except Exception as e:
                    traceback.print_exc()
                    time.sleep(2)
                else:
                    get334(_driver)
                    break
            break
        time.sleep(5)


def main():

    now = datetime.datetime.now()
    base_time = datetime.datetime(now.year, now.month, now.day, TIME334[0], TIME334[1], 0) - datetime.timedelta(minutes=34)

    times = []
    for i in range(6):
        start_time = base_time + datetime.timedelta(hours=i * 4)
        end_time = start_time + datetime.timedelta(hours=4)
        times.append([start_time, end_time])

    times[-1][1] = base_time + datetime.timedelta(days=1)
    times.append([base_time + datetime.timedelta(days=1), base_time + datetime.timedelta(days=1)])

    for i in range(len(times)):
        if now < times[i][0]:
            start_time = times[i][0]
            end_time = times[i][1]
            if len(sys.argv) != 1:
                print('TEST MODE')
                start_time = '???'
                end_time = times[i][0]

            print(start_time, end_time)


            global past_records, today_result, today_joined, records_rank
            today_unsorted = []
            response = request_php('get')
            for record in response:
                record_time = datetime.datetime.strptime(record['date'], '%Y-%m-%d') + datetime.timedelta(hours=TIME334[0], minutes=TIME334[1])
                days = (datetime.datetime.now() - record_time).days
                if days <= 91: past_records.append([record['userid'], record_time, record['result'], record['source']])
                if days == 0: today_unsorted.append([record['userid'], record['result']])
            today_unsorted = sorted(today_unsorted, key=lambda x: float(x[1]))
            current_rank = 1
            today_joined = 0
            previous_value = None
            for record in today_unsorted:
                today_joined += 1
                if record[1] != previous_value: current_rank = today_joined
                today_result[record[0]] = [current_rank, record[1]]
                previous_value = record[1]
            
            response = request_php('get_rank')
            for record in response:
                id = record['userid']
                del record['userid']
                record['max_pt'] = float(record['max_pt'])
                records_rank[id] = {key: int(value) if key not in ['best', 'max_pt'] else value for key, value in record.items()}

            make_world_rank()
            print('LOADED RANK')

            global driver
            for _ in range(5):
                try:
                    options=Options()
                    #options.add_argument('--headless')
                    options.add_argument('--no-sandbox')
                    options.add_argument("--disable-extensions")
                    options.add_argument("--disable-gpu")
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--disable-http2')
                    driver = webdriver.Chrome(options = options)
                    driver.set_script_timeout(5)
                    
                except Exception as e:
                    traceback.print_exc()
                    time.sleep(5)
                else:
                    break

            prepare_main()

            if len(sys.argv) != 1:
                start_time = datetime.datetime.now().replace(microsecond = 0) + datetime.timedelta(seconds=3)
            print('START')
            
            threading.Thread(target = get_mention_from_notion, args=(start_time, end_time,)).start()
            threading.Thread(target = get_mention_from_search, args=(start_time, end_time,)).start()
            
            if start_time < datetime.datetime(now.year, now.month, now.day, TIME334[0], TIME334[1], 0) < end_time:
                print('334MODE')
                notice()
                
            break

main()
         