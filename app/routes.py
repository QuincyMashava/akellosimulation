from datetime import datetime, timezone
from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, AddNewSchoolTrackerForm, TaskForm, WorkspaceForm
from app.models import User,SchoolTracker,Task, Workspace, Scorecard, WorkstreamsReport, TargetsReport, Notifications
import uuid as uuid
import os
import io
import pandas as pd
from werkzeug.utils import secure_filename



@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    username=current_user.username
    role=current_user.role
    user_notifications = Notifications.query.filter(Notifications.read == False)
    your_tasks = Task.query.filter(Task.assigned_to == current_user.username, Task.status == 'Pending' )
    return render_template('index.html',username=username,role=role,user_notifications=user_notifications,your_tasks=your_tasks, title='Home')


@app.route('/metrics', methods=['GET', 'POST'])
@login_required
def metrics():
    username=current_user.username
    role=current_user.role
    return render_template('key_metrics.html',username=username,role=role, title='Key Metrics')


@app.route('/contracting', methods=['GET', 'POST'])
@login_required
def contracting():
    username = current_user.username
    role = current_user.role
    scorecards = Scorecard.query.filter_by(employee_name=username).all()
    return render_template('contracting.html', username=username, role=role, title='Contracting', scorecards=scorecards)


@app.route('/save_scorecard', methods=['POST'])
def save_scorecard():
    key_focus_areas = request.form.getlist('keyFocusArea[]')
    strategic_objectives = request.form.getlist('strategicObjective[]')
    performance_measures = request.form.getlist('performanceMeasure[]')
    unit_of_measures = request.form.getlist('unitOfMeasure[]')
    targets = request.form.getlist('target[]')
    weights = request.form.getlist('weight[]')
    employee = current_user.username

    for i in range(len(key_focus_areas)):
        scorecard = Scorecard(
            key_focus_area=key_focus_areas[i],
            strategic_objective=strategic_objectives[i],
            performance_measure=performance_measures[i],
            unit_of_measure=unit_of_measures[i],
            target=targets[i],
            weight=float(weights[i]),
            employee_name = employee
        )
        db.session.add(scorecard)

    db.session.commit()
    flash('Scorecards saved successfully!', 'success')
    return redirect(url_for('contracting'))


