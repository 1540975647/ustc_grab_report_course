#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ustc_grab.config import Config
from ustc_grab.manager import CourseManager
import random
import time

def main():
    # Adding random sleep as per original logic
    time.sleep(random.randint(0, 60))
    
    try:
        from pathlib import Path
        import os
        # Use simple os.path to determine the directory of the script
        base_dir = Path(__file__).resolve().parent
        config = Config(base_dir=base_dir)
        manager = CourseManager(config)
        manager.keep_alive_routine()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
