# this file is used to replace the command "cp -r {input} {output}"
# in the snakerule "rule prepare_example" because it did not work on Windows
import sys
import shutil

src = sys.argv[1]
dst = sys.argv[2]

shutil.copytree(src=src, dst=dst)
