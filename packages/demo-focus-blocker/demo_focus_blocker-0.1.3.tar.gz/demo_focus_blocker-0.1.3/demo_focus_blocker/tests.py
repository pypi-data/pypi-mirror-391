from blocker import FocusBlocker

# Create a blocker instance
blocker = FocusBlocker()

# Check if a URL should be blocked
url = "https://www.youtube.com/watch?v=abc123"
if blocker.is_blocked(url):
    print("This website is blocked during focus hours!")
else:
    print("Website is allowed")

# Add custom sites to block
blocker.add_site("tiktok.com")
blocker.add_site("instagram.com")

# Set custom focus hours (8 AM to 6 PM)
blocker.set_focus_hours(8, 18)

# Get current status
status = blocker.get_status()
print(status)
