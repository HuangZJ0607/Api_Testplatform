from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from Myapp.models import *
import json


@login_required  # 登录态检查装饰器
def welcome(request):
    return render(request, 'welcome.html')


@login_required  # 登录态检查装饰器
def home(request):
    return render(request, 'welcome.html', {"whichHTML": "home.html", "oid": ""})


# 返回子页面
def child(request, eid, oid):
    res = child_json(eid, oid)
    return render(request, eid, res)


# 控制不同的页面返回不同的数据：数据分发器
def child_json(eid, oid=''):
    res = {}
    if eid == 'home.html':
        date = DB_home_href.objects.all()
        res = {"hrefs": date}
    if eid == "project_list.html":
        date = DB_project.objects.all()
        res = {"projects": date}
    if eid == 'P_apis.html':
        project = DB_project.objects.filter(id=oid)[0]
        apis = DB_apis.objects.filter(project_id=oid)
        res = {"project": project, "apis": apis}
    if eid == 'P_cases.html':
        project = DB_project.objects.filter(id=oid)[0]
        res = {"project": project}
    if eid == 'P_project_set.html':
        project = DB_project.objects.filter(id=oid)[0]
        res = {"project": project}
    return res


def login(request):
    return render(request, 'login.html')


def logout(request):
    from django.contrib import auth
    auth.logout(request)
    return HttpResponseRedirect('/login/')


def login_action(request):
    username = request.GET['username']
    password = request.GET['password']
    # 开始联通django用户库。
    from django.contrib import auth
    # 查看用户名密码是否正确
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        # 用户名密码正确，则调用django的真正登录函数auth.login
        auth.login(request, user)
        # 把登录状态也就是成功的用户名当作session写进用户浏览器，这样就能成功进入各个页面
        request.session['user'] = username
        return HttpResponse('True')
    else:
        # 返回前端用户名/密码不对
        return HttpResponse('False')


def register_action(request):
    # 获取前端给的用户名和密码
    username = request.GET['username']
    password = request.GET['password']
    # 开始联通django用户表
    # 导入User方法，其实User是orm方式操作用户表的实例
    from django.contrib.auth.models import User
    try:
        # 使用create_user方法生成一个y用户，参数为用户名和密码，保存这个生成的用户就是注册成功
        user = User.objects.create_user(username=username, password=password)
        user.save()
        return HttpResponse('注册成功！')
    except:
        # 上面语句报错，证明用户表中已经有这个用户名
        return HttpResponse('注册失败！用户名好像已经存在!')


# 吐槽函数
def tucao(request):
    '''
        create方法就是创建数据库记录，参数就是我们的字段内容
        不过我们本来有4个字段：id user text ctime
        因为id为自动创建不用我们操心，ctime也是自动填入也不用我们操心，所以我们这里只写user 和 text即可
        user就是吐槽的用户名，所有请求的信息包括请求者的登陆用户名都存放在reqeust这个参数中，它里面的user.username就是请求的用户名了我们拿出来当作吐槽表的用户名，tucao_text就是吐槽内容,赋值给text
    '''
    tucao_text = request.GET['tucao_text']
    DB_tucao.objects.create(user=request.user.username, text=tucao_text)
    return HttpResponse('')


def api_help(request):
    return render(request, 'welcome.html', {"whichHTML": "help.html", "oid": ""})


def project_list(request):
    '''

    :param request:
    :return:
    '''
    return render(request, 'welcome.html', {"whichHTML": "project_list.html", "oid": ""})


# 删除项目
def delete_project(request):
    '''
        获取项目id
        .filter()方法可以找出所有符合的数据记录
    :return:随便返回一个值
    '''
    id = request.GET['id']
    DB_project.objects.filter(id=id).delete()
    DB_apis.objects.filter(project_id=id).delete()
    return HttpResponse('')


def add_project(request):
    '''
    新建了这个 add_project函数：
       它要做三件事：
        1.接收project_name
        2.去项目表新建项目
        3.返回给前端一个空证明已经成功完成
    '''
    project_name = request.GET['project_name']
    DB_project.objects.create(name=project_name, remark='', user=request.user.username, other_user='')
    return HttpResponse('')


# 进入接口库
def open_apis(request, id):
    project_id = id
    return render(request, 'welcome.html', {'whichHTML': "P_apis.html", "oid": project_id})


# 进入用例设置库
def open_cases(request, id):
    project_id = id
    return render(request, 'welcome.html', {"whichHTML": "P_cases.html", "oid": project_id})


# 进入项目设置
def open_project_set(requset, id):
    project_id = id
    return render(requset, 'welcome.html', {"whichHTML": "P_project_set.html", "oid": project_id})


# 保存项目设置
def save_project_set(request, id):
    project_id = id
    name = request.GET['name']
    remark = request.GET['remark']
    other_user = request.GET['other_user']
    DB_project.objects.filter(id=project_id).update(name=name, remark=remark, other_user=other_user)
    return HttpResponse('')


# 获取接口备注
def get_bz(request):
    api_id = request.GET['api_id']
    bz_value = DB_apis.objects.filter(id=api_id)[0].des
    return HttpResponse(bz_value)


# 保存接口备注
def save_bz(request):
    api_id = request.GET['api_id']
    bz_value = request.GET['bz_value']
    DB_apis.objects.filter(id=api_id).update(des=bz_value)  # 这里的des就是描述，也就是现在的备注
    return HttpResponse('')


# 保存接口
def Api_save(request):
    # 提取所有数据
    api_id = request.GET['api_id']
    ts_method = request.GET['ts_method']
    ts_url = request.GET['ts_url']
    ts_host = request.GET['ts_host']
    ts_header = request.GET['ts_header']
    ts_body_method = request.GET['ts_body_method']
    api_name = request.GET['api_name']
    if ts_body_method == '返回体':
        api =DB_apis.objects.filter(id=api_id)[0]
        ts_body_method = api.last_body_method
        ts_api_body = api.last_api_body
    else:
        ts_api_body = request.GET['ts_api_body']
    # 保存数据
    DB_apis.objects.filter(id=api_id).update(
        api_method=ts_method,
        api_url=ts_url,
        api_header=ts_header,
        api_host=ts_host,
        body_method=ts_body_method,
        api_body=ts_api_body,
        name=api_name
    )
    # 返回
    return HttpResponse('success')


# 获取接口数据
def get_api_data(request):
    api_id = request.GET['api_id']
    api = DB_apis.objects.filter(id=api_id).values()[0]
    return HttpResponse(json.dumps(api), content_type='application/json')


# 调试层发送请求
def Api_send(request):
    # 提取所有数据
    api_id = request.GET['api_id']
    ts_method = request.GET['ts_method']
    ts_url = request.GET['ts_url']
    ts_host = request.GET['ts_host']
    ts_header = request.GET['ts_header']
    ts_body_method = request.GET['ts_body_method']
    ts_api_body = request.GET['ts_api_body']
    api_name = request.GET['api_name']
    ts_body_method = request.GET['ts_body_method']
    if ts_body_method == '返回体':
        api = DB_apis.objects.filter(id=api_id)[0]
        ts_body_method = api.last_body_method
        ts_api_body = api.last_api_body
        if ts_body_method in ['',None]:
            return HttpResponse('请先选择好请求体编码格式和请求体，再点击Send按钮发送请求！')
    else:
        ts_api_body = request.GET['ts_api_body']
        api = DB_apis.objects.filter(id=api_id)
        api.update(last_body_method=ts_body_method, last_api_method=ts_body_method)
    # 发送请求获取返回值

    # 返回
    return HttpResponse('{"code":200}')
