# forms.py
from wtforms.form import Form
from wtforms.fields import (
    StringField, PasswordField, SubmitField, HiddenField,
    TextAreaField, IntegerField, SelectField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo,
    NumberRange
)
from wtforms import ValidationError

from flask_login import current_user
from flask import flash

from flaskr.models import User, Company

#ログイン用のForm
class LoginForm(Form):
    email = StringField(
        'メール: ', validators=[DataRequired(), Email()]
        )
    password = PasswordField(
        'パスワード: ', 
        validators=[DataRequired(), 
        EqualTo('confirm_password', message="パスワードが一致しません")]
        )
    confirm_password = PasswordField(
        'パスワード再入力: ', validators=[DataRequired()]
        )
    submit = SubmitField('ログイン')

#登録用のForm
class RegisterForm(Form):
    email = StringField(
        'メール: ', validators=[DataRequired(), Email('メールアドレスが間違っています')]
        )
    username = StringField('名前: ', validators=[DataRequired()])
    submit = SubmitField('登録')

    #同じメールアドレスの人が登録されないように自作バリデーション
    def validate_email(self, field):
        #クライアントが入力したユーザーと同じユーザーがいないか引っ張り出す
        if User.select_user_by_email(field.data):
            raise ValidationError('メールアドレスは既に登録されています')

#パスワード設定用のフォーム
class ResetPasswordForm(Form):
    password = PasswordField(
        'パスワード: ',
        validators=[DataRequired(), EqualTo('confirm_password', message='パスワードが一致しません')]
    )
    confirm_password = PasswordField(
        'パスワード確認: ', validators=[DataRequired()]
        )
    submit = SubmitField('パスワードを更新する')
    #パスワードの長さを8文字以上にする
    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('パスワードは8文字以上です')

# ユーザーの情報を編集する
class UserForm(Form):
    email = StringField(
        'メール: ', validators=[DataRequired(), Email('メールアドレスが誤っています')]
    )
    username = StringField('名前: ', validators=[DataRequired()])
    submit = SubmitField('登録情報更新')

    #全体のバリデーション
    def validate(self):
        if not super(Form, self).validate():
            return False
        #メールアドレスが既に存在していないかの確認
        #追加でもし存在していても今ログインしているユーザーと同じならエラーにはしない
        user = User.select_user_by_email(self.email.data)
        if user:
            if user.id != int(current_user.get_id()):
                flash('そのメールアドレスは既に登録されています')
                return False
        return True

# パスワード変更時のフォーム
class ChangePasswordForm(Form):
    password = PasswordField(
        'パスワード',
        validators=[DataRequired(), EqualTo('confirm_password', message='パスワードが一致しません')]
    )
    confirm_password = PasswordField(
        'パスワード確認: ', validators=[DataRequired()]
    )
    submit = SubmitField('パスワードの更新')
    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('パスワードは8文字以上です')

# 会社名の登録と編集用のフォーム
class CompanyForm(Form):
    from_user_id = HiddenField()
    comname = StringField('会社名: ', validators=[DataRequired()])
    wishpoint = IntegerField('志望度: ', validators=[NumberRange(0, 100, '不正な値です')])
    step = SelectField('選考段階: ', choices=[('', ''), ('選考前', '選考前'), ('会社説明後', '会社説明後'), ('ES提出後', 'ES提出後'), ('1次面接後', '1次面接後'), ('2次面接後', '2次面接後'), ('最終面接後', '最終面接後'), ('内定獲得', '内定獲得'), ('辞退/不合格', '辞退/不合格')])
    scale = StringField('規模感: ')
    startmoney = IntegerField('資本金: ')
    numemploy = IntegerField('従業員数: ')
    comment = TextAreaField('コメント: ')
    submit = SubmitField('登録')

    # 同じ会社名を登録できないようにバリデーション
    def validate_comname(self, field):
        if Company.select_company_by_comname(field.data):
            raise ValidationError('その会社名は既に登録されてあります')

# 会社名の検索
class CompanySearchForm(Form):
    comname = StringField('会社名: ')
    submit = SubmitField('会社名検索')

