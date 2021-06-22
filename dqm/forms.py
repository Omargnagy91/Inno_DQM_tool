from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, SelectField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError, InputRequired, Required
from dqm.models import User, MetaData
from dqm.function import get_data_sources_name

class RegisterForm(FlaskForm):

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username!')

    def validate_email_address(self, email_address_to_check):
        email = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email:
            raise ValidationError('Email address already exists! Please try a different email address!')

    username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    username = StringField(label="User Name:", validators=[DataRequired()])
    password = PasswordField(label="Password:", validators=[DataRequired()])
    submit = SubmitField(label='Sign in')

class FileBrowser(FlaskForm):
    input_file = FileField(label="Fájl Neve...")
    submit = SubmitField(label="Feltöltés")

class FileUpload(FlaskForm):
    name = StringField([InputRequired()], render_kw={"placeholder": "Adatforrás azonosítója"})
    submit = SubmitField(label="Feltöltés")

class NoAction(FlaskForm):
    submit = SubmitField(label="Törlés")

class RemoveDataSet(FlaskForm):

    select_removeable_dataset = SelectField(u'Field name', choices=get_data_sources_name(), validators=[Required()])
    submit = SubmitField(label='Adatforrás eltávolítás')

class RemoveDuplication(FlaskForm):

    select_duplication_dataset = SelectField(u'Field name', choices=get_data_sources_name(), validators=[Required()])
    select_duplication_dataset_mode = SelectField(u'Field name', choices=['Első', 'Utolsó', '-'],
                                                  validators=[Required()])
    col_name = StringField(label="Oszlop neve - (üresen hagyva a teljes sor duplikáció kerül vizsgálatra")
    submit = SubmitField(label='Duplikáció eltávolítás')

class SortDataSet(FlaskForm):
    select_sort_dataset = SelectField(u'Field name', choices=get_data_sources_name(), validators=[Required()])
    col_name = StringField(label="Oszlop/Oszlopok neve, ami alapján a sorbarendezés megtörténik ")
    sort_mode = SelectField(u'Field name', choices=['Csökkenő', 'Nővekvő'],
                                                  validators=[Required()])
    submit = SubmitField(label='Sorbarendezés elvégzése')

class JoinDataSets(FlaskForm):
    select_dataset_1 = SelectField(u'Dataset 1 name', choices=get_data_sources_name(), validators=[Required()])
    select_dataset_2 = SelectField(u'Dataset 2 name', choices=get_data_sources_name(), validators=[Required()])
    join_col_name_dataset_1 = StringField(label="Első dataset join mezője", validators=[Required()])
    join_col_name_dataset_2 = StringField(label="Első dataset join mezője", validators=[Required()])
    join_mode = SelectField(u'Dataset 2 name', choices=['INNER', 'LEFT', 'RIGHT', 'OUTER'], validators=[Required()])
    new_dataset_name = StringField(label="Új adatforrás db azonosítója", validators=[Required()])
    new_dataset_physical_name = StringField(label="Új adatforrás fizikai neve", validators=[Required()])
    submit = SubmitField(label='Összekapcsolás elvégzése')

class RemoveCells(FlaskForm):
    select_dataset_remove_cells = SelectField(u'Field name', choices=get_data_sources_name(), validators=[Required()])
    select_removeable_cells = StringField(label="Törölhető mezők neve vesszővel elválasztva", validators=[Required()])
    submit = SubmitField(label='Adatforrás eltávolítás')