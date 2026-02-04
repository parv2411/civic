import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import get_db
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super_secret_key'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route("/")
def index():
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM complaints")
    total = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS resolved FROM complaints WHERE status='Resolved'")
    resolved = cursor.fetchone()['resolved']

    cursor.execute("SELECT COUNT(*) AS pending FROM complaints WHERE status != 'Resolved'")
    pending = cursor.fetchone()['pending']

    cursor.execute("SELECT COUNT(*) AS citizens FROM users WHERE role='citizen'")
    citizens = cursor.fetchone()['citizens']

    return render_template(
        "dashboard.html",
        total=total,
        resolved=resolved,
        pending=pending,
        citizens=citizens
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        place = request.form.get("place")
        phone = request.form.get("phone")
        email = request.form.get("email")
        password = request.form.get("password")
        
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, place, phone, email, password, role) VALUES (%s, %s, %s, %s, %s, 'citizen')",
                (name, place, phone, email, password)
            )
            db.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            print(f"Error: {e}")
            flash("Registration failed. Email or Name might already exist.", "danger")
            return render_template("register.html")
        finally:
            cursor.close()
            db.close()
            
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE name = %s AND password = %s", (name, password))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['role'] = user['role']
            
            if user['role'] == 'admin':
                return redirect(url_for("admin_dashboard"))
            elif user['role'] == 'department':
                session['dept_name'] = user['name']
                # Determine which dashboard to redirect to
                if user['name'] == 'Water Authority':
                    return redirect(url_for("water_dashboard"))
                elif user['name'] == 'Municipality':
                    return redirect(url_for("muni_dashboard"))
                elif user['name'] == 'Green Services':
                    return redirect(url_for("green_dashboard"))
                else:
                    return redirect(url_for("road_dashboard"))
            else:
                return redirect(url_for("user_dashboard"))
        else:
            flash("Invalid Credentials. Please try again.", "danger")
            return redirect(url_for("login"))

            
    return render_template("login.html")

def get_dashboard_data():
    user_id = session.get('user_id')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Stats
    cursor.execute("SELECT COUNT(*) AS total FROM complaints WHERE user_id = %s", (user_id,))
    total = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) AS pending FROM complaints WHERE user_id = %s AND status = 'Pending'", (user_id,))
    pending = cursor.fetchone()['pending']
    cursor.execute("SELECT COUNT(*) AS progress FROM complaints WHERE user_id = %s AND status IN ('In Progress', 'Assigned')", (user_id,))
    inprogress = cursor.fetchone()['progress']
    cursor.execute("SELECT COUNT(*) AS resolved FROM complaints WHERE user_id = %s AND status = 'Resolved'", (user_id,))
    resolved = cursor.fetchone()['resolved']
    
    # Recent Complaints
    cursor.execute("SELECT * FROM complaints WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    complaints = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return {
        'total': total,
        'pending': pending,
        'inprogress': inprogress,
        'resolved': resolved,
        'complaints': complaints,
        'user_name': session.get('user_name')
    }

@app.route("/user_dashboard")
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get user specific counts
    cursor.execute("SELECT COUNT(*) AS total FROM complaints WHERE user_id = %s", (user_id,))
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) AS pending FROM complaints WHERE user_id = %s AND status = 'Pending'", (user_id,))
    pending = cursor.fetchone()['pending']
    
    cursor.execute("SELECT COUNT(*) AS progress FROM complaints WHERE user_id = %s AND status IN ('In Progress', 'Assigned')", (user_id,))
    inprogress = cursor.fetchone()['progress']
    
    cursor.execute("SELECT COUNT(*) AS resolved FROM complaints WHERE user_id = %s AND status = 'Resolved'", (user_id,))
    resolved = cursor.fetchone()['resolved']

    # Support for searching/tracking by ID or Title
    search = request.args.get('search')
    if search:
        if search.isdigit():
            cursor.execute("SELECT * FROM complaints WHERE user_id = %s AND id = %s", (user_id, int(search)))
        else:
            cursor.execute("SELECT * FROM complaints WHERE user_id = %s AND title LIKE %s", (user_id, f"%{search}%"))
        user_complaints = cursor.fetchall()
    else:
        # Get recent complaints
        cursor.execute("SELECT * FROM complaints WHERE user_id = %s ORDER BY created_at DESC LIMIT 10", (user_id,))
        user_complaints = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    data = get_dashboard_data()
    return render_template("user_dashboard.html", **data)

@app.route("/user_reports")
def user_reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('user_dashboard', _anchor='reports'))

@app.route("/raise_complaint")
def raise_complaint():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('user_dashboard', _anchor='raise-complaint'))

@app.route("/information_category")
def information_category():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("info_category.html", user_name=session.get('user_name'))

