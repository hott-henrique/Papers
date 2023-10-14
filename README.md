# Papers
Crawler to find papers of a given query using Google Scholar.

# Install
```bash
# pip install -r requirements.txt
```

# Execution
There is two ways of executing the script, the first is using environment variables:
```bash
export GOOGLE_SCHOLAR_QUERY='("deep learning" OR "neural network") AND \
                             ("image classification" OR "image recognition")'

python3 -m crawler \
             --max 1000 \
             --min-year 2021
```
or using the argument option:
```bash
python3 -m crawler \
             --query '("deep learning" OR "neural network") AND ("image classification" OR "image recognition")'
             --max 1000 \
             --min-year 2021
```
Maybe you want to pipe the objects to another command:
```bash
python3 -m crawler \
             --query '("deep learning" OR "neural network") AND ("image classification" OR "image recognition")' \
             --max 10 \
             --min-year 2021 \
             --stop-pretty-print | grep --ignore-case "ieee"
```
