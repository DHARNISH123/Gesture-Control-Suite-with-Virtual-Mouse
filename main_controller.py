import subprocess
import sys
import os

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_script(script_name):
    try:
        subprocess.run([sys.executable, script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: Script '{script_name}' exited with error.")
    except FileNotFoundError:
        print(f"❌ Error: '{script_name}' not found.")
    except Exception as e:
        print(f"❌ Unexpected error while running '{script_name}': {e}")

def main():
    try:
        while True:
            clear_console()
            print("""
==========================================
        🎮 Gesture Control Suite
==========================================
Choose a mode:
 1️⃣  Virtual Mouse Control
 2️⃣  YouTube Gesture Control
 3️⃣  Presentation Gesture Control
 0️⃣  Exit
""")
            choice = input("Enter your choice (0-3): ").strip()

            if choice == '1':
                run_script("virtual_mouse_advanced.py")
            elif choice == '2':
                run_script("youtube_gesture_control.py")
            elif choice == '3':
                run_script("presentation_gesture_control.py")
            elif choice == '0':
                print("\n👋 Exiting Gesture Control Suite. Goodbye!\n")
                break
            else:
                print("❗ Invalid choice. Please enter a number between 0 and 3.")

            input("\nPress ENTER to return to menu...")

    except KeyboardInterrupt:
        print("\n\n👋 Exiting Gesture Control Suite (Keyboard Interrupt). Goodbye!")

if __name__ == "__main__":
    main()