@app.route("/government_directories")
def government_directories():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('user_dashboard', _anchor='gov-directories'))



@app.route("/submit_complaint", methods=["GET", "POST"])
def submit_complaint():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == "POST":
        user_id = session['user_id']
        dept = request.form.get("department")
        title = request.form.get("title")
        desc = request.form.get("description")
        incident_date = request.form.get("incident_date")
        incident_location = request.form.get("incident_location")
        
        if not dept:
            dept = 'Municipality'

        # Image Handling
        image_filename = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        # Video Handling
        video_filename = None
        if 'video' in request.files:
            file = request.files['video']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                video_filename = filename
        
        db = get_db()
        cursor = db.cursor()
        
        # Insert without tracking_id first to get the ID
        cursor.execute(
            "INSERT INTO complaints (user_id, department, title, description, incident_date, incident_location, image, video, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Pending')",
            (user_id, dept, title, desc, incident_date, incident_location, image_filename, video_filename)
        )
        complaint_id = cursor.lastrowid
        
        # Generate tracking_id based on department
        prefixes = {
            'Road / PWD': 'PWD',
            'Water Authority': 'WTR',
            'Municipality': 'MUN',
            'Green Services': 'GRN'
        }
        prefix = prefixes.get(dept, 'OTH')
        tracking_id = f"{prefix}-{complaint_id:03d}"
        
        # Update with tracking_id
        cursor.execute("UPDATE complaints SET tracking_id = %s WHERE id = %s", (tracking_id, complaint_id))
        
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for("complaint_success", complaint_id=complaint_id))
        
    dept = request.args.get("dept")
    return render_template("complaint_form.html", dept=dept, user_name=session.get('user_name'))

