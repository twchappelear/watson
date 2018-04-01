from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post
from .forms import PostForm
from django.shortcuts import redirect
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import LanguageTranslatorV2 as LanguageTranslator
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 \
  import Features, KeywordsOptions


# Create your views here.

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    tone_analyzer = ToneAnalyzerV3(
        username='cb346cc1-2e7f-40a1-b425-b447f325708e',
        password='jKqhMKEbM2N5',
        version='2016-05-19 ')

    language_translator = LanguageTranslator(
        username='9af1bf91-8ed7-4e26-a3fb-fb07c74d556e',
        password='8cSAvBouuZD8')

    natural_language_understanding = NaturalLanguageUnderstandingV1(
        username='8ffadb58-95ba-4d61-8443-30a942bc9903',
        password='NjmkNHyHdpFn',
        version='2018-03-16')

    # print(json.dumps(translation, indent=2, ensure_ascii=False))

    for post in posts:
        posting = post.text
        toneObj = json.dumps(tone_analyzer.tone(tone_input=posting,
                                                content_type="text/plain"), indent=2)
        post.toneObj2 = json.loads(toneObj)
        post.angerScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][0]['score']
        post.disgustScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][1]['score']
        post.fearScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][2]['score']
        post.joyScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][3]['score']
        post.sadScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][4]['score']

        translation = language_translator.translate(
            text=post.text,
            source='en',
            target='es')
        obj = json.dumps(translation, indent=2, ensure_ascii=False)
        post.obj2 = json.loads(obj)
        post.trans = post.obj2['translations'][0]['translation']
        post.wordCount = post.obj2['word_count']
        post.characterCount = post.obj2['character_count']

        response = natural_language_understanding.analyze(
            text=post.text,
            features=Features(
                keywords=KeywordsOptions(
                    sentiment=True,
                    emotion=True,
                    limit=2)))
        keyObj = json.dumps(response, indent=2)
        post.obj3= json.loads(keyObj)
        post.keyUse = post.obj3['usage']['text_characters']
        post.keyWord = post.obj3['keywords'][0]['text']
        post.keySent = post.obj3['keywords'][0]['sentiment']['label']
        post.keyRel = post.obj3['keywords'][0]['relevance']
        post.keySad = post.obj3['keywords'][0]['emotion']['sadness']
        post.keyJoy = post.obj3['keywords'][0]['emotion']['joy']
        post.keyFear = post.obj3['keywords'][0]['emotion']['fear']
        post.keyDisg = post.obj3['keywords'][0]['emotion']['disgust']
        post.keyAng = post.obj3['keywords'][0]['emotion']['anger']



    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})
