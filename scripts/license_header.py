import os
import sys

# Define the license header you expect in each file
LICENSE_HEADER = '''"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""'''


def check_and_add_license_header(file_path):
    with open(file_path, "r+", encoding="utf-8") as file:
        content = file.read()
        if LICENSE_HEADER not in content:
            print(f"Adding license header to: {file_path}")
            file.seek(0, 0)
            file.write(LICENSE_HEADER + "\n" + content)
            return False
    return True


def main():
    if len(sys.argv) != 2:
        print("Usage: python check_license_header.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    all_files_passed = True

    for root, _, files in os.walk(directory):
        if "build" in root.split(os.path.sep):
            continue
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if not check_and_add_license_header(file_path):
                    print(f"License header missing in: {file_path}")
                    all_files_passed = False

    if not all_files_passed:
        sys.exit(1)
    else:
        print("All files have the correct license header.")


if __name__ == "__main__":
    main()
