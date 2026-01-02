import os
import shutil
import csv

BASE_DIR = os.path.abspath("reference_images")
ENV_DIR = os.path.abspath("Environments")
MAPPING_FILE = os.path.join(ENV_DIR, "mapping.csv")

# Mapping from reference_images subfolders to Environments subfolders
FOLDER_MAPPING = {
    "Etappe_1/Mount_Sinai": "Sinai_Port_V1",
    "Etappe_1/Negev_Desert": "Desert_Transition",
    "Etappe_1/Judean_Mountains": "Cold_Storage_Caves",
    "Etappe_1/Qumran_Caves": "Cold_Storage_Caves",
    "Etappe_1/Mount_Hermon": "Hermon_Ingress_Hub",
    "Etappe_2/Jordan_Rift_Valley": "Rift_Valley_Black",
    "Etappe_2/Dallol_Ethiopia": "Rift_Valley_Yellow",
    "Etappe_2/Simien_Mountains": "Ethiopian_Highlands",
    "Etappe_3/Indian_Ocean_Coast": "Socotra_Coast",
    "Etappe_3/Socotra_Island": "Gold_Master_Eden",
    "Etappe_3/Svalbard": "The_North_Ice",
    "Etappe_4/Wadi_Rum": "Astronomical_Desert",
    "Etappe_4/Jerusalem_Gehenna": "Gehenna_Data_Sink",
    "Etappe_4/Jerusalem_Kidron": "Gehenna_Data_Sink",
    "Etappe_1/Tel_Dan": "unsortiert",
    "Etappe_3/Atmospheric_IO_Gates": "Atmospheric_IO_Gates",
    "Etappe_2/Core_Cluster_Mountains": "Core_Cluster_Mountains",
    "Etappe_2/Root_Mainframe_Hall": "Root_Mainframe_Hall"
}

def distribute_images():
    new_mappings = []
    
    print("Starting distribution of reference images...")
    
    for src_sub, target_name in FOLDER_MAPPING.items():
        src_path = os.path.join(BASE_DIR, src_sub)
        target_path = os.path.join(ENV_DIR, target_name)
        
        if not os.path.exists(src_path):
            print(f"Skipping {src_sub} (Source not found)")
            continue
            
        if not os.path.exists(target_path):
            os.makedirs(target_path)
            print(f"Created directory: {target_path}")
            
        # Iterate over files in source
        for filename in os.listdir(src_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                src_file = os.path.join(src_path, filename)
                
                # Create a unique filename to avoid collisions
                # e.g. Mount_Sinai_image_1.jpg
                prefix = src_sub.replace("/", "_").replace("\\", "_")
                new_filename = f"{prefix}_{filename}"
                target_file = os.path.join(target_path, new_filename)
                
                # Copy file
                shutil.copy2(src_file, target_file)
                print(f"Copied {filename} -> {target_name}/{new_filename}")
                
                # Add to mapping list
                new_mappings.append([new_filename, target_name, "Reference Image"])

    # Update mapping.csv
    if new_mappings:
        print(f"\nUpdating {MAPPING_FILE} with {len(new_mappings)} new entries...")
        
        file_exists = os.path.exists(MAPPING_FILE)
        
        with open(MAPPING_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Image_Filename", "Target_Folder_Name", "Notes"])
            
            writer.writerows(new_mappings)
        print("Mapping file updated.")
    else:
        print("No new images found to map.")

if __name__ == "__main__":
    distribute_images()
