#!/bin/bash

export GOOGLE_SCHOLAR_QUERY='("deep learning" OR "neural network") AND \
                             ("image classification" OR "image recognition")'

python3 -m crawler \
            --stop-pretty-print \
            --max 1000 \
            --min-year 2021

