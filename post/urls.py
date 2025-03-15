from django.urls import path
from post.views import index, NewPost, PostDetail, PostLike, SavedPost, postComment, PostTag, UpdatePost, DeletePost

urlpatterns = [
    path('index/', index, name="index"),
    path('new-post/', NewPost, name="NewPost"),
    path('post/<post_id>/', PostDetail, name="PostDetail"),
    path('liked/<post_id>/', PostLike, name="PostLike"),
    path('saved/<post_id>/', SavedPost, name="SavedPost"),
    path('post-comment/<str:post_id>/', postComment, name='postComment'),
    path('tags/<slug:tag_slug>/', PostTag, name='tags'),
    path('post/delete/<post_id>/', DeletePost, name="delete_post"),
    path('post/edit/<post_id>/', UpdatePost, name="edit_post"),

]


