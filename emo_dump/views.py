import traceback

from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response
import tweepy


def hello(request):
    return HttpResponse('Hello world')


def index(request):
    auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    if 'key' not in request.session:
        return render_to_response('no_login.html')

    print(request.session.get('key'), request.session.get('secret'))
    auth.set_access_token(request.session.get('key'), request.session.get('secret'))
    api = tweepy.API(auth_handler=auth)
    tweets = api.home_timeline()
    return render_to_response('tweet.html', {'tweets': tweets})

def oauth_start(request):
    CALLBACK_URL = 'http://localhost:8000/auth/end/'.encode('utf-8')
    auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET, CALLBACK_URL)
    try:
        auth_url = auth.get_authorization_url()
    except tweepy.TweepError:
        print(traceback.format_exc())
    request.session['request_token'] = auth.request_token
    return HttpResponseRedirect(auth_url)


def oauth_end(request):
    verifier = request.GET.get('oauth_verifier')
    auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
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
