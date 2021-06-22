from dqm import app
from flask import render_template, redirect, url_for, flash, request
from dqm.models import User, MetaData, TableData
from dqm.forms import RegisterForm, LoginForm, FileBrowser, FileUpload, NoAction, RemoveDataSet, RemoveDuplication,\
    SortDataSet, JoinDataSets, RemoveCells
from werkzeug.utils import secure_filename
from dqm import db
from flask_login import login_user, logout_user, login_required, current_user
import pandas as pd
from .function import get_summary, get_data_sources_name, get_separator

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/dqm', methods=['GET', 'POST'])
@login_required
def dqm_page():

    global df
    global df_stat
    global file_name

    form_browser = FileBrowser()
    form_upload = FileUpload()
    form_no_action = NoAction()
    remove_data_set = RemoveDataSet()
    remove_duplication = RemoveDuplication()
    sort_data_set = SortDataSet()
    join_data_sets = JoinDataSets()
    remove_cells = RemoveCells()

    if request.method == 'POST':

        # feature - browse file
        file_browser = request.form.get('file_browser')
        if file_browser:
            file_name = secure_filename(form_browser.input_file.data.filename)

            # Upload file to the directed
            form_browser.input_file.data.save('datas/' + file_name)
            form_browser.input_file.data.stream.seek(0)

            df = pd.read_csv(form_browser.input_file.data, delimiter=get_separator(file_name))

            # get statistics of the examined dataframe
            df_stat = get_summary(df)

            # query all sources
            data_sets = MetaData.query.all()

            return render_template('dqm.html',
                                   file_name=file_name,
                                   form_browser=form_browser,
                                   form_upload=form_upload,
                                   form_no_action=form_no_action,
                                   remove_data_set=remove_data_set,
                                   remove_duplication=remove_duplication,
                                   sort_data_set=sort_data_set,
                                   data_sets=data_sets,
                                   join_data_sets=join_data_sets,
                                   remove_cells=remove_cells,
                                   eda=[df_stat.to_html(classes='table table-hover table-dark text-center',
                                                        header=True)])

        # feature - Upload file
        file_upload = request.form.get('file_upload')
        if file_upload:
            # create new db entity
            data_metaclass = MetaData(
                name=form_upload.name.data,
                physical_name=file_name,
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

            # adding column name - column types in loop
            for column in df:
                if df.dtypes[column] in ['int16', 'int32', 'int64']:
                    column_type = 'INT'
                elif df.dtypes[column] in ['float16', 'float32', 'float64']:
                    column_type = 'FLOAT'
                elif df.dtypes[column]  == 'datetime64':
                    column_type = 'DATE'
                elif df.dtypes[column] == 'object':
                    column_type = 'STRING'

                # print(f'Column name: {column} - Column type: {column_type}')
                data_tableclass = TableData(
                    related_metadata_name=form_upload.name.data,
                    column_name=column,
                    column_type=column_type
                )

                db.session.add(data_tableclass)
                db.session.commit()

            # Update info list and select drop down list
            data_sets = MetaData.query.all()
            remove_data_set.select_removeable_dataset.choices = get_data_sources_name()
            remove_duplication.select_duplication_dataset.choices = get_data_sources_name()
            sort_data_set.select_sort_dataset.choices = get_data_sources_name()
            join_data_sets.select_dataset_1.choices = get_data_sources_name()
            join_data_sets.select_dataset_2.choices = get_data_sources_name()
            remove_cells.select_dataset_remove_cells.choices = get_data_sources_name()

            # Move files to datas directory
            # print(type(file_name))
            # with file_name.read():
            #     df = pd.read_csv(file_name, delimiter='[;|,]', engine='python')
            #     df.to_csv(f'./datas/{form_upload.name.data}', index_col=False, sep=',')

            return render_template('dqm.html',
                                   form_browser=form_browser,
                                   form_upload=form_upload,
                                   form_no_action=form_no_action,
                                   remove_data_set=remove_data_set,
                                   remove_duplication=remove_duplication,
                                   sort_data_set=sort_data_set,
                                   data_sets=data_sets,
                                   join_data_sets=join_data_sets,
                                   remove_cells=remove_cells
                                   )

        # feature - No action
        file_no_action = request.form.get('file_no_action')
        if file_no_action:
            return redirect(url_for('dqm_page'))

        # Feature - drop data set
        remove_data = request.form.get('remove_data_set')
        if remove_data:

            # Select drop down element
            element = request.form.get('select_removeable_dataset')

            # query db record
            db_record = MetaData.query.filter_by(name=element).first()

            # Delete elements
            db.session.delete(db_record)
            db.session.commit()

            # Update info list and select drop down list
            remove_data_set.select_removeable_dataset.choices = get_data_sources_name()
            remove_duplication.select_duplication_dataset.choices = get_data_sources_name()
            sort_data_set.select_sort_dataset.choices = get_data_sources_name()
            join_data_sets.select_dataset_1.choices = get_data_sources_name()
            join_data_sets.select_dataset_2.choices = get_data_sources_name()
            remove_cells.select_dataset_remove_cells.choices = get_data_sources_name()

            data_sets = MetaData.query.all()

            return render_template('dqm.html',
                                   form_browser=form_browser,
                                   form_upload=form_upload,
                                   form_no_action=form_no_action,
                                   remove_data_set=remove_data_set,
                                   remove_duplication=remove_duplication,
                                   sort_data_set=sort_data_set,
                                   data_sets=data_sets,
                                   join_data_sets=join_data_sets,
                                   remove_cells=remove_cells
                                   )

        # Feature - drop duplication
        remove_duplication_form = request.form.get('remove_duplication')
        if remove_duplication_form:

            # Select drop down element
            element = request.form.get('select_duplication_dataset')

            # filter data - from MetaData class identify the correct class
            selected_dataset = MetaData.query.filter_by(name=element).first().physical_name

            # get path and file for reading and saving
            path_and_file = '/'.join(['datas', selected_dataset])

            # reading the dataframe
            df = pd.read_csv(path_and_file, encoding='utf-8-sig', delimiter=get_separator(selected_dataset))

            df = df.drop_duplicates()
            df.to_csv(path_or_buf=path_and_file, index=False, encoding='utf-8-sig')

            # get statistics of the examined dataframe
            df_stat = get_summary(df)

            # update MetaData Class in db
            data_metaclass = MetaData.query.filter_by(name=element).first()

            data_metaclass.row_num = df_stat.iloc[1, 1]
            data_metaclass.unique_row_num = df_stat.iloc[2, 1]
            data_metaclass.unique_row_rate = df_stat.iloc[3, 1]
            data_metaclass.filled_row_num = df_stat.iloc[4, 1]
            data_metaclass.filled_row_rate = df_stat.iloc[5, 1]
            data_metaclass.missing_row_num = df_stat.iloc[6, 1]
            data_metaclass.missing_row_rate = df_stat.iloc[7, 1]

            db.session.commit()

            # getting datas
            data_sets = MetaData.query.all()

            return render_template('dqm.html',
                                   form_browser=form_browser,
                                   form_upload=form_upload,
                                   form_no_action=form_no_action,
                                   remove_data_set=remove_data_set,
                                   remove_duplication=remove_duplication,
                                   sort_data_set=sort_data_set,
                                   data_sets=data_sets,
                                   join_data_sets=join_data_sets,
                                   remove_cells=remove_cells
                                   )

        # Feature - sort data set
        sort_data_set_form = request.form.get('sort_data_set')
        if sort_data_set_form:

            # Select drop down element
            element = request.form.get('select_sort_dataset')
            sort_by_col = request.form.get('col_name')
            sort_mode = request.form.get('sort_mode')
            sort_lst = []

            # create 'by' variable for sort_values function
            if ',' in sort_by_col:
                for i in sort_by_col.split(','):
                    sort_lst.append(i)
            else:
                sort_lst.append(sort_by_col)

            # filter data - from MetaData class identify the correct class
            selected_dataset = MetaData.query.filter_by(name=element).first().physical_name

            # get path and file for reading and saving
            path_and_file = '/'.join(['datas', selected_dataset])

            # reading the dataframe
            df = pd.read_csv(path_and_file, encoding='utf-8-sig', delimiter=get_separator(selected_dataset))

            # sort values
            df.sort_values(by=sort_lst, inplace=True, ascending=True if sort_mode == 'Nővekvő' else False)

            # save new dataset
            df.to_csv(path_or_buf=path_and_file, index=False, encoding='utf-8-sig')

            # getting datas
            data_sets = MetaData.query.all()
            return render_template('dqm.html',
                                   form_browser=form_browser,
                                   form_upload=form_upload,
                                   form_no_action=form_no_action,
                                   remove_data_set=remove_data_set,
                                   remove_duplication=remove_duplication,
                                   sort_data_set=sort_data_set,
                                   data_sets=data_sets,
                                   join_data_sets=join_data_sets,
                                   remove_cells=remove_cells
                                   )

        # Feature - join datasets
        join_data_sets_form = request.form.get('join_data_sets')
        if join_data_sets_form:

            # create variables from Form elements
            dataset_1 = request.form.get('select_dataset_1')
            dataset_2 = request.form.get('select_dataset_2')
            join_col_name_dataset_1 = request.form.get('join_col_name_dataset_1')
            join_col_name_dataset_2 = request.form.get('join_col_name_dataset_2')
            join_mode = request.form.get('join_mode')
            new_dataset_name = request.form.get('new_dataset_name')
            new_dataset_physical_name = request.form.get('new_dataset_physical_name')

            # filter data - from MetaData class identify the correct rows
            dataset_1 = MetaData.query.filter_by(name=dataset_1).first().physical_name
            dataset_2 = MetaData.query.filter_by(name=dataset_2).first().physical_name

            # get path and file for reading and saving
            path_and_file_1 = '/'.join(['datas', dataset_1])
            path_and_file_2 = '/'.join(['datas', dataset_2])

            # reading the dataframe - these dataframes will construct as left and right side of the join
            df_left = pd.read_csv(path_and_file_1, index_col=False, delimiter=get_separator(dataset_1))
            df_right = pd.read_csv(path_and_file_2, index_col=False, delimiter=get_separator(dataset_2))

            if join_mode == 'LEFT':
                df = pd.merge(df_left, df_right, how='left', left_on=join_col_name_dataset_1,
                              right_on=join_col_name_dataset_2)
            elif join_mode == 'INNER':
                df = pd.merge(df_left, df_right, how='inner', left_on=join_col_name_dataset_1,
                              right_on=join_col_name_dataset_2)
            elif join_mode == 'RIGHT':
                df = pd.merge(df_left, df_right, how='right', left_on=join_col_name_dataset_1,
                              right_on=join_col_name_dataset_2)
            elif join_mode == 'OUTER':
                df = pd.merge(df_left, df_right, how='outer', left_on=join_col_name_dataset_1,
                              right_on=join_col_name_dataset_2)

            # get statistics of the examined dataframe
            df_stat = get_summary(df)

            # create new db entity
            data_metaclass = MetaData(
                name=new_dataset_name,
                physical_name=new_dataset_physical_name,
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

            # adding column name - column types in loop
            for column in df:
                if df.dtypes[column] in ['int16', 'int32', 'int64']:
                    column_type = 'INT'
                elif df.dtypes[column] in ['float16', 'float32', 'float64']:
                    column_type = 'FLOAT'
                elif df.dtypes[column] == 'datetime64':
                    column_type = 'DATE'
                elif df.dtypes[column] == 'object':
                    column_type = 'STRING'

                # print(f'Column name: {column} - Column type: {column_type}')
                data_tableclass = TableData(
                    related_metadata_name=new_dataset_name,
                    column_name=column,
                    column_type=column_type
                )

                db.session.add(data_tableclass)
                db.session.commit()

            # save output physically
            # get path and filename for new merged dataframe
            path_and_file = '/'.join(['datas', new_dataset_physical_name])
            if 'csv' in new_dataset_physical_name:
                df.to_csv(path_and_file, encoding='utf-8-sig', index=False)
            elif 'xlsx' in new_dataset_physical_name:
                df.to_excel(path_and_file, encoding='utf-8-sig', index=False)
            else:
                print('Nem megfelelő jelenlegi output típus!')
                pass

            # Update info list and select drop down list
            data_sets = MetaData.query.all()
            remove_data_set.select_removeable_dataset.choices = get_data_sources_name()
            remove_duplication.select_duplication_dataset.choices = get_data_sources_name()
            sort_data_set.select_sort_dataset.choices = get_data_sources_name()
            join_data_sets.select_dataset_1.choices = get_data_sources_name()
            join_data_sets.select_dataset_2.choices = get_data_sources_name()
            remove_cells.select_dataset_remove_cells.choices = get_data_sources_name()

            return render_template('dqm.html',
                                   form_browser=form_browser,
                                   form_upload=form_upload,
                                   form_no_action=form_no_action,
                                   remove_data_set=remove_data_set,
                                   remove_duplication=remove_duplication,
                                   sort_data_set=sort_data_set,
                                   data_sets=data_sets,
                                   join_data_sets=join_data_sets,
                                   remove_cells=remove_cells
                                   )

        # feature - remove cells
        remove_cells_form = request.form.get('remove_cells')
        if remove_cells_form:

            # create variables from Form elements
            dataset = request.form.get('select_dataset_remove_cells')
            removeable_columns = request.form.get('select_removeable_cells')

            removeable_columns_lst = []

            # remove TableData cell from db
            def remove_cell_from_table_data(dataset_name: str, column_name: str) -> None:

                # select TableData column
                db_record = TableData.query.filter_by(related_metadata_name=dataset_name, column_name=column_name)\
                    .first()

                # Delete column
                db.session.delete(db_record)
                db.session.commit()

            # create removeable columsns list for 'drop' function
            if ',' in removeable_columns:
                for column in removeable_columns.split(','):
                    removeable_columns_lst.append(column)

                    # remove cells from TableData
                    remove_cell_from_table_data(dataset_name=dataset, column_name=column)

            else:
                removeable_columns_lst.append(removeable_columns)

                # remove cells from TableData
                remove_cell_from_table_data(dataset_name=dataset, column_name=removeable_columns)

            # filter data - from MetaData class identify the correct class
            selected_dataset = MetaData.query.filter_by(name=dataset).first().physical_name

            # get path and file for reading and saving
            path_and_file = '/'.join(['datas', selected_dataset])

            # reading the dataframe
            df = pd.read_csv(path_and_file, encoding='utf-8-sig', delimiter=get_separator(selected_dataset))

            # drop cells from dataframe
            df.drop(columns=removeable_columns_lst, axis=1, inplace=True)

            # get statistics of the examined dataframe
            df_stat = get_summary(df)

            # update MetaData Class in db
            data_metaclass = MetaData.query.filter_by(name=dataset).first()

            data_metaclass.column_num = df_stat.iloc[0, 1]
            data_metaclass.row_num = df_stat.iloc[1, 1]
            data_metaclass.unique_row_num = df_stat.iloc[2, 1]
            data_metaclass.unique_row_rate = df_stat.iloc[3, 1]
            data_metaclass.filled_row_num = df_stat.iloc[4, 1]
            data_metaclass.filled_row_rate = df_stat.iloc[5, 1]
            data_metaclass.missing_row_num = df_stat.iloc[6, 1]
            data_metaclass.missing_row_rate = df_stat.iloc[7, 1]

            db.session.commit()

            # save new dataset
            df.to_csv(path_or_buf=path_and_file, index=False, encoding='utf-8-sig')

            data_sets = MetaData.query.all()

            # Update info list and select drop down list
            remove_data_set.select_removeable_dataset.choices = get_data_sources_name()
            remove_duplication.select_duplication_dataset.choices = get_data_sources_name()
            sort_data_set.select_sort_dataset.choices = get_data_sources_name()
            join_data_sets.select_dataset_1.choices = get_data_sources_name()
            join_data_sets.select_dataset_2.choices = get_data_sources_name()
            remove_cells.select_dataset_remove_cells.choices = get_data_sources_name()

            return render_template('dqm.html',
                                   form_browser=form_browser,
                                   form_upload=form_upload,
                                   form_no_action=form_no_action,
                                   remove_data_set=remove_data_set,
                                   remove_duplication=remove_duplication,
                                   sort_data_set=sort_data_set,
                                   data_sets=data_sets,
                                   join_data_sets=join_data_sets,
                                   remove_cells=remove_cells
                                   )


    if request.method == 'GET':
        data_sets = MetaData.query.all()
        return render_template('dqm.html',
                                       form_browser=form_browser,
                                       form_upload=form_upload,
                                       form_no_action=form_no_action,
                                       remove_data_set=remove_data_set,
                                       remove_duplication=remove_duplication,
                                       sort_data_set=sort_data_set,
                                       data_sets=data_sets,
                                       join_data_sets=join_data_sets,
                                       remove_cells=remove_cells
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

