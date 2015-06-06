import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from emo_dump.classes.twitter_manager import TwitterManager
from emo_dump.classes.cabocha_manager import CabochaManager


def hello(request):
    return HttpResponse('Hello world')


def index(request):
    """トップページ"""
    tm = TwitterManager(request.session)
    if not tm.is_login:
        return render_to_response('no_login.html')
    # TODO: 動的に デフォルトは認証ユーザ
    target_screen_anme = None
    tweets = tm.user_timeline(target_screen_anme, count=200)

    cm = CabochaManager()
    res = cm.analyze_tweets(tweets)

    # limit
    limit_info = tm.rate_limit_status_userstimeline()
    ts = datetime.datetime.fromtimestamp(int(limit_info['reset']))
    limit_info['time_str'] = ts.strftime('%H:%M:%S')

    return render_to_response('tweet.html', {'res': res.items(), 'tweets': tweets, 'limit_info': limit_info})


def oauth_start(request):
    """Twitter認証開始ページ"""
    tm = TwitterManager(request.session, set_api=False)
    tm.auth_start()
    request.session['request_token'] = tm.auth.request_token
    return HttpResponseRedirect(tm.auth_url)


def oauth_end(request):
    """Twitter認証 Callback ページ"""
    verifier = request.GET.get('oauth_verifier')
    tm = TwitterManager(request.session, set_api=False)
    tm.auth_end(verifier=verifier,
                token=request.session.get('request_token'))
    request.session['key'] = tm.auth.access_token
    request.session['secret'] = tm.auth.access_token_secret
    return HttpResponseRedirect('/')


def oauth_clear(request):
    request.session.clear()
    return HttpResponseRedirect('/')
