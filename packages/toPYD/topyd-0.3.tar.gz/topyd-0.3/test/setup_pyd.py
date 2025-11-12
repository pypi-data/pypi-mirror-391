from src.toPYD import to_pyd
import sys
import os

startup_file_name = os.path.basename(sys.argv[0])
print(startup_file_name)

if __name__ == '__main__':
    to_pyd(
        exclude=[
            startup_file_name,
            '*.pyc',
            '*.pyo',
            'build_pyd',
        ]
    )

    raise Exception("找一个崩溃")
