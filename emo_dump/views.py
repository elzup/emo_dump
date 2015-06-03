from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext


def hello(request):
    return HttpResponse('Hello world')



def tweet_test(request):
    return render_to_response('tweet.html',
                              {'testval': 'foo'},
                              context_instance=RequestContext(request))
