import os
print('path: {}'.format(os.environ["PATH"]))
open(r"C:\Python34\Scripts\python3.bat", "w").write(r"@C:\Python34\python %*")
print("\n".join(repr(e) for e in os.walk(r"C:\Python34")))
print(open(r"C:\Python34\Scripts\python3.bat", "r").read())
