from ninja import Router
from .models import User, UserLikePaper, UserBrowsePaperHistory
from .schemas import RegisterIn, LoginIn, NotesPostIn, NotesGetOut, LikePaperOut, BrowsePaperHistoryOut
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from gpt_simplify.models import Paper

from django.db.models import F, Value, BooleanField, ExpressionWrapper, Q

user_authentication_api = Router()


@user_authentication_api.post("/register/")
def auth_register(request, payload: RegisterIn):
    if User.objects.filter(username=payload.username).exists():
        return {"msg": "Username already exists"}
    user = User.objects.create_user(
        username=payload.username, password=payload.password)
    return {"msg": "User created successfully", "username": user.username, "pwd": user.password}


@user_authentication_api.post("/login/")
# 这样用payload参数代表request body
def auth_login(request: HttpRequest, response: HttpResponse, payload: LoginIn):
    print(f"username: {payload.username}, password: {payload.password}")
    # authenticate()自动调用create_user()时同样的哈希计算
    user = authenticate(request, username=payload.username,
                        password=payload.password)  # 就是检查用户名对应的口令
    print(user)
    print(type(user))
    if user is not None:
        login(request, user)
        # 浏览器还是没有cookie !!!(前端需要设置axios.defaults.withCredentials = true;)
        response.set_cookie("cookie", "delicious")
        return {"msg": "Login successful", "username": user.username}
    else:
        return {"msg": "Invalid credentials"}


@user_authentication_api.get("/logout/")
def auth_logout(request, response: HttpResponse):
    # 把login()做的事情抵消了,session表删掉这个用户的session,删掉client的sessionid的cookie
    logout(request)
    response.delete_cookie('cookie')  # 然后前端浏览器真的把这个cookie删了
    return {"msg": "Logout successfully"}


@user_authentication_api.post("/like/")
@login_required
def user_like_paper(request, paper_id: str):
    # 按钮灰色星星时点击收藏
    # 如果已经收藏了，那就返回个msg，不往数据库里添加了
    existing_record = UserLikePaper.objects.filter(
        user_id=request.user.id, paper_id=paper_id).first()
    if existing_record:
        return {"msg": "already liked"}
    else:
        print(request.user.id)
        print(paper_id)
        # create参数严格要和数据库里的一样，和model定义的一样没用，按数据库的字段名为准
        UserLikePaper.objects.create(
            user_id=request.user.id, paper_id=paper_id)


@user_authentication_api.delete("/like/")
@login_required
def user_cancel_like_paper(request, paper_id: str):
    # 按钮黄色星星时点击取消收藏
    existing_record = UserLikePaper.objects.filter(
        user_id=request.user.id, paper_id=paper_id).first()
    if existing_record:
        existing_record.delete()
        return {"msg": "favorites canceled"}


@user_authentication_api.get("/like/", response=list[LikePaperOut])
@login_required
def user_like_list(request):
    liked_papers_id = UserLikePaper.objects.filter(
        user_id=request.user.id).values_list('paper_id', flat=True)
    print(liked_papers_id)
    # !!! __in查询
    liked_papers = Paper.objects.filter(paper_id__in=liked_papers_id)
    print(liked_papers)
    # 字段名改为和数据库里一样后，就直接返回行了
    """ return_list = []
    for liked_paper in liked_papers:
        cur_paper = {}
        cur_paper["paper_id"] = liked_paper.paper_id
        cur_paper["title_en"] = liked_paper.title_en
        cur_paper["title_ja"] = liked_paper.title_ja
        cur_paper["Authors"] = liked_paper.authors
        cur_paper["Categories"] = liked_paper.categories
        cur_paper["Published"] = liked_paper.published
        cur_paper["Content_En"] = liked_paper.content_en
        cur_paper["Pdf_url"] = liked_paper.pdf_url
        return_list.append(cur_paper)
    return return_list """
    # TypeError: Object of type QuerySet is not JSON serializable
    # 看样子ninja的修饰器出口会把dict给serialize成json
    # 而数据库Object就要写schema才能serialize为json出口了
    return liked_papers


@user_authentication_api.get("/likelist_cnt/")
@login_required
def user_likedlist_cnt(request):
    return UserLikePaper.objects.filter(user_id=request.user.id).count()


@user_authentication_api.post("/notes/")
@login_required
def post_notes(request, payload: NotesPostIn):
    existing_record = UserBrowsePaperHistory.objects.filter(
        user_id=request.user.id, paper_id=payload.paper_id).first()
    if existing_record:
        existing_record.notes = payload.notes
        existing_record.save()
    # 其实不需要else了，因为先访问simplify进入detailpaper页面，那肯定在浏览历史里加入记录了
    else:
        UserBrowsePaperHistory.objects.create(user_id=request.user.id,
                                              paper_id=payload.paper_id,
                                              notes=payload.notes)
    # return {"msg": "post success"}


@user_authentication_api.get("/notes/", response=NotesGetOut)
@login_required
def get_notes(request, paper_id: str):
    existing_record = UserBrowsePaperHistory.objects.filter(
        user_id=request.user.id, paper_id=paper_id).first()
    if existing_record:
        # return {"notes": existing_record.notes, "123": 456} #response=NotesGetOut定义了schema就只返回schema里有的字段
        return existing_record


@user_authentication_api.get("/browse-history-cnt/")
@login_required
def user_browse_history_cnt(request):
    return UserBrowsePaperHistory.objects.filter(user_id=request.user.id).count()


# 需要把has_note布尔变量传给前端，用以区别显示
@user_authentication_api.get("/browse-history/", response=list[BrowsePaperHistoryOut])
@login_required
def user_browse_history_list(request):
    # 获取用户浏览历史记录并联接对应的论文数据
    browse_history = UserBrowsePaperHistory.objects.filter(
        user_id=request.user.id).select_related('paper')
    # select_related('paper')：预加载 paper外键关联的数据，以避免 N+1 查询问题，提高查询效率
    # print(browse_history)

    # 创建查询集，注释has_note字段 (annotate给QuerySet增加一个表里没有的field)
    browse_history_with_hasNotes = browse_history.annotate(
        has_note=ExpressionWrapper(
            ~Q(notes=""), output_field=BooleanField())
    )
    # print(browse_history_with_hasNotes.values())
    # print(list(browse_history_with_hasNotes.values()))
    # 保留自己的两个字段"paper_id", "has_note", 其他通过外键 双下划线(__)用于跨表引用字段
    browse_history_with_hasNotes = browse_history_with_hasNotes.values(
        "paper_id",
        "has_note",
        title_en=F('paper__title_en'),
        title_ja=F('paper__title_ja'),
        authors=F('paper__authors'),
        categories=F('paper__categories'),
        published=F('paper__published'),
        content_en=F('paper__content_en'),
        pdf_url=F('paper__pdf_url'),
    )
    # print(browse_history_with_hasNotes[0].values())

    return browse_history_with_hasNotes


# 创建一条历史记录会在叩く/simplify时创建
@user_authentication_api.delete("/browse-history/")
@login_required
def user_delete_simplify_history(request, paper_id: str):
    existing_record = UserBrowsePaperHistory.objects.filter(
        user_id=request.user.id, paper_id=paper_id).first()
    if existing_record:
        existing_record.delete()
        return {"msg": "history deleted"}
