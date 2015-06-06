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
    tweets = api.user_timeline(screen_name=target_screen_anme, count=200)
    limit = api.rate_limit_status(resources="statuses")
    # 各要素の取り出し
    limit_info = limit['resources']['statuses']['/statuses/user_timeline']
    ts = datetime.datetime.fromtimestamp(int(limit_info['reset']))
    limit_info['time_str'] = ts.strftime('%H:%M:%S')
    # print(limit_info)
    return render_to_response('tweet.html', {'tweets': tweets, 'limit_info': limit_info})


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
    pass


def analyze_text(text):
    pass


def test(request):
    line = 'プロ生ちゃんかわいい'
    cp = CaboCha.Parser()
    print(cp.parseToString(line))
    tree = cp.parse(line)

    emo_list = {}
    for i in range(tree.chunk_size()):
        chunk = tree.chunk(i)
#        print(chunk.link.numerator)
        if chunk.link.real == -1:
            continue
        link_chunk = tree.chunk(chunk.link)
        link_chunk_str = ",".join([tree.token(i).surface for i in range(link_chunk.head_pos, link_chunk.head_pos + link_chunk.token_size)])
        chunk_str = ",".join([tree.token(i).surface for i in range(chunk.head_pos, chunk.head_pos + chunk.token_size)])
        emo_list[chunk_str] = link_chunk_str
        print('Chunk:', i)
        print(' Score:', chunk.score)
        print(' Link:', chunk.link)
        print(' Size:', chunk.token_size)
        print(' Pos:', chunk.token_pos)
        print(' Func:', chunk.func_pos, tree.token(chunk.token_pos + chunk.func_pos).surface) # 機能語
        print(' Features:',)
#        for j in range(chunk.feature_list_size):
#            print(chunk.feature_list(j),)
        print
        print

    print(emo_list)
    for i in range(tree.token_size()):
        token = tree.token(i)
        print('Surface:', token.surface)
        print(' Normalized:', token.normalized_surface)
        print(' Feature:', token.feature)
        print(' NE:', token.ne) # 固有表現
        print(' Info:', token.additional_info)
        print(' Chunk:', token.chunk)
        print

    return HttpResponse('test page')
