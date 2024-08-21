import copy, datetime, json, os, requests, sys, threading, time, traceback, re, gzip, io, hmac, hashlib, base64, urllib.parse, random
from collections import defaultdict

TIME334 = [3, 34]
KEYWORD = '334'
PHP_URL = os.environ['PHP_URL']
clients = ['Twitter for iPhone',  'Twitter for Android',  'Twitter Web Client',  'TweetDeck',  'TweetDeck Web App',  'Twitter for iPad',  'Twitter for Mac',  'Twitter Web App',  'Twitter Lite',  'Mobile Web (M2)',  'Twitter for Windows',  'Janetter',  'Janetter for Android',  'Janetter Pro for iPhone',  'Janetter for Mac',  'Janetter Pro for Android',  'Tweetbot for iΟS',  'Tweetbot for iOS',  'Tweetbot for Mac',  'twitcle plus',  'ツイタマ',  'ツイタマ for Android',  'ツイタマ+ for Android',  'Sobacha',  'SobaCha',  'Metacha',  'MetaCha',  'MateCha',  'ツイッターするやつ',  'ツイッターするやつγ',  'ツイッターするやつγ pro',  'jigtwi',  'feather for iOS',  'hamoooooon',  'Hel2um on iOS',  'Hel1um Pro on iOS',  'Hel1um on iOS',  'undefined']

BEFORE = 0 ##### 何日前の計測？

records_rank, today_result, driver, request_body, request_header = {}, {}, {}, {}, {}
past_records, rep_accounts = [], []
today_joined = 0
prepare_flag = False


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


def TweetIdTime(id):
    """ツイートIDを投稿時刻に変換"""
    return datetime.datetime.fromtimestamp(((id >> 22) + 1288834974657) / 1000.0)


def make_world_rank():
    """級位ポイント計算"""

    def time_to_point(date, result):
        """タイムをポイントに変換"""

        days = (datetime.datetime.now() - date).days - BEFORE
        b = 10000 * 2 ** (-10 * float(result))
        if days >= 30: b *= (91 - days) / 61
        return b

    user_data = defaultdict(lambda: {'valid': [], 'all': [], 'a': []})
    for entry in past_records:
        userid, date, value, source = entry
        user_data[userid]['a'].append(value)
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


def make_ranking(results_dict_arr, _driver):
    """当日分のランキングの作成"""

    #生データを扱いやすい形に変換

    global records_rank, today_result, today_joined, prepare_flag
    now = datetime.datetime.now() - datetime.timedelta(days=BEFORE, hours=TIME334[0], minutes=TIME334[1])
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
                    case 2: records_rank[id]['s'] += 1
                    case 3: records_rank[id]['t'] += 1
                if current_rank <= 30: records_rank[id]['rankin'] += 1

                update_list = list(records_rank[id].values())[:8]
                update_list.insert(0, id)
                update_records_rank.append(update_list)

                past_records.append([id, now, result_str, source])
                update_past_records.append([id, today_str, result_str, source]) #JSONにできるよう文字列に


    make_world_rank()

    prepare_flag = False

    for update_record in update_records_rank:
        update_record[3] = records_rank[update_record[0]]['max_pt']

    print(update_records_rank)
    print(update_past_records)

    #response = request_php('add_rank', update_records_rank) ##### rankを保存する場合はつける
    #print("Response:", response.status_code, response.text)
    #response = request_php('add', update_past_records) ##### resultを保存する場合はつける
    #print("Response:", response.status_code, response.text)




def main():

    global past_records, today_result, today_joined, records_rank
    today_unsorted = []
    response = request_php('get2') ##### 100日前まで取得用
    for record in response:
        record_time = datetime.datetime.strptime(record['date'], '%Y-%m-%d') + datetime.timedelta(hours=TIME334[0], minutes=TIME334[1])
        days = (datetime.datetime.now() - record_time).days - BEFORE - 1
        if 0 <= days <= 91: past_records.append([record['userid'], record_time, record['result'], record['source']])
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

main()
print("SET")
         

res_a = []

res_b = []
for a in res_a:
    res_b.append({
                'id_str': a[4],
                'text': '334',
                'source': a[3],
                'user': {
                    'id_str': a[6],
                    'name': a[1],
                    'screen_name': a[5][1:],
                    'profile_image_url_https': a[0]
                },

    })

make_ranking(res_b, {})