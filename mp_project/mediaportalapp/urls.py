from django.urls import path, reverse_lazy
from django.contrib.auth.views import LogoutView
from mediaportalapp.views import CategoryListView, CategoryDetailView, ArticleDetailView, DynamicArticleImageView, CreateCommentView, DisplayArticlesByCategoryView, UserReactionView, RegistrationView, LoginView, UserAccountView, AddArticleToFavorites, RemoveArticleFromFavorites, SearchView

urlpatterns = [
    path('', CategoryListView.as_view(), name='base_view'),
    path('category/<slug>', CategoryDetailView.as_view(), name='category_detail'),
    path('<category>/<slug>', ArticleDetailView.as_view(), name='article_detail'),
    path('show_article_image', DynamicArticleImageView.as_view(), name='article_image'),
    path('add_comment/', CreateCommentView.as_view(), name='add_comment'),
    path('display_articles_by_category', DisplayArticlesByCategoryView.as_view(), name='articles_by_category'),
    path('user_reaction/', UserReactionView.as_view(), name='user_reaction'),
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('user_account/<user>/', UserAccountView.as_view(), name='account_view'),
    path('add_to_fav/', AddArticleToFavorites.as_view(), name='add_to_fav'),
    path('remove_from_fav/', RemoveArticleFromFavorites.as_view(), name='remove_from_fav'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('base_view')), name='logout'),
    path('search/', SearchView.as_view(), name='search')
]
