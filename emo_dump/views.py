import traceback
import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response
import tweepy
import CaboCha


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
        for mod, ref in emo_parse(tweet.text).items():
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
        _chunk_text = chunk_text(tree, i)

        # 対象chunk
        link_chunk = tree.chunk(chunk.link)
        link_token = tree.token(link_chunk.head_pos + link_chunk.token_pos)
        link_chunk_text = chunk_text(tree, chunk.link)

        is_adj_chunk = token.feature.split(',')[0] == "形容詞"
        is_adj_link_chunk = link_token.feature.split(',')[0] == "形容詞"

        # print(_chunk_text, "->",  link_chunk_text)
        # print(is_adj_chunk, is_adj_link_chunk)
        # 形容詞を含んでいるか
        if not is_adj_chunk and not is_adj_link_chunk:
            continue

        if is_adj_chunk:
            emo_list[token.surface] = link_chunk_text
        else:
            emo_list[link_token.surface] = _chunk_text

    return emo_list


def chunk_text(tree, pos, delimiter=''):
    """

    :param tree:
    :param pos:
    :param delimiter: string
    :return: string
    """
    chunk = tree.chunk(pos)
    return delimiter.join([tree.token(i).surface for i in range(chunk.token_pos, chunk.token_pos + chunk.token_size)])
