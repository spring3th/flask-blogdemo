# This Python file uses the following encoding: utf-8
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(Form):#用户登陆
    email = StringField('邮箱', validators=[Required(),Length(1, 64), Email()])
    password =PasswordField('密码', validators=[Required()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登陆')
    
class RegistrationForm(Form):#注册用户
    email = StringField('邮箱', validators=[Required(), Length(1, 64),Email()])
    username = StringField('用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          '用户名只能包含字母、数字、点或者下划线')])    
    password = PasswordField('密码', validators=[Required(), EqualTo('password2',message='密码不一致')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('注册')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')
        
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被使用')
        
class ChangePasswordForm(Form):
    old_password = PasswordField('原密码', validators=[Required()])
    new_password = PasswordField('新密码', validators=[Required(), EqualTo('password2',message='两次输入密码不一致')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('确认')

class ChangeUsernameForm(Form):
    old_username = StringField('原用户名', validators=[Required(),Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'用户名只能包含字母、数字、点或者下划线')])
    new_username = StringField('新用户名', validators=[Required(),Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'用户名只能包含字母、数字、点或者下划线')])
    submit = SubmitField('确认')
    

class PasswordResetRequestForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                             Email()])
    submit = SubmitField('找回密码')


class PasswordResetForm(Form):
    email = StringField('验证邮箱', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='两次输入不一致')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('确认')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('邮箱无效')
        
        
class ChangeEmailForm(Form):
    email = StringField('新邮箱',validators=[Required(), Length(1,64),Email()])
    password = PasswordField('密码',validators=[Required()])
    submit = SubmitField('确认')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')