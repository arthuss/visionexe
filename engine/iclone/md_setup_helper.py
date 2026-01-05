rl_plugin_info = {"ap": "iClone", "ap_version": "8.0"}

import RLPy

def create_md_target():
    # 1. Check if target exists
    target_name = "MD_Target"
    target = RLPy.RScene.FindObject(RLPy.EObjectType_Prop, target_name)
    
    if not target:
        # Create a simple box as target if not found
        # Note: RLPy doesn't have a simple "CreatePrimitive" in all versions.
        # We might need to load a prop. But let's check if we can assume one exists.
        print(f"Target '{target_name}' not found. Please create a primitive (Box) and name it '{target_name}'.")
        RLPy.RUi.ShowMessageBox(f"Please create a Prop named '{target_name}' to serve as the destination.", "Setup Required", RLPy.EMsgButton_Ok)
        return None
    else:
        print(f"Target '{target_name}' found.")
        return target

def setup_avatar_follow(target):
    avatars = list(RLPy.RScene.GetAvatars())
    if not avatars:
        print("No avatar found.")
        return

    avatar = avatars[0]
    print(f"Configuring Avatar: {avatar.GetName()}")

    # Try to find MD Control to set target
    # Since direct API is undocumented, we print instructions for the user
    msg = (
        f"1. Open Motion Director (MD) panel.\n"
        f"2. Select '{avatar.GetName()}'.\n"
        f"3. In MD settings, switch to 'Follow Object' mode.\n"
        f"4. Pick '{target.GetName()}' as the target.\n"
        f"5. Now you can run the 'animate_md_target.py' script."
    )
    RLPy.RUi.ShowMessageBox(msg, "Manual MD Setup", RLPy.EMsgButton_Ok)

def main():
    target = create_md_target()
    if target:
        setup_avatar_follow(target)

if __name__ == "__main__":
    main()
