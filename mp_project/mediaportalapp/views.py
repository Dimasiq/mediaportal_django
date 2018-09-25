from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from mediaportalapp.models import Article, Category, UserAccount
from django.db.models import Q
from mediaportalapp.mixins import CategoryAndArticlesListMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.views import View
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from mediaportalapp.forms import CommentForm, RegistrationForm, LoginForm

User = get_user_model()

class ArticleListView(ListView):
    model = Article
    template_name = 'index.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ArticleListView, self).get_context_data(*args, **kwargs)
        context['articles'] = self.model.objects.all()
        return context

class CategoryListView(ListView, CategoryAndArticlesListMixin):
    model = Category
    template_name = 'index.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryListView, self).get_context_data(*args, **kwargs)
        context['categories'] = self.model.objects.all()
        context['articles'] = Article.objects.all()[:4]
        context['slider_articles'] = Article.objects.order_by('?')[:3]
        context['article'] = Article.objects.get(id=1)
        return context

class CategoryDetailView(DetailView, CategoryAndArticlesListMixin):
    model = Category
    template_name = 'category_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(*args, **kwargs)
        context['category'] = self.get_object()
        context['articles_from_category'] = self.get_object().article_set.all()
        return context

class ArticleDetailView(DetailView, CategoryAndArticlesListMixin):
    model = Article
    template_name = 'article_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(*args, **kwargs)
        context['article'] = self.get_object()
        context['article_comments'] = self.get_object().comments.all()
        context['form'] = CommentForm()
        if self.request.user.is_authenticated:
            context['current_user'] = UserAccount.objects.get(user=self.request.user)
        else:
            context['current_user'] = AnonymousUser
        return context

class DynamicArticleImageView(View):
    def get(self, request, *args, **kwargs):
        article_id = self.request.GET.get('article_id')
        article = Article.objects.get(id=article_id)
        data = {
            'article_image': article.image.url
        }
        return JsonResponse(data)

class CreateCommentView(View):
    template_name: 'article_detail.html'

    def post(self, request, *args, **kwargs):
        article_id = self.request.POST.get('article_id')
        comment = self.request.POST.get('comment')
        article = Article.objects.get(id=article_id)
        new_comment = article.comments.create(author=request.user, comment=comment)
        comment = [{ 'author': new_comment.author.username, 'comment': new_comment.comment, 'timestamp': new_comment.timestamp.strftime('%Y-%m-%d') }]
        return JsonResponse(comment, safe=False)

class DisplayArticlesByCategoryView(View):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        category_slug = self.request.GET.get('category_slug')
        articles = list(Article.objects.filter(category=Category.objects.get(slug = category_slug)).values('title', 'image', 'slug'))
        data = {
            'articles': articles
        }
        return JsonResponse(data)

class UserReactionView(View):
    template_name = 'article_detail.html'

    def get(self, request, *args, **kwargs):
        article_id = self.request.GET.get('article_id')
        article = Article.objects.get(id=article_id)
        like = self.request.GET.get('like')
        dislike = self.request.GET.get('dislike')
        if like and (request.user not in article.users_reaction.all()):
            article.likes += 1
            article.users_reaction.add(request.user)
            article.save()
        if dislike and (request.user not in article.users_reaction.all()):
            article.dislikes += 1
            article.users_reaction.add(request.user)
            article.save()
        data = {
            'likes': article.likes,
            'dislikes': article.dislikes
        }
        return JsonResponse(data)

class RegistrationView(View):
    template_name = 'registration.html'

    def get(self, request, *args, **kwargs):
        form = RegistrationForm()
        categories = Category.objects.all()
        context = {
            'form': form,
            'categories': categories
        }
        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            new_user.set_password(password)
            password_check = form.cleaned_data['password_check']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            new_user.save()
            UserAccount.objects.create(user=User.objects.get(username=new_user.username),
                                                            first_name=new_user.first_name,
                                                            last_name=new_user.last_name,
                                                            email=new_user.email)
            return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(self.request, self.template_name, context)

class LoginView(View):
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        categories = Category.objects.all()
        context = {
            'form': form,
            'categories': categories
        }
        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(self.request, user)
                return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(self.request, self.template_name, context)

class UserAccountView(View, CategoryAndArticlesListMixin):
    template_name = 'user_account.html'

    def get(self, request, *args, **kwargs):
        user = self.kwargs.get('user')
        categories = Category.objects.all()
        current_user = UserAccount.objects.get(user=User.objects.get(username=user))
        context = {
            'current_user': current_user,
            'categories': categories
        }
        return render(self.request, self.template_name, context)

class AddArticleToFavorites(View):
    template_name = 'article_detail.html'

    def get(self, request, *args, **kwargs):
        article_slug = self.request.GET.get('article_slug')
        article = Article.objects.get(slug=article_slug)
        current_user = UserAccount.objects.get(user=request.user)
        current_user.fav_articles.add(article)
        current_user.save()
        return JsonResponse({ 'ok':'ok' })

class RemoveArticleFromFavorites(View):
    template_name = 'user_account.html'

    def get(self, request, *args, **kwargs):
        article_slug = self.request.GET.get('article_slug')
        article = Article.objects.get(slug=article_slug)
        current_user = UserAccount.objects.get(user=request.user)
        current_user.fav_articles.remove(article)
        current_user.save()
        return JsonResponse({ 'ok':'ok' })

class SearchView(View):
    template_name = 'search.html'

    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('q')
        categories = Category.objects.all()
        found_articles = Article.objects.filter(
            Q(title__icontains=query)|
            Q(content__icontains=query))
        context = {
            'found_articles': found_articles,
            'categories': categories
        }
        return render(self.request, self.template_name, context)
