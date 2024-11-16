from flask import render_template, url_for, flash, redirect, request, Blueprint, Response
from flask_login import login_user, current_user, logout_user, login_required
from flaskapp import db, bcrypt
from flaskapp.db_models import User, Post, Sales, Inventory, Service
from flaskapp.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, SaleForm, InventoryForm
from flaskapp.users.utils import send_reset_email, save_picture
import os
import csv
from datetime import datetime
from io import StringIO
from collections import defaultdict

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password, role = form.role.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log in!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data, role = form.role.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email or password', 'danger')
    return render_template('login.html', title = 'Login', form = form)


@users.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('main.home'))




@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    update_form = UpdateAccountForm()
    if update_form.validate_on_submit():
        if update_form.picture.data:
            if current_user.image_file != 'default.jpg':
                try:
                    os.remove(os.path.join(users.root_path, 'static/profile_pics', current_user.image_file))
                except FileNotFoundError as e:
                    #logger.info("Error in loading profile picture", 'warning')
                    pass
            picture_file = save_picture(update_form.picture.data)
            current_user.image_file = picture_file
            db.session.commit()
        current_user.username = update_form.username.data
        current_user.email = update_form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        update_form.username.data = current_user.username
        update_form.email.data = current_user.email
    try:
        image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    except FileNotFoundError as e:
        flash("Error in loading profile picture", 'warning')
    return render_template('account.html', title = 'Account', image_file = image_file, form = update_form)


@users.route('/user_posts/<username>')
def user_posts(username):
    page = request.args.get('page', 1, type = int)
    user = User.query.filter_by(username = username).first_or_404()
    posts = Post.query.filter_by(author = user).order_by(Post.date_posted.desc()).paginate(page = page, per_page = 2)   
    return render_template('user_posts.html', posts = posts, user = user)



@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('users.login'))

    return render_template('reset_request.html', title = 'Reset Password', form = form)

@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is invalid token!", "warning")
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated! You are now able to log in!', 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_token.html', title = 'Reset Password', form = form)


### SALES
@users.route("/sales", methods=['GET', 'POST'])
def sales():
    # Start with the base query for Sales
    sales_query = Sales.query

    # Optionally filter based on search criteria
    search = request.args.get('search')
    if search:
        # Assuming vehicle and customer are columns on the Sales model
        sales_query = sales_query.filter(
            Sales.vehicle_id.contains(search) | Sales.customer_id.contains(search)
        )

    # Filter by start and end date
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date and end_date:
        sales_query = sales_query.filter(Sales.sale_date.between(start_date, end_date))
    
    # Execute the query to get the filtered results
    sales = sales_query.all()
    
    # Calculate overview metrics (replace with actual logic)
    total_sales = len(sales)
    total_revenue = sum(sale.total_amount for sale in sales)
    num_transactions = total_sales      
    
    vehicle_sales_count = {}
    for sale in sales:
        vehicle_sales_count[sale.vehicle_id] = vehicle_sales_count.get(sale.vehicle_id, 0) + 1

    # Find the vehicle with the maximum sales
    top_selling_vehicle_id = max(vehicle_sales_count, key=vehicle_sales_count.get, default=None)

    if top_selling_vehicle_id:
        top_selling_vehicle = Inventory.query.get(top_selling_vehicle_id)
        top_selling_vehicle = f"{top_selling_vehicle.make} - {top_selling_vehicle.model}" if top_selling_vehicle else "Audi"
    else:
        top_selling_vehicle = "Audi"    
    
    #sales data for json
    # Aggregate sales by month
    monthly_sales = defaultdict(int)  # Default to 0 for any month
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    for sale in sales:
        # Get the month from the sale date (assuming sale_date is a datetime object)
        month = sale.sale_date.month  # sale_date is a datetime object
        monthly_sales[month] += sale.total_amount  # Aggregate total sales for the month

    # Prepare data for chart
    sales_data = {
        "labels": months,  # Month names
        "sales": [monthly_sales[i] for i in range(1, 13)],  # Sales for each month
    }

    # Fetch vehicles and customers separately
    vehicle_ids = [sale.vehicle_id for sale in sales]
    customer_ids = [sale.customer_id for sale in sales]

    # Query vehicles and customers based on the IDs from the sales data
    vehicles = {vehicle.vehicle_id: vehicle for vehicle in Inventory.query.filter(Inventory.vehicle_id.in_(vehicle_ids)).all()}
    customers = {customer.user_id: customer for customer in User.query.filter(User.user_id.in_(customer_ids)).all()}

    return render_template('sales.html', 
                           sales=sales, 
                           vehicles=vehicles, 
                           customers=customers,
                           total_sales=total_sales,
                           total_revenue=total_revenue,
                           top_selling_vehicle=top_selling_vehicle,
                           num_transactions=num_transactions, 
                           sales_data=sales_data)

