import os
import subprocess
import re
import tempfile
import sys

def import_task_keep_user_fix_sid(xml_filename):
    """
    Reads an exported Task Scheduler XML, removes the machine-specific SID,
    but KEEPS the <UserId> (username), then imports it.
    """
    
    if not os.path.exists(xml_filename):
        print(f"Error: File '{xml_filename}' not found.")
        return

    # 1. Read the original XML
    with open(xml_filename, 'r', encoding='utf-16') as f:
        xml_content = f.read()

    # 2. Remove the <UserId> SID inside <Principals>
    # We want to keep the <UserId> inside <Triggers> (which is the username),
    # but remove the <UserId> inside <Principal> (which is the SID: S-1-5-21...).
    # The regex looks for the pattern S-1-5-xx... and removes that line.
    
    print("Processing XML to make it compatible...")
    
    # Regex to find the Principal UserId (the SID) and remove it.
    # We look for <UserId>S-1-...</UserId> and replace it with nothing, 
    # letting Windows resolve the Principal from the Context or Triggers.
    # Alternatively, we can just remove the whole <UserId> tag if it starts with S-1-
    
    fixed_xml = re.sub(r'<UserId>S-1-5-.*?</UserId>', '', xml_content)

    # 3. Save to a temporary file
    try:
        # Create temp file (must be UTF-16 for Task Scheduler)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml", mode='w', encoding='utf-16') as temp_xml:
            temp_xml.write(fixed_xml)
            temp_xml_path = temp_xml.name

        # 4. Import the Task
        task_name = "AutoSpaceManager" # You can change this name
        
        # /TN = Task Name, /XML = Path to XML, /F = Force overwrite
        command = ["schtasks", "/Create", "/F", "/TN", task_name, "/XML", temp_xml_path]
        
        print(f"Importing task '{task_name}'...")
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print("\nSUCCESS: Task imported successfully.")
        else:
            print("\nERROR: Import failed.")
            print("Windows Output:", result.stderr)

    except Exception as e:
        print(f"Script Error: {e}")
        
    finally:
        # Clean up temp file
        if 'temp_xml_path' in locals() and os.path.exists(temp_xml_path):
            os.remove(temp_xml_path)

if __name__ == "__main__":
    print(sys.argv)
    filename = ""
    if len(sys.argv) < 1:
        filename = input('Input filename of the task to be imported: ')
    if not filename:
        tasks = ["Z:\space killer\Auto space manager.xml"]
        for task in tasks:
            import_task_keep_user_fix_sid(task)
        exit()
    # filename of your exported XML
    import_task_keep_user_fix_sid(filename)