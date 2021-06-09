from dqm import app
from flask import render_template, redirect, url_for, flash, request
from dqm.models import User, MetaData
from dqm.forms import RegisterForm, LoginForm, FileBrowser, FileUpload, NoAction, RemoveDataSet
from werkzeug.utils import secure_filename
from dqm import db
from flask_login import login_user, logout_user, login_required, current_user
import pandas as pd
from .function import get_summary, get_data_sources_name
import shutil

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/dqm', methods=['GET', 'POST'])
@login_required
def dqm_page():

    global df_stat
    global file_name
    form_browser = FileBrowser()
    form_upload = FileUpload()
    form_no_action = NoAction()
    remove_data_set = RemoveDataSet()

    if request.method == 'POST':

        # Browse file
        file_browser = request.form.get('file_browser')
        if file_browser:
            file_name = secure_filename(form_browser.input_file.data.filename)

            # Upload file to the directed
            form_browser.input_file.data.save('datas/' + file_name)
            form_browser.input_file.data.stream.seek(0)
            df = pd.read_csv(form_browser.input_file.data, sep=";", encoding='latin-1')

            # get statistics from dataframe
            df_stat = get_summary(df)

            # query all sources
            data_sets = MetaData.query.all()


            return render_template('dqm.html',
                                   file_name=file_name,
                                   form_browser=form_browser,
                                   form_upload=form_upload,
                                   form_no_action=form_no_action,
                                   remove_data_set=remove_data_set,
                                   data_sets=data_sets,
                                   eda=[df_stat.to_html(classes='table table-hover table-dark text-center',
                                                        header=True)])

        # Upload file
        file_upload = request.form.get('file_upload')
        if file_upload:
            # create new db entity
            data_metaclass = MetaData(
                name=form_upload.name.data,
                column_num=df_stat.iloc[0, 1],
                row_num=df_stat.iloc[1, 1],
                unique_row_num=df_stat.iloc[2, 1],
                unique_row_rate=df_stat.iloc[3, 1],
                filled_row_num=df_stat.iloc[4, 1],
                filled_row_rate=df_stat.iloc[5, 1],
                missing_row_num=df_stat.iloc[6, 1],
                missing_row_rate=df_stat.iloc[7, 1]
            )

            db.session.add(data_metaclass)
            db.session.commit()

            # Update info list and select drop down list
            data_sets = MetaData.query.all()
            remove_data_set.select_data.choices = get_data_sources_name()

            # Move files to datas directory
            print(type(file_name))
            # with file_name.read():
            #     df = pd.read_csv(file_name)
            #     df.to_csv(f'./datas/{form_upload.name.data}', index_col=False)

            return render_template('dqm.html',
                                   form_browser=form_browser,
                                   form_upload=form_upload,
                                   form_no_action=form_no_action,
                                   remove_data_set=remove_data_set,
                                   data_sets=data_sets
                                   )

        # No action
        file_no_action = request.form.get('file_no_action')
        if file_no_action:
            return redirect(url_for('dqm_page'))

        # Features - drop data set
        remove_data = request.form.get('remove_data_set')
        if remove_data:

            # Select drop down element
            element = request.form.get('select_data')

            # query db record
            db_record = MetaData.query.filter_by(name=element).first()

            # Delete element
            db.session.delete(db_record)
            db.session.commit()

            # Update info list and select drop down list
            remove_data_set.select_data.choices = get_data_sources_name()
            data_sets = MetaData.query.all()

            return render_template('dqm.html',
                                   form_browser=form_browser,
                                   form_upload=form_upload,
                                   form_no_action=form_no_action,
                                   remove_data_set=remove_data_set,
                                   data_sets=data_sets
                                   )


    if request.method == 'GET':
        data_sets = MetaData.query.all()
        return render_template('dqm.html',
                                       form_browser=form_browser,
                                       form_upload=form_upload,
                                       form_no_action=form_no_action,
                                       remove_data_set=remove_data_set,
                                       data_sets=data_sets
                                       )




@app.route('/register', methods=['POST', 'GET'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Account created successfully! You are now logged in as {user_to_create.username}', category='success')
        return redirect(url_for('dqm_page'))
    if form.errors != {}: #Error occured during the validation
        for err_msg in form.errors.values():
            flash(f'There was an error during creating the user: {err_msg}', category='danger')
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success. You are logged in as {attempted_user.username}', category='success')
            return redirect(url_for('dqm_page'))
        else:
            flash('Username and password does not match! Please try again!', category='danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for('home_page'))