@app.route("/complaint_success/<int:complaint_id>")
def complaint_success(complaint_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT tracking_id FROM complaints WHERE id = %s", (complaint_id,))
    comp = cursor.fetchone()
    cursor.close()
    db.close()
    
    tracking_id = comp[0] if comp else str(complaint_id)
    
    return render_template("complaint_success.html", tracking_id=tracking_id, complaint_id=complaint_id, user_name=session.get('user_name'))

@app.route("/track_complaint", methods=["GET", "POST"])
def track_complaint():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    data = get_dashboard_data()
    complaint = None
    if request.method == "POST":
        track_id = request.form.get("track_id").strip().upper()
        captcha = request.form.get("captcha")
        
        if captcha != "A314":
            flash("Invalid Captcha. Please try again.")
        else:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            
            if track_id.isdigit():
                cursor.execute("SELECT user_id FROM complaints WHERE id = %s", (track_id,))
            else:
                cursor.execute("SELECT user_id FROM complaints WHERE tracking_id = %s", (track_id,))
                
            exists = cursor.fetchone()
            
            if not exists:
                flash("No complaint found with this ID.")
            elif exists['user_id'] != session['user_id']:
                flash("Access denied. This complaint ID belongs to another user.")
            else:
                if track_id.isdigit():
                    cursor.execute("SELECT * FROM complaints WHERE id = %s", (track_id,))
                else:
                    cursor.execute("SELECT * FROM complaints WHERE tracking_id = %s", (track_id,))
                complaint = cursor.fetchone()
                
            cursor.close()
            db.close()
            
    return render_template("user_dashboard.html", complaint=complaint, **data)

@app.route("/edit_complaint_portal", methods=["GET", "POST"])
def edit_complaint_portal():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == "POST":
        track_id = request.form.get("track_id").strip().upper()
        
        # Check if it exists for this user (support both formats)
        db = get_db()
        cursor = db.cursor()
        if track_id.isdigit():
            cursor.execute("SELECT id FROM complaints WHERE id = %s AND user_id = %s", (track_id, session['user_id']))
        else:
            cursor.execute("SELECT id FROM complaints WHERE tracking_id = %s AND user_id = %s", (track_id, session['user_id']))
        comp = cursor.fetchone()
        
        if comp:
            # Always pass the numeric ID to the edit_complaint route for simplicity
            return redirect(url_for("edit_complaint", id=comp[0]))
        else:
            flash("Invalid ID or access denied.")
        
    data = get_dashboard_data()
    return render_template("user_dashboard.html", **data)

@app.route("/delete_complaint_portal", methods=["GET", "POST"])
def delete_complaint_portal():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    success = False
    if request.method == "POST":
        track_id = request.form.get("track_id").strip().upper()
        reason = request.form.get("reason")
        captcha = request.form.get("captcha")
        
        if captcha != "1232":
            flash("Invalid Captcha.")
        else:
            db = get_db()
            cursor = db.cursor()
            
            if track_id.isdigit():
                cursor.execute("SELECT user_id, id FROM complaints WHERE id = %s", (track_id,))
            else:
                cursor.execute("SELECT user_id, id FROM complaints WHERE tracking_id = %s", (track_id,))
                
            comp = cursor.fetchone()
            
            if comp and comp[0] == session['user_id']:
                cursor.execute("DELETE FROM complaints WHERE id = %s", (comp[1],))
                db.commit()
                success = True
                flash("Complaint deleted successfully.", "success")
            else:
                flash("Invalid ID or access denied.")
            cursor.close()
            db.close()
        
    data = get_dashboard_data()
    return render_template("user_dashboard.html", success=success, **data)

@app.route("/delete_complaint/<int:id>", methods=["POST"])
def delete_complaint(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    db = get_db()
    cursor = db.cursor()
    # Check if the complaint belongs to the user
    cursor.execute("SELECT user_id FROM complaints WHERE id = %s", (id,))
    comp = cursor.fetchone()
    
    if comp and comp[0] == session['user_id']:
        cursor.execute("DELETE FROM complaints WHERE id = %s", (id,))
        db.commit()
        flash("Complaint deleted successfully.")
    
    cursor.close()
    db.close()
    return redirect(url_for("user_dashboard", _anchor="delete-complaint"))

@app.route("/edit_complaint/<int:id>", methods=["GET", "POST"])
def edit_complaint(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        location = request.form.get("location")
        
        cursor.execute(
            "UPDATE complaints SET title = %s, description = %s, incident_location = %s WHERE id = %s AND user_id = %s",
            (title, description, location, id, session['user_id'])
        )
        db.commit()
        cursor.close()
        db.close()
        flash("Complaint updated successfully!", "success")
        return redirect(url_for("user_dashboard", _anchor="edit-complaint"))
        
    cursor.execute("SELECT * FROM complaints WHERE id = %s AND user_id = %s", (id, session['user_id']))
    complaint = cursor.fetchone()
    cursor.close()
    db.close()
    
    if not complaint:
        return "Complaint not found or access denied."
        
    return render_template("edit_complaint.html", complaint=complaint, user_name=session.get('user_name'))

@app.route("/road_dashboard")
def road_dashboard():
    if 'role' not in session or session['role'] != 'department':
        return redirect(url_for('login'))
        
    dept_name = session['dept_name']
    view = request.args.get('view', 'dashboard')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT c.*, u.name as user_name 
        FROM complaints c 
        JOIN users u ON c.user_id = u.id 
        WHERE c.department = %s 
        ORDER BY c.created_at DESC
    """, (dept_name,))
    complaints = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return render_template("road_dashboard.html", complaints=complaints, dept_name=dept_name, view=view)

@app.route("/water_dashboard")
def water_dashboard():
    if 'role' not in session or session['role'] != 'department':
        return redirect(url_for('login'))
        
    dept_name = session['dept_name']
    view = request.args.get('view', 'dashboard')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT c.*, u.name as user_name 
        FROM complaints c 
        JOIN users u ON c.user_id = u.id 
        WHERE c.department = %s 
        ORDER BY c.created_at DESC
    """, (dept_name,))
    complaints = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return render_template("water_dashboard.html", complaints=complaints, dept_name=dept_name, view=view)

@app.route("/muni_dashboard")
def muni_dashboard():
    if 'role' not in session or session['role'] != 'department':
        return redirect(url_for('login'))
        
    dept_name = session['dept_name']
    view = request.args.get('view', 'dashboard')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT c.*, u.name as user_name 
        FROM complaints c 
        JOIN users u ON c.user_id = u.id 
        WHERE c.department = %s 
        ORDER BY c.created_at DESC
    """, (dept_name,))
    complaints = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return render_template("muni_dashboard.html", complaints=complaints, dept_name=dept_name, view=view)

@app.route("/green_dashboard")
def green_dashboard():
    if 'role' not in session or session['role'] != 'department':
        return redirect(url_for('login'))
        
    dept_name = session['dept_name']
    view = request.args.get('view', 'dashboard')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT c.*, u.name as user_name 
        FROM complaints c 
        JOIN users u ON c.user_id = u.id 
        WHERE c.department = %s 
        ORDER BY c.created_at DESC
    """, (dept_name,))
    complaints = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return render_template("green_dashboard.html", complaints=complaints, dept_name=dept_name, view=view)

@app.route("/assign_complaint/<int:id>", methods=["POST"])
def assign_complaint(id):
    if 'role' not in session or session['role'] != 'department':
        return redirect(url_for('login'))
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE complaints SET status = 'Assigned' WHERE id = %s", (id,))
    db.commit()
    cursor.close()
    db.close()
    redirect_to = request.form.get("redirect_to", "road_dashboard")
    return redirect(url_for(redirect_to, view='complaints'))

@app.route("/resolve_complaint/<int:id>", methods=["POST"])
def resolve_complaint(id):
    if 'role' not in session or session['role'] != 'department':
        return redirect(url_for('login'))
        
    image_filename = None
    if 'resolved_photo' in request.files:
        file = request.files['resolved_photo']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename
            
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE complaints SET status = 'Resolved', resolved_image = %s WHERE id = %s", (image_filename, id))
    db.commit()
    cursor.close()
    db.close()
    redirect_to = request.form.get("redirect_to", "road_dashboard")
    return redirect(url_for(redirect_to, view='complaints'))

@app.route("/update_status/<int:complaint_id>", methods=["POST"])
def update_status(complaint_id):
    if 'role' not in session or session['role'] != 'department':
        return redirect(url_for('login'))
        
    new_status = request.form.get("status")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE complaints SET status = %s WHERE id = %s", (new_status, complaint_id))
    db.commit()
    cursor.close()
    db.close()
    
    redirect_to = request.form.get("redirect_to", "road_dashboard")
    return redirect(url_for(redirect_to, view='complaints'))


@app.route("/admin_dashboard")
def admin_dashboard():
    # In a real app, check for admin role here
    view = request.args.get('view', 'dashboard')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Global stats
    cursor.execute("SELECT COUNT(*) AS total FROM complaints")
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) AS new FROM complaints WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
    new_count = cursor.fetchone()['new']
    
    cursor.execute("SELECT COUNT(*) AS pending FROM complaints WHERE status = 'Pending'")
    pending = cursor.fetchone()['pending']
    
    cursor.execute("SELECT COUNT(*) AS resolved FROM complaints WHERE status = 'Resolved'")
    resolved = cursor.fetchone()['resolved']
    
    # Calculate percentage
    resolved_pct = (resolved / total * 100) if total > 0 else 0
    
    # Complaints/Users/Settings/Departments logic
    all_complaints = []
    system_users = []
    detailed_dept_stats = []
    dept_analytics_data = None
    selected_dept = request.args.get('dept')
    
    if view == 'reports':
        # Fetch ALL complaints for reports
        cursor.execute("""
            SELECT c.*, u.name as user_name 
            FROM complaints c 
            JOIN users u ON c.user_id = u.id 
            ORDER BY c.created_at DESC
        """)
        all_complaints = cursor.fetchall()
    elif view == 'users':
        # Fetch ALL users and their complaint counts
        cursor.execute("""
            SELECT u.*, 
            (SELECT COUNT(*) FROM complaints WHERE user_id = u.id) as complaint_count 
            FROM users u 
            WHERE role = 'citizen'
            ORDER BY name ASC
        """)
        system_users = cursor.fetchall()
    elif view == 'departments':
        # Fetch detailed stats for each department
        cursor.execute("""
            SELECT department, 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved
            FROM complaints 
            GROUP BY department
        """)
        detailed_dept_stats = cursor.fetchall()
    elif view == 'dept_analytics' and selected_dept:
        # Fetch specific data for the selected department
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved,
                SUM(CASE WHEN status = 'Assigned' THEN 1 ELSE 0 END) as assigned
            FROM complaints 
            WHERE department = %s
        """, (selected_dept,))
        dept_analytics_data = cursor.fetchone()
        
        # Also fetch recent complaints for this dept
        cursor.execute("""
            SELECT c.*, u.name as user_name 
            FROM complaints c 
            JOIN users u ON c.user_id = u.id 
            WHERE c.department = %s
            ORDER BY c.created_at DESC
            LIMIT 5
        """, (selected_dept,))
        all_complaints = cursor.fetchall()
    elif view == 'settings':
        # No extra DB fetch needed
        pass
    else:
        # Fetch only recent for dashboard
        cursor.execute("""
            SELECT c.*, u.name as user_name 
            FROM complaints c 
            JOIN users u ON c.user_id = u.id 
            ORDER BY c.created_at DESC 
            LIMIT 10
        """)
        all_complaints = cursor.fetchall()
    
    # Department breakdown (for the chart)
    cursor.execute("SELECT department, COUNT(*) as count FROM complaints GROUP BY department")
    dept_stats = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return render_template(
        "admin_dashboard.html",
        total=total,
        new_count=new_count,
        pending=pending,
        resolved=resolved,
        resolved_pct=round(resolved_pct, 1),
        complaints=all_complaints,
        users=system_users,
        dept_details=detailed_dept_stats,
        dept_analytics=dept_analytics_data,
        selected_dept=selected_dept,
        dept_stats=dept_stats,
        view=view
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
