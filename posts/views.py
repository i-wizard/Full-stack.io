from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Post, Author, PostView
from marketing.models import Signup
from .forms import CommentForm, PostForm

def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None

#processing a search request
def search(request):
    post_list = Post.objects.all()
    query = request.GET.get('q')#this is what the user is searching ofr
    if query:
        post_list = post_list.filter(
            Q(title__icontains=query)|#this means if the title contains the search query, we first import the Q
            Q(overview__icontains=query)#this means if the overview contains the search query
        ).distinct()#this is incase the search query exist in both the title and the overview of the same post, to make sure it doesnt return the same result twice

    context = {
            'post_list':post_list
        }
    return render(request, 'search_results.html', context)


def get_category_count():# the first line is to get the value of the object category in the Post model
    queryset = Post.objects.values('categories__title').annotate(Count('categories__title'))
    return queryset

def index(request):
    featured = Post.objects.filter(featured=True)
    latest = Post.objects.order_by('-timestamp')[0:3]

    if request.method=="POST":
        email = request.POST['email']
        new_signup = Signup()
        new_signup.email = email
        new_signup.save()
        return redirect('/')

    context = {
        "object_list":featured,
        "latest":latest
    } 
    return render(request, 'index.html', context)

def blog(request):
    category_count = get_category_count()
    article_list = Post.objects.order_by('-timestamp')
    most_recent = Post.objects.order_by('-timestamp')[:3]
    #this will render the article list and only for instance(1 blog post)
    paginator = Paginator(article_list, 2)
    page_request_var = 'page'
    #this is what will show on the url bar....we are making it show the page number
    page = request.GET.get(page_request_var)
    #lets look out for some errors by users
    try:
        paginated_queryset = paginator.page(page)#this will get the requested page according to the page number passed in as an arguement
    except PageNotAnInteger:# when a user uses a string it will return the first page
        paginated_queryset = paginator.page(1)
    except EmptyPage:# when a user searches beyong the avilable numbert of pages it will return tyhe last page
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'article_list':paginated_queryset,
        'page_request_var':page_request_var,
        'most_recent':most_recent,
        'category_count':category_count
    }
    return render(request, 'blog.html', context)

def post(request, id):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post = get_object_or_404(Post, id=id)

    if request.user.is_authenticated:
        PostView.objects.get_or_create(user=request.user, post=post)
    
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        form.instance.user = request.user
        form.instance.post = post
        if form.is_valid():
            form.save()
            return redirect(reverse('post-detail', kwargs={
                'id':post.id
            }))

   
#
    context = {
        'form':form,
        'post':post,
        'most_recent':most_recent,
        'category_count':category_count
    }
    return render(request, "post.html", context)



def post_create(request):
    title = 'Create'
    form= PostForm(request.POST or None, request.FILES or None)
    author = get_author(request.user)
    if request.method=='POST':
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse('post-detail', kwargs={
                'id':form.instance.id
            }))
    context={
        'form':form,
        'title':title
    }
    return render(request, 'post_create.html', context)


def post_update(request, id):
    title = 'Update'
    post = get_object_or_404(Post, id=id)
    form= PostForm(request.POST or None, request.FILES or None, instance=post)
    author = get_author(request.user)
    if request.method=='POST':
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse('post-detail', kwargs={
                'id':form.instance.id
            }))
    context={
        'form':form,
        'title':title
    }
    return render(request, 'post_create.html', context)

def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect(reverse('post-list'))