@app.route('/save_scorecard_row', methods=['POST'])
def save_scorecard_row():
    try:
        # Parse JSON data from the request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Extract data from the request
        scorecard_id = data.get('id')  # ID of the scorecard row
        key_focus_area = data.get('keyFocusArea')
        strategic_objective = data.get('strategicObjective')
        performance_measure = data.get('performanceMeasure')
        unit_of_measure = data.get('unitOfMeasure')
        target = data.get('target')
        weight = data.get('weight')

        # Validate required fields
        if not scorecard_id:
            return jsonify({'error': 'Scorecard ID is required'}), 400

        # Find the scorecard by ID
        scorecard = Scorecard.query.get(scorecard_id)
        if not scorecard:
            return jsonify({'error': 'Scorecard not found'}), 404

        # Update the scorecard fields
        scorecard.key_focus_area = key_focus_area
        scorecard.strategic_objective = strategic_objective
        scorecard.performance_measure = performance_measure
        scorecard.unit_of_measure = unit_of_measure
        scorecard.target = target
        scorecard.weight = weight

        # Commit changes to the database
        db.session.commit()

        return jsonify({'message': 'Scorecard updated successfully'}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while saving the scorecard'}), 500



@app.route('/schools', methods=['GET', 'POST'])
@login_required
def schools():
    form = AddNewSchoolTrackerForm()
    username = current_user.username
    role = current_user.role

    all_schools = SchoolTracker.query.order_by(SchoolTracker.schoolname.asc(), SchoolTracker.archived == False).all()
    
    # Query to fetch schools in descending order of installation date and filter out dates earlier than today
    today = datetime.utcnow()
    all_schools_scheduled = SchoolTracker.query.filter(SchoolTracker.installation_date >= today)\
                                     .order_by(SchoolTracker.installation_date.desc())\
                                     .all()
    
    return render_template('school_tracker.html', 
                           username=username, 
                           role=role, 
                           all_schools=all_schools, 
                           all_schools_scheduled=all_schools_scheduled,
                           form=form, 
                           title='School Tracker')




@app.route('/archive_school/<int:id>', methods=['GET', 'POST'])
@login_required
def archive_school(id):
    school_to_be_deleted = SchoolTracker.query.get(id)
    if current_user.role == 'Administrator':
        school_to_be_deleted.archived = True
        # db.session.delete(task_to_be_deleted)
        db.session.commit()
        flash("School deleted successfully")
    else:
        flash("You don't have permission to delete this school.") 
    return redirect(url_for('schools'))




@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    form=TaskForm()
    username=current_user.username
    role=current_user.role
    all_users = User.query.all()
    user_choices = [(user.username) for user in all_users]
    your_tasks = Task.query.filter(Task.assigned_to == current_user.username, Task.status == 'Pending',Task.archived == False )
    your_department_tasks = Task.query.filter(Task.department == current_user.department,Task.archived == False )
    tasks_you_created = Task.query.filter(Task.task_author == current_user.username )
    archived_tasks = Task.query.filter(Task.task_author == current_user.username, Task.archived == True)
    return render_template('tasks.html',tasks_you_created =tasks_you_created ,archived_tasks=archived_tasks, your_department_tasks=your_department_tasks,your_tasks=your_tasks,user_choices=user_choices,username=username,role=role,form=form, title='Tasks')


@app.route('/delete_task/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_task(id):
    task_to_be_deleted = Task.query.get(id)
    if current_user.role == 'Administrator' or task_to_be_deleted.task_author:
        task_to_be_deleted.archived = True
        # db.session.delete(task_to_be_deleted)
        db.session.commit()
        flash("Task deleted successfully")
    else:
        flash("You don't have permission to delete this task.") 
    return redirect(url_for('tasks'))




# @app.route('/notifications', methods=['GET', 'POST'])
# @login_required
# def notifications():
#     username=current_user.username
#     role=current_user.role

#     this_week = WorkstreamsReport.query.filter(WorkstreamsReport.employee_name == current_user.username)
#     following_week = TargetsReport.query.filter(TargetsReport.employee_name==current_user.username)
#     return render_template('notifications.html',username=username,role=role,this_week=this_week,following_week=following_week, title='Reports')


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    
    return render_template('settings.html', title='Settings')



@app.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    username=current_user.username
    role=current_user.role

    this_week = WorkstreamsReport.query.filter(WorkstreamsReport.employee_name == current_user.username)
    following_week = TargetsReport.query.filter(TargetsReport.employee_name==current_user.username)
    return render_template('reports.html',username=username,role=role,this_week=this_week,following_week=following_week, title='Reports')


@app.route('/save_work_stream_row', methods=['GET', 'POST'])
@login_required
def save_work_stream_row():
    username=current_user.username
    role=current_user.role

    this_week = WorkstreamsReport.query.filter(WorkstreamsReport.employee_name == current_user.username)
    following_week = TargetsReport.query.filter(TargetsReport.employee_name==current_user.username)
    return render_template('reports.html',username=username,role=role,this_week=this_week,following_week=following_week, title='Reports')


@app.route('/save_workstreamsTable', methods=['POST'])
def save_workstreams_table():
    try:
        data = request.get_json().get('data', [])
        for row in data:
            row_id = row.get('id')
            row_data = row.get('data')

            if row_id == "new":  # Create a new row
                new_report = WorkstreamsReport(
                    workstream=row_data[0],
                    progress=row_data[1],
                    quantity=row_data[2],
                    target_completion_date=row_data[3],
                    comments=row_data[4],
                    employee_name=current_user.username
                )
                db.session.add(new_report)
            else:  # Update existing row
                report = WorkstreamsReport.query.get(row_id)
                if report:
                    report.workstream = row_data[0]
                    report.progress = row_data[1]
                    report.quantity = row_data[2]
                    report.target_completion_date = row_data[3]
                    report.comments = row_data[4]

        db.session.commit()
        return jsonify({"message": "Table saved successfully!"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "An error occurred while saving the table."}), 500

@app.route('/save_targetsTable', methods=['POST'])
def save_targets_table():
    try:
        data = request.get_json().get('data', [])
        for row in data:
            if len(row) >= 2:  # Ensure there are enough columns
                target = row[0]
                target_completion_date = row[1]

                # Add or update the record in the database
                report = TargetsReport(
                    target=target,
                    target_completion_date=target_completion_date,
                    employee_name=current_user.username,
                    timestamp=datetime.utcnow()
                )
                db.session.add(report)
        db.session.commit()
        return jsonify({"message": "Targets table saved successfully!"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "An error occurred while saving the targets table."}), 500


@app.route('/workspaces', methods=['GET', 'POST'])
@login_required
def workspaces():
    username=current_user.username
    role=current_user.role
    form = WorkspaceForm()
    form.members.choices = [(user.id, user.username) for user in User.query.all()]  # Populate member options

    if form.validate_on_submit():
        workspace = Workspace(
            name=form.name.data,
            description=form.description.data
        )
        workspace.members = User.query.filter(User.id.in_(form.members.data)).all()  # Add selected members
        db.session.add(workspace)
        db.session.commit()
        return redirect(url_for('workspaces'))

    workspaces = Workspace.query.all()
    return render_template('workspaces.html',username=username,role=role,form=form, workspaces=workspaces, title='Workspaces')


@app.route('/workspacename/<int:workspaceID>', methods=['GET', 'POST'])
@login_required
def workspacename(workspaceID):
    username=current_user.username
    role=current_user.role
    form = WorkspaceForm()
    form.members.choices = [(user.id, user.username) for user in User.query.all()]  # Populate member options
    # current_workspace = Workspace.query.get(Workspace.id == Workspace.workspaceID)
    # workspaces = Workspace.query.all()
    current_workspace = Workspace.query.get_or_404(workspaceID)
    return render_template('workspace_name.html',username=username,current_workspace=current_workspace, role=role,form=form, workspaces=workspaces, title='Workspaces')


@app.route('/events', methods=['GET', 'POST'])
@login_required
def events():
    username=current_user.username
    role=current_user.role
    return render_template('events_and_planning.html',username=username,role=role, title='Events & Planning')


@app.route('/team', methods=['GET', 'POST'])
@login_required
def team():
    username=current_user.username
    role=current_user.role
    team= User.query.filter(User.department == current_user.department)
    return render_template('team.html',username=username,role=role,team=team, title='Team')


@app.route('/helpdesk', methods=['GET', 'POST'])
@login_required
def helpdesk():
    username=current_user.username
    role=current_user.role
    return render_template('help_desk.html',username=username,role=role, title='Help Desk')


# Set up file upload configurations
SCHOOL_UPLOAD_FOLDER = 'app/static/schooluploads'
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}
app.config['SCHOOL_UPLOAD_FOLDER'] = SCHOOL_UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(SCHOOL_UPLOAD_FOLDER):
    os.makedirs(SCHOOL_UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_school_data', methods=['POST'])
def upload_school_data():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['SCHOOL_UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Import the file into the database
        import_school_data(filepath)
        flash('File successfully uploaded and data imported!')
        return redirect('/schools')

    flash('Invalid file format. Please upload a .csv, .xls, or .xlsx file.')
    return redirect(request.url)

def import_school_data(filepath):
    # Read the uploaded file using pandas
    if filepath.endswith('.csv'):
        data = pd.read_csv(filepath)
    else:
        data = pd.read_excel(filepath)

    # Debugging: Print the column names and first few rows for verification
    print("Columns in uploaded file:", data.columns.tolist())
    print("Sample data:", data.head())

    # Iterate through the data and add it to the database
    for _, row in data.iterrows():
        # Convert installation_date to a Python datetime object, if it exists
        installation_date = None
        if 'installation_date' in row and pd.notnull(row['installation_date']):
            try:
                installation_date = datetime.strptime(str(row['installation_date']), '%Y-%m-%d')
            except ValueError:
                raise ValueError(f"Invalid date format for installation_date: {row['installation_date']}")

        # Create a new SchoolTracker object
        school = SchoolTracker(
            schoolname=row['schoolname'],
            province=row['province'],
            district=row['district'],
            computers=row['computers'],
            internet=row['internet'],
            lab=row['lab'],
            installed=row['installed'],
            scheduled_visit=row['scheduled_visit'],
            installation_date=installation_date,  # Pass the datetime object
            tech_ready=row['tech_ready']
        )
        db.session.add(school)

    # Commit the changes to the database
    db.session.commit()
    return redirect(url_for('schools'))


@app.route('/addtoschooltracker', methods=['GET', 'POST'])
@login_required
def addtoschooltracker():
    form=AddNewSchoolTrackerForm()

    if form.validate_on_submit():
        add_school_to_tracker = SchoolTracker(
                        schoolname=form.schoolname.data,
                        province=form.province.data,
                        district=form.district.data,
                        computers=form.computers.data,
                        internet=form.internet.data,
                        lab=form.lab.data,
                        installed=form.installed.data,
                        scheduled_visit=form.scheduled_visit.data,
                        tech_ready=form.tech_ready.data,
                        installation_date=form.installation_date.data,
                        school_contact=form.school_contact.data
                        )
        db.session.add(add_school_to_tracker)
        db.session.commit()
        flash(('New School added'))
        return redirect(url_for('schools'))
    else:
        flash(('Error: Could not add school'))
        return redirect(url_for('schools'))
    

@app.route('/deleteschool/<int:schoolId>', methods=['POST'])
@login_required
def deleteschool(schoolId):
    # Query the school by ID
    school = SchoolTracker.query.get_or_404(schoolId)

    # Delete the school from the database
    db.session.delete(school)
    db.session.commit()

    # Flash a success message and redirect to the school tracker page
    flash(f'School "{school.schoolname}" has been successfully deleted.', 'success')
    return redirect('/schools')


@app.route('/new_task', methods=['GET','POST'])
@login_required
def new_task():
    form=TaskForm()
    if form.validate_on_submit():
        create_task = Task(
            taskname=form.taskname.data,
            description=form.description.data,
            status=form.status.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
            task_author=current_user.username,
            department=form.department.data,
            assigned_to=form.assigned_to.data,
            category=form.category.data,
            progress=form.progress.data,
            # complete_date=form.complete_date.data
        )
        if form.assigned_to.data == 'Nobody' and form.department.data == 'None':
            create_task.assigned_to == current_user.username
            create_task.department == current_user.department
        db.session.add(create_task)
        db.session.commit()
        # flash(('Your task was successfully posted.'))
        send_alert = Notifications(
            message = 'You have been assigned new task.',
            category = 'Tasks',
            sender = current_user.username,
            reciever = form.assigned_to.data
        )
        if form.assigned_to.data == 'Nobody' and form.department.data == 'None':
                send_alert.reciever = current_user.username
        elif form.assigned_to.data == 'Nobody' and form.department.data != 'None':
            send_alert.reciever = form.department.data
            send_alert.message = 'Your department has been assigned a task.'
        db.session.add(send_alert)
        db.session.commit()
        return redirect(url_for('tasks'))
    else:
        flash(('Error: Your task was not posted.'))
        return redirect(url_for('tasks'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(firstname=form.firstname.data, lastname=form.lastname.data,username=form.username.data,department=form.department.data, role=form.role.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))

    return render_template('user.html',title='Profile', user=user)


UPLOAD_FOLDER = 'app/static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    # if request.method == "POST":
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.role = form.role.data
        current_user.department = form.department.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data

        if form.profile_pic.data:
            # Process the new profile picture
            pic_filename = secure_filename(form.profile_pic.data.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            pic_path = os.path.join(app.config['UPLOAD_FOLDER'], pic_name)
            form.profile_pic.data.save(pic_path)
            current_user.profile_pic = pic_name

            try:
                db.session.commit()
                flash(('Your changes have been saved.'))
                return redirect(url_for('index'))
            except:
                flash(('Oops, something went wrong. Please try again.'))
                return redirect(url_for('index'))
            
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.role.data = current_user.role
        form.department.data = current_user.department
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

