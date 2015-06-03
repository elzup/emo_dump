import traceback

from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
import tweepy


def hello(request):
    return HttpResponse('Hello world')


def index(request):
    return HttpResponse('index')


def oauth_start(request):
    CALLBACK_URL = 'http://lvh.me:8000/auth/end/'.encode('utf-8')
    auth = tweepy.OAuthHandler(settings.CONSUMER_KEY.encode('utf-8'), settings.CONSUMER_SECRET.encode('utf-8'),
                               CALLBACK_URL)
    try:
        auth_url = auth.get_authorization_url()
    except tweepy.TweepError:
        print(traceback.format_exc())
    print(auth.request_token.keys())
    keys = auth.request_token.keys()
    request.session['request_token'] = (
    auth.request_token.get('oauth_token'), auth.request_token.get('oauth_token_secret'))
    return HttpResponseRedirect(auth_url)


def oauth_end(request):
    verifier = request.GET.get('oauth_verifier')
    auth = tweepy.OAuthHandler(settings.CONSUMER_KEY.encode('utf-8'), settings.CONSUMER_SECRET.encode('utf-8'))

    token = request.session.get('request_token')
    del request.session['request_token']
    auth.set_access_token(token[0], token[1])

    request.session['key'] = token[0]
    request.session['secret'] = token[1]
    return HttpResponseRedirect('/')