# Export Sales Data (CSV)
@users.route('/sales/export')
@login_required

def export_sales():
    # Fetch all sales
    sales = Sales.query.all()
    
    # Create a StringIO buffer for CSV output
    si = StringIO()
    writer = csv.writer(si)
    
    # Write CSV headers
    writer.writerow(['Date', 'Vehicle', 'Customer', 'Quantity', 'Total Amount'])
    
    # Loop through all sales and write each row
    for sale in sales:
        # Get the vehicle details
        vehicle = Inventory.query.get(sale.vehicle_id)
        if vehicle:  # If vehicle exists, get details
            vehicle_info = f"{vehicle.make} - {vehicle.model}"
        else:
            vehicle_info = "Unknown Vehicle"  # Handle case where vehicle is not found
        
        # Get customer details (Assuming you want the name or email)
        customer = User.query.get(sale.customer_id)
        if customer:  # If customer exists, get details
            customer_info = customer.username  # Or use customer.email, depending on what you want
        else:
            customer_info = "Unknown Customer"  # Handle case where customer is not found
        
        # Write the data row for this sale
        writer.writerow([sale.sale_date, vehicle_info, customer_info, sale.quantity, sale.total_amount])
    
    # Get the CSV data as a string
    output = si.getvalue()
    
    # Return the CSV as a response
    return Response(output, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=sales_data.csv'})


# Add New Sale Page
@users.route('/sales/add', methods=['GET', 'POST'])
@login_required
def add_sale():
    form = SaleForm()

    # Handle POST request (form submission)
    if form.validate_on_submit():
        vehicle_id = form.vehicle_id.data
        customer_id = form.customer_id.data
        quantity = form.quantity.data
        sale_date = datetime.strptime(form.sale_date.data, '%Y-%m-%d').date()

        # Get the vehicle details (model, make, price)
        model_name, make, price = form.get_vehicle_details(vehicle_id)

        # Get the customer name
        customer_name = form.get_customer_name(customer_id)

        if model_name and customer_name:
            # Calculate the total amount
            total_amount = price * quantity

            # Create a new sale record
            sale = Sales(
                sale_date=sale_date,
                vehicle_id=vehicle_id,
                customer_id=customer_id,
                quantity=quantity,
                total_amount=total_amount,
                payment_method=form.payment_method.data
            )

            # Add sale to the database
            db.session.add(sale)
            # Update vehicle stock count
            vehicle = Inventory.query.get(vehicle_id)
            
            if vehicle and vehicle.stock_count >= quantity:
                vehicle.stock_count -= quantity  # Update stock count in memory
                db.session.commit()  # Commit the changes to both Sales and Inventory tables
                flash(f'Sale added successfully! {quantity} vehicles sold.', 'success')
                return redirect(url_for('users.sales'))
            else:
                db.session.rollback()  # Rollback if stock is insufficient
                flash('Not enough stock available for this sale.', 'danger')
                return redirect(url_for('users.sales'))

            flash(f'Sale added successfully! {customer_name} purchased {quantity} {model_name} - {make}', 'success')
            return redirect(url_for('users.sales'))  # Redirect to another route after success
        else:
            flash('Invalid vehicle or customer ID', 'danger')

    # Render the form with any additional context data
    return render_template('add_sale.html', form=form)




### INVENTORY
@users.route('/inventory', methods=['GET', 'POST'])
def inventory():
    # Search and Filter
    search = request.args.get('search', '')
    status_filter = request.args.get('status', 'All')

    # Base query
    inventory_query = Inventory.query.filter(
        (Inventory.make.like(f'%{search}%')) | 
        (Inventory.model.like(f'%{search}%')) |
        (str(Inventory.year) == f'%{search}%')
    )

    # Filter by status
    if status_filter != 'All':
        inventory_query = inventory_query.filter_by(status=status_filter)

    # Paginate results
    inventory_list = inventory_query.paginate(page=request.args.get('page', 1, type=int), per_page=10)

    return render_template('inventory.html', inventory_list=inventory_list, search=search, status_filter=status_filter)


@users.route('/add_vehicle', methods=['GET', 'POST'])
@login_required
def add_vehicle():
    form = InventoryForm()

    if form.validate_on_submit():
        new_vehicle = Inventory(
            make=form.make.data,
            model=form.model.data,
            year=form.year.data,
            stock_count=form.stock_count.data,
            price=form.price.data,
            status=form.status.data
        )
        db.session.add(new_vehicle)
        db.session.commit()
        flash('New vehicle added successfully!', 'success')
        return redirect(url_for('users.inventory'))

    return render_template('add_vehicle.html', form=form)


@users.route('/edit_vehicle/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):
    vehicle = Inventory.query.get_or_404(vehicle_id)
    form = InventoryForm(obj=vehicle)

    if form.validate_on_submit():
        vehicle.make = form.make.data
        vehicle.model = form.model.data
        vehicle.year = form.year.data
        vehicle.stock_count = form.stock_count.data
        vehicle.price = form.price.data
        vehicle.status = form.status.data
        db.session.commit()
        flash('Vehicle updated successfully!', 'success')
        return redirect(url_for('users.inventory'))

    return render_template('edit_vehicle.html', form=form, vehicle=vehicle)


@users.route('/delete_vehicle/<int:vehicle_id>', methods=['POST'])
@login_required
def delete_vehicle(vehicle_id):
    vehicle = Inventory.query.get_or_404(vehicle_id)
    db.session.delete(vehicle)
    db.session.commit()
    flash('Vehicle deleted successfully!', 'danger')
    return redirect(url_for('users.inventory'))



### SERVICE

# View all scheduled service appointments
@users.route('/service_appointments', methods=['GET', 'POST'])
@login_required
def service_appointments():
    if current_user.role != 'Service' and current_user.role != 'Admin':
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('main.home'))

    # Filter functionality
    status_filter = request.args.get('status')
    date_filter = request.args.get('date')

    appointments = Service.query

    if status_filter:
        appointments = appointments.filter(Service.status == status_filter)
    if date_filter:
        appointments = appointments.filter(Service.appointment_date >= datetime.strptime(date_filter, '%Y-%m-%d'))

    appointments = appointments.all()

    return render_template('service_appointments.html', appointments=appointments, inventory = Inventory.query, users = User.query)

# Update service appointment status
@users.route('/service_update_status/<int:service_id>', methods=['POST'])
@login_required
def update_status(service_id):
    service = Service.query.get_or_404(service_id)
    
    if current_user.role != 'Service':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.home'))

    new_status = request.form.get('status')

    # Update status
    if new_status in ['Scheduled', 'In Progress', 'Completed']:
        service.status = new_status
        db.session.commit()
        flash(f'Service status updated to {new_status}.', 'success')
    else:
        flash('Invalid status selected.', 'danger')

    return redirect(url_for('users.service_appointments'))



@users.route('/book_service', methods=['GET', 'POST'])
def book_service():
    if request.method == 'POST':
        # Get form data
        service_type = request.form['service_type']
        vehicle_id = request.form['vehicle_id']
        appointment_date = request.form['date']
        
        # Convert the date string into a datetime object
        try:
            appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d')
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return redirect(url_for('users.book_service'))

        # Check if the appointment date is in the future (to prevent past appointments)
        if appointment_date < datetime.now():
            flash("The appointment date cannot be in the past. Please choose a future date.", "danger")
            return redirect(url_for('users.book_service'))
        
        # Create new appointment entry
        new_appointment = Service(
            customer_id=current_user.user_id,
            service_type=service_type,
            vehicle_id=vehicle_id,
            appointment_date=appointment_date,
            status='Scheduled'  # Default status when booking
        )
        
        # Add to the database
        db.session.add(new_appointment)
        db.session.commit()
        
        flash(f"Service appointment for {service_type} booked successfully!", "success")
        return redirect(url_for('users.customer_service_data'))  # Redirect to service dashboard
    
    return render_template('book_service.html')



### CUSTOMER SERVICE DATA
# Service history and upcoming appointments (fetch from the database)
@users.route('/customer_service_data', methods=['GET', 'POST'])
def customer_service_data():
    # Fetch service history and upcoming appointments for the logged-in customer
    service_history = Service.query.filter_by(customer_id=current_user.user_id, status='Completed').all()
    upcoming_appointments = Service.query.filter_by(customer_id=current_user.user_id, status='Scheduled').all()

    # Handle the form to book a new service
    if request.method == 'POST':
        service_type = request.form['service_type']
        vehicle = request.form['vehicle']
        date = request.form['date']
        new_appointment = Service(
            customer_id=current_user.id,
            service_type=service_type,
            vehicle=vehicle,
            date=date,
            status='Scheduled'
        )
        db.session.add(new_appointment)
        db.session.commit()
        return redirect(url_for('users.customer_service_data'))  # Refresh page

    return render_template('customer_service_data.html', service_history=service_history, upcoming_appointments=upcoming_appointments)

# Route to handle appointment cancellation
@users.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    appointment = Service.query.get_or_404(appointment_id)
    appointment.status = 'Cancelled'
    db.session.commit()
    return redirect(url_for('users.customer_service_data'))