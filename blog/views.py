#encoding=utf-8
import markdown
import pygments
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Post, Category
from comments.forms import CommentForm
from django.views.generic import ListView,DetailView

# Create your views here.
def index(request):
    post_list = Post.objects.all().order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})

def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # 阅读量 +1
    post.increase_views()
    # Markdown 渲染
    post.body = markdown.markdown(post.body,
                                extensions=[
                                    'markdown.extensions.extra',
                                    'markdown.extensions.codehilite',
                                    'markdown.extensions.toc',
                                  ])
    form = CommentForm()
    # 获取这篇 post 下的全部评论
    comment_list = post.comment_set.all()
    # 将文章、表单、以及文章下的评论列表作为模板变量传给 detail.html 模板，以便渲染相应数据。
    context = {'post': post,
               'form': form,
               'comment_list': comment_list
               }
    return render(request, 'blog/detail.html', context=context)

def archives(request, year, month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month
                                    ).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})

def category(request, pk):
    # 记得在开始部分导入 Category 类
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})

class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

class CategoryView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    
    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.grt('pk'))
        return super(CategoryView,self).get_queryset().filter(category=cate)

class ArchivesView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    
    def get_queryset(self):
        year = self.Kwargs.get('year')
        month = self.Kwargs.get('month')
        return super(ArchivesView, self).get_queryset().filter(created_time__year=year,created_time__month=month)

class PostDetailView(DetailView):
    # 这些属性的含义和 ListView 是一样的
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post_list'
    
    def get(self, request, *args, **kwargs):
        # 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
        # get 方法返回的是一个 HttpResponse 实例
        # 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，
        # 才有 self.object 属性，其值为 Post 模型实例，即被访问的文章 post
        respose = super(PostDetailView, self).get(request, *args, **kwargs)
        
        # 将文章阅读量 +1
        # 注意 self.object 的值就是被访问的文章 post
        self.object.increase_views()
        
        # 视图必须返回一个 HtppResponse 对象
        return respose
    
    def get_object(self, queryset=None):
        # 覆写 get_object 方法的目的是因为需要对 post 的 body 进行渲染
        post = super(PostDetailView, self).get_object(queryset=Nodne)
        # Markdown 渲染
        post.body = markdown.markdown(post.body,
                                      extensions=[
                                          'markdown.extensions.extra',
                                          'markdown.extensions.codehilite',
                                          'markdown.extensions.toc',
                                      ])
        return post
    
    def get_context_data(self, **kwargs):
        # 覆写 get_context_data 的目的是因为除了将 post 传递给模板外（DetailView 已经帮我们完成），
        # 还要把评论表单、post 下的评论列表传递给模板。
        context = super(PostDetailView, self).get_context_data(**kwargs)
        form = CommentForm()
        # 获取这篇 post 下的全部评论
        comment_list = self.object.comment_set.all()
        # 将表单、以及文章下的评论列表作为模板变量传给 detail.html 模板，以便渲染相应数据。
        context.update({
                   'form': form,
                   'comment_list': comment_list
                   })
        return context