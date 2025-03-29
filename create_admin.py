from models import User

# Check if an admin user already exists
admin_exists = False
for user in User.get_all():
    if user.role == 'admin':
        admin_exists = True
        print(f"Admin user already exists: {user.username} ({user.email})")
        break

# Create admin user if none exists
if not admin_exists:
    admin_user = User(
        username="admin",
        email="admin@example.com",
        password="admin123",  # This is a temporary password, change it in production
        role="admin"
    )
    
    if admin_user.save():
        print(f"Admin user created successfully: {admin_user.username} ({admin_user.email})")
        print("Password: admin123")
    else:
        print("Failed to create admin user")

# Display all users for verification
print("\nAll users in the system:")
for user in User.get_all():
    print(f"- {user.username} ({user.email}) - Role: {user.role}")