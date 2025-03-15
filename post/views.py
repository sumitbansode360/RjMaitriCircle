from django.shortcuts import render, redirect, HttpResponseRedirect
from post.models import Post, Stream, Like, Follow, Tag, Like
from post.forms import NewPostModelForm
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from userauths.models import Profile
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from comments.models import PostComment
from collections import defaultdict
from channels.layers import get_channel_layer
from notification.models import Notification
from asgiref.sync import async_to_sync

def index(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('sign-in') 
    
    profile = Profile.objects.get(user=user)

    posts = Stream.objects.filter(user=user)

    grp_ids = []

    for post in posts:
        grp_ids.append(post.post_id)

    post_items = Post.objects.filter(id__in=grp_ids).all().order_by('-posted')


#     all_profiles = Profile.objects.exclude(user=user and Profile.user.follow=)
# # Attach follow status to each profile dynamically
#     for other_profile in all_profiles:
#         other_profile.follow_status = Follow.objects.filter(follower=request.user, following=other_profile.user).exists()

    unfollowed_profiles = Profile.objects.exclude(user=user).exclude(user__in=Follow.objects.filter(follower=request.user).values_list('following', flat=True))
    context = {
        'post_items' : post_items,
        'profile' : profile,
        'all_profile' : unfollowed_profiles,
    }

    return render(request, 'post/index.html', context)

def NewPost(request):
    user = request.user.id
    tag_obj = []
    if request.method == "POST":
        form = NewPostModelForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data.get('image')
            caption = form.cleaned_data.get('caption')
            tag_form = form.cleaned_data.get('tag')
            tag_list = list(tag_form.split(","))

            for tag in tag_list:
                t , created = Tag.objects.get_or_create(title=tag)
                tag_obj.append(t)

            p , created = Post.objects.get_or_create(image=image, caption=caption, user_id=user)
            p.tag.set(tag_obj)

            return redirect("index")
    else:
        form = NewPostModelForm()
    context = {
        'form' : form
    }

    return render(request, 'post/new_post.html', context)

def PostDetail(request, post_id):
    user = request.user
    post = Post.objects.get(post_id=post_id)
    profile = Profile.objects.get(user=user)

    comments = PostComment.objects.filter(post=post, parent=None).order_by('-timestamp')
    replies = PostComment.objects.filter(post=post).exclude(parent=None)

 # Create a dictionary to store replies grouped by parent comment's sno
    replyDict = defaultdict(list)
    for reply in replies:
        replyDict[reply.parent.sno].append(reply)

    context = {
        "post" : post,
        'profile' : profile,
        'comments': comments,
        'user': request.user,
        'replyDict': replyDict,

    }

    return render(request, "post-detail.html", context)

def PostLike(request, post_id):
    if request.method == "POST":
        user = request.user
        post = get_object_or_404(Post, post_id=post_id)

        if user in post.liked_by.all():
            post.liked_by.remove(user)
            liked = False
        else:
            post.liked_by.add(user)
            liked = True

        notification = Notification.objects.create(
            user = post.user,
            sender = user,
            notification_type = "like",
            message = f"{user.username} liked ❤️ your post!"
        )


        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{post.user.id}",  
            {
                "type" : "send_notification",
                "notification": {
                    "id": notification.id,
                    "image": notification.sender.profile.image.url if notification.sender.profile.image.url else "/static/default-profile.png",
                    "notification_type": notification.notification_type,
                    "message": notification.message,
                    "timestamp": str(notification.created_at),
                }
            }
        )


        post.likes = post.liked_by.count()
        post.save()

        return JsonResponse({
            "liked": liked,
            "like_count": post.likes
        })
    return JsonResponse({"error": "Invalid request"}, status=400)

def SavedPost(request, post_id):
    if request.method == "POST":
        user = request.user
        # Get the post and profile objects
        post = get_object_or_404(Post, id=post_id)  # Ensure you're querying by the correct ID field
        profile = get_object_or_404(Profile, user=user)

        # Toggle the save status
        if profile.saved.filter(id=post.id).exists():
            profile.saved.remove(post)
            saved = False
        else:
            profile.saved.add(post)
            saved = True

        return JsonResponse({
            "saved": saved,  
        })

    return JsonResponse({"error": "Invalid request method."}, status=400)

def postComment(request, post_id):
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        user = request.user
        parent_sno = request.POST.get('parentSno', None)

        # Fetch the post using post_id
        post = get_object_or_404(Post, post_id=post_id)

        # Handle parent comment if provided
        if parent_sno:
            parent = get_object_or_404(PostComment, sno=parent_sno)
            comment = PostComment(comment=comment_text, user=user, post=post, parent=parent)
        else:
            comment = PostComment(comment=comment_text, user=user, post=post)


        notification = Notification.objects.create(
            user = post.user,
            sender = user,
            notification_type = "comment",
            message = f"{user.username} commented 💬 on your post: {post.caption[:30]}"
        )



        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{post.user.id}",  
            {
                "type" : "send_notification",
                "notification": {
                    "id": notification.id,
                    "image": notification.sender.profile.image.url if notification.sender.profile.image.url else "/static/default-profile.png",
                    "notification_type": notification.notification_type,
                    "message": notification.message,
                    "timestamp": str(notification.created_at),

                }
            }
        )

        

        comment.save()
        messages.success(request, "Comment posted!")
        # Redirect back to the post details page
        return HttpResponseRedirect(reverse('PostDetail', args=[post_id]))

    return redirect('index')


def PostTag(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tag=tag).order_by('-posted')

    context = {
        'posts': posts,
        'tag': tag

    }
    return render(request, 'post/tag.html', context)