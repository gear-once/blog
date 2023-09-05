from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CommentForm, PostCreateForm
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.auth.decorators import login_required


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    # Pagination with 3 posts per page
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request,
                 'post/list.html',
                 {'posts': posts,
                  'tag':tag,
                  'section': 'blog',})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                            status=Post.Status.PUBLISHED,
                            slug=post,
                           
                            publish__year=year,
                            publish__month=month,
                            publish__day=day)
   
    # List of active comments for this post
    comments = post.comments.filter(active=True)[0:20]
    # Form for users to comment
    form = CommentForm()

    #list of similar posts
    post_tags = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags).exclude(id=post.id)
    similiar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[0:4]

    return render(request,
                  'post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form,
                   'similar_posts':similar_posts,
                   'section': 'blog',})


def postCreate(request):
    if request.method == 'POST':
        form = PostCreateForm(data=request.POST)
        if form.is_valid():
            new_post=form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect("posts:post_list")

    else:
        
        form = PostCreateForm(data=request.GET)

    return render(request,
                  'post/create_post.html',
                  {'section': 'blog',
                   'form': form})

@login_required
@require_POST
def post_like(request):
    post_id = request.POST.get('id')
    action =request.POST.get('action')
    if post_id and action:
        try:
            post = Post.published.get(id=post_id)
            if action =='like':
                post.posts_like.add(request.user)
            else:
                post.posts_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Post.DoesNotExist:
            pass
    return JsonResponse({'status':'error'})


#-----------------Comment Views------------------------------------


def post_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id, \
                                    status=Post.Status.PUBLISHED)
        comment = None
        # A comment was posted
        form = CommentForm(data=request.POST)
        if form.is_valid():
            # Create a Comment object without saving it to the database
            comment = form.save(commit=False)
            # Assign the post to the comment
            comment.post = post
            if request.user.is_authenticated:
                comment.user = request.user
            else:
                comment.user = None
                comment.active = False
            # Save the comment to the database
            comment.save()
        return render(request, 'post/comment.html',
                            {'post': post,
                                'form': form,
                                'comment': comment,
                                'section': 'blog',})
    
    else:
        return HttpResponse("only Post requests allowed.")
