import traceback
import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response
import tweepy
import CaboCha
import re


def hello(request):
    return HttpResponse('Hello world')


def index(request):
    if 'key' not in request.session:
        return render_to_response('no_login.html')
    # TODO: 動的に デフォルトは認証ユーザ
    target_screen_anme = 'arzzup'
    api = get_api(request.session.get('key'), request.session.get('secret'))
    tweets = api.user_timeline(screen_name=target_screen_anme, count=200, include_rts=False)

    res = analyze_tweets(tweets)

    # limit
    limit = api.rate_limit_status(resources="statuses")
    # 各要素の取り出し
    limit_info = limit['resources']['statuses']['/statuses/user_timeline']
    ts = datetime.datetime.fromtimestamp(int(limit_info['reset']))
    limit_info['time_str'] = ts.strftime('%H:%M:%S')

    return render_to_response('tweet.html', {'res': res.items(), 'tweets': tweets, 'limit_info': limit_info})


def oauth_start(request):
    callback_url = 'http://localhost:8000/auth/end/'.encode('utf-8')
    auth = get_auth(callback_url)
    try:
        auth_url = auth.get_authorization_url()
    except tweepy.TweepError:
        print(traceback.format_exc())
    request.session['request_token'] = auth.request_token
    return HttpResponseRedirect(auth_url)


def oauth_end(request):
    verifier = request.GET.get('oauth_verifier')
    auth = get_auth()
    # request.session.delete('request_token')
    token = request.session.get('request_token')
    auth.request_token = token
    auth.get_access_token(verifier)
    request.session['key'] = auth.access_token
    request.session['secret'] = auth.access_token_secret
    return HttpResponseRedirect('/')


def oauth_clear(request):
    request.session.clear()
    return HttpResponseRedirect('/')


def get_api(token, secret):
    auth = get_auth()
    auth.set_access_token(token, secret)
    return tweepy.API(auth_handler=auth)


def get_auth(callback=None):
    return tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET, callback)


def analyze_tweets(tweets):
    """

    :param tweets:
    :return: dict[string, list[string]]
    """
    results = {}
    for tweet in tweets:
        text = filter_text(tweet.text)
        for mod, ref in emo_parse(text).items():
            if mod not in results:
                results[mod] = []
            results[mod].append(ref)
    return results


def emo_parse(text):
    """
    テキストから嗜好辞書を作成する.
    {対象: 感性, 対象2: 感性2...}
    TODO: 対象の重複による上書きをなくす

    :param text: 解析するテキスト
    :return: dict[string, string]
    """
    cp = CaboCha.Parser()
    # print(cp.parseToString(text))
    tree = cp.parse(text)

    emo_list = {}
    for i in range(tree.chunk_size()):
        chunk = tree.chunk(i)

        # 係っているか
        # NOTE: 汚い
        if chunk.link.real == -1:
            continue

        token = tree.token(chunk.head_pos + chunk.token_pos)
        # TODO: リファクタリング
        _chunk_text = chunk_text(tree, chunk)

        # 対象chunk
        link_chunk = tree.chunk(chunk.link)
        link_token = tree.token(link_chunk.head_pos + link_chunk.token_pos)
        link_chunk_text = chunk_text(tree, link_chunk)

        # 分詞節
        chunk_part = token.feature.split(',')[0]
        link_chunk_part = link_token.feature.split(',')[0]

        # 形容詞節, 名詞節のペアであるか
        if \
           not (chunk_part == "名詞" and link_chunk_part == "形容詞"):
            continue

        chunk_indep = chunk_independant(tree, chunk)
        link_chunk_indep = chunk_independant(tree, link_chunk)

        if chunk_part == "形容詞":
            chunk_indep, link_chunk_indep = link_chunk_indep, chunk_indep

        emo_list[chunk_indep] = link_chunk_indep

    return emo_list


def chunk_independant(tree, chunk):
    """
    自立語のみを返す
    :param chunk:
    :return: string
    """
    text = ''
    for i in range(chunk.token_pos, chunk.token_pos + chunk.token_size):
        token = tree.token(i)
#         print(token.surface)
#         print(token.feature.split(",")[1])
#         print(is_indepenedant(token.feature.split(",")[1]))
#        print()
        if not is_indepenedant(token.feature.split(",")[1]):
            break
        text += token.surface
    return text


def is_indepenedant(part):
    """
    自立語であるかどうか
    :param part:
    :return: True|False
    """
    return part in ["自立", "固有名詞", "数", "一般", "形容動詞語幹", "接尾"]


def chunk_text(tree, chunk, delimiter=''):
    """
    chunk 全体のテキストを返す
    :param tree:
    :param pos:
    :param delimiter: string
    :return: string
    """
    return delimiter.join([tree.token(i).surface for i in range(chunk.token_pos, chunk.token_pos + chunk.token_size)])


def filter_text(text):
    # url 取り除き
    text = re.sub(r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", '', text)
    text = re.sub(r"「.*」", '', text)
    return text


def chunk_text_pos(tree, pos, delimiter=''):
    """
    chunk 全体のテキストを返す
    :param tree:
    :param pos: int
    :param delimiter: string
    :return:
    """
    chunk_text(tree, tree.chunk(pos), delimiter=delimiter)
