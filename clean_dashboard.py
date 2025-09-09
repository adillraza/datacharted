#!/usr/bin/env python3
"""
Clean up the dashboard template to remove hardcoded values
"""

def main():
    # Read the dashboard template
    with open('app/templates/main/dashboard.html', 'r') as f:
        content = f.read()
    
    # Replace hardcoded "2 Active" with dynamic placeholder
    content = content.replace(
        '<h4 id="bigquery-status" class="text-success mb-2">2 Active</h4>',
        '<h4 id="bigquery-status" class="text-muted mb-2">Loading...</h4>'
    )
    
    # Write back the cleaned template
    with open('app/templates/main/dashboard.html', 'w') as f:
        f.write(content)
    
    print("✅ Dashboard template cleaned - removed hardcoded '2 Active'")

if __name__ == "__main__":
    main()
