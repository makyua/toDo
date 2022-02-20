#models.py
from flaskr import db, login_manager
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin

from datetime import datetime, timedelta
from uuid import uuid4 #uuidを作成するためのライブラリー、uuidはパスワードを作成する際などに便利な機能

# 認証ユーザーの呼び出し方を定義する⇒認証したいページに@login_requiredデコレートする
# さらにログインページのviewではis_authenticated()メソッドでログインの有無を確認できるので便利
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# flask_loginのuserMixinを継承したUserクラスを作る
class User(UserMixin, db.Model):
    
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True, index=True) #unique=Tにより、1つのemailは1つしか登録できない。同じemailのユーザーが登録できない。
    password = db.Column(
        db.String(128), 
        default=generate_password_hash('dbflaskapp') #デフォルトのパスワードとして、ユーザーが後で変更する
        )
    # 有効か無効かのフラグ
    is_active = db.Column(db.Boolean, unique=False, default=False)
    create_at = db.Column(db.DateTime, default=datetime.now)
    # カラムを追加したときに自動で作成される、管理者や運用の人がいつ更新されたかなどの流れを確認できる
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    @classmethod
    def select_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first() #カラムemailがemailのデータのみに絞り込み、SELECT+WHERE

    def validate_password(self, password):
        return check_password_hash(self.password, password) #self.passwordはテーブルに保持されているハッシュ化された値
    
    def create_new_user(self):
        db.session.add(self)

    @classmethod
    def select_user_by_id(cls, id):
        return cls.query.get(id)

    def save_new_password(self, new_password):
        self.password = generate_password_hash(new_password)
        self.is_active = True

    @classmethod
    def delete_user(cls, id):
        cls.query.filter_by(id=int(id)).delete()

#パスワードをリセットするときに利用する
class PasswordResetToken(db.Model):

    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(
        db.String(64),
        unique=True,
        index=True,
        server_default=str(uuid4) #ランダムにuuidの値を生成するのでそれを文字列型に変換してデフォルトにする
    )
    #uer tableに紐づける際に利用する外部キー
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    #Tokenが有効な時間
    expire_at = db.Column(db.DateTime, default=datetime.now)
    # カラムを追加したときに自動で作成される、管理者や運用の人がいつ更新されたかなどの流れを確認できる
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)
    
    def __init__(self, token, user_id, expire_at):
        self.token = token
        self.user_id = user_id
        self.expire_at = expire_at

    @classmethod
    #パスワードを設定用のURLを生成
    def publish_token(cls, user):
        token = str(uuid4())
        new_token = cls(
            token, 
            user.id,
            #パスワードの設定期限を明日までに設定する
            datetime.now() + timedelta(days=1)
        )
        db.session.add(new_token)
        return token
    
    @classmethod
    def get_user_id_by_token(cls, token):
        now = datetime.now()
        #tokenを使った絞り込みと有効期限が切れていないことの確認
        record = cls.query.filter_by(token=str(token)).filter(cls.expire_at > now).first()
        if record:
            return record.user_id
        else:
            return None

    @classmethod
    def delete_token(cls, token):
        cls.query.filter_by(token=str(token)).delete()

# 会社
class Company(db.Model):

    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), index=True
    ) #誰が記入した企業研究結果か
    comname = db.Column(db.String(64), index=True)
    wishpoint = db.Column(db.Integer)
    step = db.Column(db.String(64))
    scale = db.Column(db.Integer)
    startmoney = db.Column(db.Integer)
    numemploy = db.Column(db.Integer)
    comment = db.Column(db.Text)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(
        self, from_user_id, comname, wishpoint,
        step, scale, startmoney, numemploy, comment
        ):
        self.from_user_id = from_user_id
        self.comname = comname
        self.wishpoint = wishpoint
        self.step = step
        self.scale = scale
        self.startmoney = startmoney
        self.numemploy = numemploy
        self.comment = comment

    # データベース追加用
    def create_new_company(self):
        db.session.add(self)
    
    @classmethod
    def select_company_by_comname(cls, id):
        return cls.query.get(id)

    # ユーザーが作成した情報をすべて取得
    @classmethod
    def select_company_by_user_id(cls, id):
        return cls.query.filter_by(from_user_id=id).all()
    
    # idから一つだけ情報を取得
    @classmethod
    def select_company_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    # 会社名から検索
    @classmethod
    def search_by_comname(cls, comname, id):
        return cls.query.filter(
            cls.comname.like(f'%{comname}%'),
            cls.from_user_id == int(id)
        ).all()

    # idから会社の情報の削除、本当はユーザーのIDと会社情報を登録したユーザーのIDと等しいか検証
    @classmethod
    def delete_company(cls, id):
        cls.query.filter_by(id=int(id)).delete()