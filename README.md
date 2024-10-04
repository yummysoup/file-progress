# file-progress

Show progress processing files on linux

# What it actually does

Looks at open files on the system and reports the current seek position as a percent of total size

# When you'd want to use it

Let's say you've got a slow process that works with local files (CPU-intensive transformations, ETL process, upload, etc.) but your processing tool doesn't report progress. This will let you know how much of your file has been read so far.

Repeated invocations can give hints of overall throughput and let you guess how long you have left.

# USAGE

```
chmod +x progress.py
./progress.py
```

# History
This was originally written for python 2 and probably could benefit from some clean up.