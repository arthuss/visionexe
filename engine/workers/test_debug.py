import subprocess
import time
import shutil

def resolve_gemini_command():
    gemini_path = shutil.which("gemini") or shutil.which("gemini.cmd")
    if gemini_path:
        return f"\"{gemini_path}\""

    npx_path = shutil.which("npx") or shutil.which("npx.cmd")
    if npx_path:
        return f"\"{npx_path}\" -y @google/gemini-cli"

    return None

def test_large_input():
    print("Testing gemini-cli with LARGE stdin...")
    timeout_sec = 60
    
    # Simulate a large prompt like drehbuch.py
    large_prompt = "Hello " * 1000 + "\nAnalyze this text and tell me about it."

    try:
        # Mimic drehbuch.py's current Popen structure
        print("--- Using Popen raw write (Old Method) ---")
        cmd = resolve_gemini_command()
        if not cmd:
            print("Gemini CLI nicht gefunden (gemini/npx).")
            return

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            encoding='utf-8',
            shell=True 
        ) 
        
        try:
            print(f"Sending prompt ({len(large_prompt)} chars)...")
            process.stdin.write(large_prompt)
            process.stdin.close()

            output, stderr = process.communicate(timeout=timeout_sec)
            print(f"Return code: {process.returncode}")
            if process.returncode != 0:
                print(f"Stderr: {stderr}")
            else:
                print("Success (Old Method)")
                
        except BrokenPipeError:
            print("Caught BrokenPipeError!")
            # Read stderr to see why it died
            try:
                _, stderr = process.communicate(timeout=timeout_sec)
            except subprocess.TimeoutExpired:
                process.kill()
                _, stderr = process.communicate()
            print(f"Stderr after crash: {stderr}")
        except subprocess.TimeoutExpired:
            process.kill()
            output, stderr = process.communicate()
            print(f"Timed out after {timeout_sec}s (Old Method)")
            if stderr:
                print(f"Stderr: {stderr}")
            
        
        print("\n--- Using communicate (New Method) ---")
        process2 = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            encoding='utf-8',
            shell=True 
        ) 
        
        try:
            stdout2, stderr2 = process2.communicate(input=large_prompt, timeout=timeout_sec)
            print(f"Return code: {process2.returncode}")
            if process2.returncode != 0:
                print(f"Stderr: {stderr2}")
            else:
                print("Success (New Method)")
                # print(f"Output: {stdout2[:100]}...")
        except subprocess.TimeoutExpired:
            process2.kill()
            stdout2, stderr2 = process2.communicate()
            print(f"Timed out after {timeout_sec}s (New Method)")
            if stderr2:
                print(f"Stderr: {stderr2}")

    except Exception as e:
        print(f"General Error: {e}")

if __name__ == "__main__":
    test_large_input()
