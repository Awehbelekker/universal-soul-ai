"""Quick fix for UserContext instances"""

# Read the file
with open('final_validation_test.py', 'r') as f:
    content = f.read()

# Replace all UserContext instances
old_pattern = """UserContext(
                user_id="test_user",
                preferences={},
                session_data={},
                device_info={}
            )"""

new_pattern = """UserContext(
                user_id="test_user",
                preferences={},
                session_data={},
                device_info={},
                privacy_settings={}
            )"""

content = content.replace(old_pattern, new_pattern)

# Write back
with open('final_validation_test.py', 'w') as f:
    f.write(content)

print("Fixed all UserContext instances")
