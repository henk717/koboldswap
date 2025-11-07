#!/usr/bin/env python3
"""
Kobold-Swap, a simple wrapper to make llama-swap very easy in the KoboldCpp ecosystem.
Simply place your .kcpps files (with showgui and browser launching disabled) in the configs folder.
Place a koboldcpp executable next to the tool and the rest is automatic.
"""

import os
import yaml
from pathlib import Path
import sys
import subprocess
import platform


def find_kcpps_files(configs_dir="configs"):
    """
    Find all .kcpps files in the configs directory.
    
    Args:
        configs_dir (str): Path to the configs directory
        
    Returns:
        list: List of .kcpps file paths
    """
    configs_path = Path(configs_dir)
    
    if not configs_path.exists():
        print(f"Error: Configs directory '{configs_dir}' not found.")
        return []
    
    kcpps_files = list(configs_path.glob("*.kcpps"))
    
    if not kcpps_files:
        print(f"Warning: No .kcpps files found in '{configs_dir}'.")
        return []
    
    return kcpps_files


def extract_filename(file_path):
    """
    Extract filename without extension from a file path.
    
    Args:
        file_path (Path): Path to the file
        
    Returns:
        str: Filename without extension
    """
    return file_path.stem


def generate_config_entry(filename):
    """
    Generate a config.yaml entry for a given filename.
    
    Args:
        filename (str): Filename without extension
        
    Returns:
        dict: Configuration entry
    """
    return {
        f"koboldcpp/{filename}": {
            "cmd": f"kcpp-extracted/koboldcpp-launcher --config configs/{filename}.kcpps --port ${{PORT}} --hordemodelname {filename}",
            "checkEndpoint": "/ping"
        }
    }


def generate_config_yaml(kcpps_files, output_file="config.yaml"):
    """
    Generate config.yaml from .kcpps files.
    
    Args:
        kcpps_files (list): List of .kcpps file paths
        output_file (str): Output YAML file path
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not kcpps_files:
        print("No .kcpps files to process.")
        return False
    
    # Create models structure
    models = {}
    
    for kcpps_file in kcpps_files:
        filename = extract_filename(kcpps_file)
        entry = generate_config_entry(filename)
        models.update(entry)
    
    # Create complete config structure
    config = {
        "models": models
    }
    
    try:
        # Write YAML file
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print(f"Successfully generated {output_file}")
        return True
        
    except Exception as e:
        print(f"Error writing {output_file}: {e}")
        return False


def launch_llama_swap():
    """
    Launch llama-swap as a subprocess.
    
    Returns:
        subprocess.Popen: Process object for llama-swap
    """
    try:
        basepath = os.path.abspath(os.path.dirname(__file__))
        # Determine the executable name based on platform
        if platform.system() == "Windows":
            executable = os.path.join(basepath, "llama-swap.exe")
        else:
            executable = os.path.join(basepath, "llama-swap")
        
        # Check if executable exists
        if not os.path.exists(executable):
            print(f"Warning: {executable} not found. Skipping llama-swap launch.")
            return None
        
        print(f"Launching {executable}...")
        process = subprocess.Popen([executable])
        return process
        
    except Exception as e:
        print(f"Error launching llama-swap: {e}")
        return None


def main():
    """
    Main function to generate config.yaml and launch llama-swap
    """
    print("Kobold Swap")

    if not os.path.exists("configs"):
        os.makedirs("configs")
        print("Configs folder created, place your .kcpps files here.\n Make sure they are set to not show the launcher and don't launch a browser")
        quit("")

    # 2. Check and run koboldcpp --unpack if 'kcpp-extracted' doesn't exist
    if not os.path.exists("kcpp-extracted"):
        # This command works on Windows, macOS, and Linux
        subprocess.run(["koboldcpp", "--unpack", "kcpp-extracted"])

    # Find .kcpps files
    kcpps_files = find_kcpps_files()
    
    if not kcpps_files:
        print("No .kcpps files found. Exiting.")
        return
    
    # Generate config.yaml
    success = generate_config_yaml(kcpps_files)
    
    if success:
        print("Config generation completed successfully!")
        
        # Launch llama-swap
        llama_swap_process = launch_llama_swap()
        
        if llama_swap_process:
            print("llama-swap launched successfully!")
            # Keep the script running
            try:
                llama_swap_process.wait()
            except KeyboardInterrupt:
                print("\nShutting down llama-swap...")
                llama_swap_process.terminate()
                llama_swap_process.wait()
    else:
        print("Config generation failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()