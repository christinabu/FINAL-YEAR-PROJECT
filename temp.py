@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        user_id = session['user']
        username = session.get('username', 'admin')
        
        # Get current month and year  and Calculate start and end dates of the current month
        current_month = datetime.now().month
        current_year = datetime.now().year
        current_start_date = f"{current_year}-{current_month:02d}-01"
        current_end_date = f"{current_year}-{current_month:02d}-{monthrange(current_year, current_month)[1]}"
        

        # Calculate start and end dates of the previous month
        prev_month = current_month - 1 if current_month > 1 else 12
        prev_year = current_year if current_month > 1 else current_year - 1
        prev_start_date = f"{prev_year}-{prev_month:02d}-01"
        prev_end_date = f"{prev_year}-{prev_month:02d}-{monthrange(prev_year, prev_month)[1]}"
        
        # Query Firebase to fetch expenditures for the current month
        expenditures_ref = db.child("users").child(user_id).child("expenditure") \
            .order_by_child("date").start_at(current_start_date).end_at(current_end_date).get()

        # Calculate total expenditure for the current month
        total_expenditure = 0
        if expenditures_ref:
            for exp in expenditures_ref.each():
                total_expenditure += float(exp.val()['amount'])
        
        # Query Firebase to fetch incomes for the current month
        incomes_ref = db.child("users").child(user_id).child("income") \
            .order_by_child("date").start_at(current_start_date).end_at(current_end_date).get()
        
        # Calculate total income for the current month
        total_income = 0
        if incomes_ref:
            for inc in incomes_ref.each():
                total_income += float(inc.val()['amount'])
        
        profit = total_income - total_expenditure

        #print("*****************************************************************",total_income,total_expenditure,profit)


        # Query Firebase to fetch expenditures for the previous month
        prev_expenditures_ref = db.child("users").child(user_id).child("expenditure") \
            .order_by_child("date").start_at(prev_start_date).end_at(prev_end_date).get()
        
        # Calculate total expenditure for the previous month
        prev_total_expenditure = 0
        if prev_expenditures_ref:
            for exp in prev_expenditures_ref.each():
                prev_total_expenditure += float(exp.val()['amount'])
        
        # Query Firebase to fetch incomes for the previous month
        prev_incomes_ref = db.child("users").child(user_id).child("income") \
            .order_by_child("date").start_at(prev_start_date).end_at(prev_end_date).get()
        
        # Calculate total income for the previous month
        prev_total_income = 0
        if prev_incomes_ref:
            for inc in prev_incomes_ref.each():
                prev_total_income += float(inc.val()['amount'])
        
        prev_profit = prev_total_income - prev_total_expenditure

        # Calculate percentage change in income
        # Calculate percentage change in income
        income_change = round(((total_income - prev_total_income) / prev_total_income) * 100, 1) if prev_total_income != 0 else 0

        # Calculate percentage change in expenditure
        expenditure_change = round(((total_expenditure - prev_total_expenditure) / prev_total_expenditure) * 100, 1) if prev_total_expenditure != 0 else 0

        # Calculate percentage change in profit
        profit_change = round(((profit - prev_profit) / prev_profit) * 100, 1) if prev_total_income != 0 else 0

        #------------------------------pie chart------------------------------------
        
        # Query Firebase to fetch expenditure data
        expenditure_data = db.child("users").child(user_id).child("expenditure").get().val()

        # Initialize dictionary to store total expenditure for each category
        category_totals = {}

    # Process the data to calculate total expenditure for each category
        for key, item in expenditure_data.items():
            category = item['category']
            amount = float(item['amount'])
            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount

        # Convert the data into lists for rendering in the template
        category_labels = list(category_totals.keys())
        category_amounts = list(category_totals.values())     
        
          
        return render_template(
            'dashboard.html', 
                           username=username, 
                           total_expenditure=total_expenditure, 
                           total_income=total_income, 
                           income_change=income_change, 
                           expenditure_change=expenditure_change, 
                           profit=profit, 
                           profit_change=profit_change,
                           category_labels=category_labels,
                           category_amounts=category_amounts,
        )
    else:
        # If user is not in session, redirect to sign-in page
        return redirect(url_for('signin'))

