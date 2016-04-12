# This Python file uses the following encoding: utf-8
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
    
from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required,current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, ChangeUsernameForm,PasswordResetRequestForm,PasswordResetForm,ChangeEmailForm


@auth.before_app_request
def before_request():
    if current_user.is_authenticated():
        current_user.ping()
    #(1) 用户已登录( current_user.is_authenticated() 必须返回 True )。
    #(2) 用户的账户还未确认。
    #(3) 请求的端点(使用 request.endpoint 获取)不在认证蓝本中。访问认证路由要获取权
    #限,因为这些路由的作用是让用户确认账户或执行其他账户管理操作。
    if current_user.is_authenticated() \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))
    
@auth.route('/unconfirmed')
def unconfirmed():#为验证邮箱状态
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():#登陆
    if current_user.is_authenticated():
        flash('你已登陆请勿重复登陆')
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('无效的用户名或密码错误')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():#登出
    logout_user()
    flash('已退出登陆')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():#注册
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, '验证你的邮箱','auth/email/confirm', user=user, token=token)
        flash('你已成功注册')
        flash('一封验证邮件已发往你的邮箱，请验证')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):#验证邮箱
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('你已成功验证邮箱，谢谢')
    else:
        flash('此验证信息无效或已过期')
    return redirect(url_for('main.index'))

@auth.route('/confirm')
@login_required
def resend_confirmation():#重新发送验证邮件
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '验证你的邮箱','auth/email/confirm', user=current_user, token=token)
    flash('一封验证邮件已发往你的邮箱')
    return redirect(url_for('main.index'))

@auth.route('/change-password',methods = ['GET','POST'])
@login_required
def change_password():#修改密码
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            flash('密码已修改')
        else:
            flash('密码错误或无效')
    return render_template('auth/change_password.html', form=form)
    
@auth.route('/change-username',methods = ['GET','POST'])
@login_required
def change_username():#修改用户名
    form = ChangeUsernameForm()
    if form.validate_on_submit():
        if not User.query.filter_by(username=form.new_username.data).first():
            current_user.username = form.new_username.data
            db.session.add(current_user)
            flash('用户名已修改')
        else:
            flash('新用户名已被占用')
    form.old_username.data = current_user.username
    return render_template('auth/change_username.html', form=form)

@auth.route('/reset-password', methods=['GET','POST'])
def password_reset_request():
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, '找回密码',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('一封用于找回密码的邮件已发送至你的邮箱')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('密码已修改')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)
    
@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, '确认新邮箱',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('一封用于验证新邮箱的邮件已发出，请注意查收')
            return redirect(url_for('main.index'))
        else:
            flash('无效的邮箱或密码错误')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('邮箱地址已更新')
    else:
        flash('无效的请求')
    return redirect(url_for('main.index')) 