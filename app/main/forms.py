# This Python file uses the following encoding: utf-8
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

from flask.ext.wtf import Form
from flask.ext.pagedown.fields import PageDownField
from wtforms import StringField, TextAreaField, BooleanField, SelectField,SubmitField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User

class EditProfileForm(Form):
    name = StringField('姓名',validators = [Length(0,64)])
    location = StringField('所在地点', validators = [Length(0,64)])
    about_me = TextAreaField('自我介绍')
    submit = SubmitField('确定')
    
class EditProfileAdminForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),Email()])
    username = StringField('用户名', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'用户名必须由字母、数字、点及下划线组成')])
    confirmed = BooleanField('已验证')
    role = SelectField('角色', coerce=int)
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('所在地点', validators=[Length(0, 64)])
    about_me = TextAreaField('自我介绍')
    submit = SubmitField('确定')    
    
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user
    
    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')
    
    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被使用')    
        
class PostForm(Form):
    title = TextAreaField('标题',validators =[Required()])
    digest = TextAreaField('摘要',validators = [Required()])
    body = PageDownField('内容',validators = [Required()])
    submit = SubmitField('提交')
    
class CommentForm(Form):
    body = TextAreaField('', validators=[Required()])
    submit = SubmitField('Submit')    