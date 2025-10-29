#!/bin/bash
docker run -d -v ./files/chroma-data:/data -p 8000:8000 chromadb/chroma
