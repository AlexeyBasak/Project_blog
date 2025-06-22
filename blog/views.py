from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from blog.models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import AddPostForm, EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.views.generic import CreateView
from django.utils import timezone
from slugify import slugify 
# class PostsListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    data = {
        "posts": posts,
        "tag": tag,
    }

    return render(request, "blog/post/list.html", context=data)


def post_detail(request, year, month, day, post):
    p = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    try:
        comment = p.comments.latest("id")
    except Comment.DoesNotExist:
        comment = None
    count = p.comments.count()

    form = CommentForm()
    post_tags_ids = p.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=p.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:3]

    data = {"post": p, "comment": comment, "form": form, "count": count, 'similar_posts': similar_posts}

    return render(request, "blog/post/detail.html", context=data)


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)

    sent = False
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you to read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, "alexey.basak06@gmail.com", [cd["to"]])
            sent = True
            return redirect("blog:post_list")
    else:
        form = EmailPostForm()

    data = {"post": post, "form": form, "sent": sent}

    return render(request, "blog/post/share.html", context=data)


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None

    form = CommentForm(data=request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    data = {
        "post": post,
        "form": form,
        "comment": comment,
    }

    return render(request, "blog/post/comment.html", context=data)


def all_post_comments(request, post_slug):
    post = get_object_or_404(Post, slug=post_slug)
    comments = post.comments.all()

    data = {"post": post, "comments": comments}

    return render(request, "blog/post/post_comments.html", context=data)


def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:post_list')

    data = {
        'post': post,
    }
    return render(request, 'blog/post/post_confirm_delete.html', context=data)

class AddPost(View):
    def get(self, request):
        form = AddPostForm()
        return render(request, 'blog/post/create_post.html', {'form': form})

    def post(self, request):
        form = AddPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.slug = slugify(post.title)
            post.created = timezone.now()
            post.updated = timezone.now()
            post.save()
            form.save_m2m()
            return redirect('blog:post_list')
        
        return render(request, 'blog/post/create_post.html', {'form': form})  
    


def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post = comment.post
    if request.method == 'POST':
        comment.delete()
        return redirect(post.get_absolute_url())

    data = {
        'comment': comment,
    }
    return render(request, 'blog/post/comment_confirm_delete.html', context=data)
