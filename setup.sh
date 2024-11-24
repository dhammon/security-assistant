#!/bin/bash

#run following on VM to setup
apt update -y
apt install pip -y
apt install curl -y

#install ollama
curl -fsSL https://ollama.com/install.sh | sh

#pull llama
ollama pull llama3:instruct  #because it fails the first time lol
ollama pull llama3:instruct
ollama pull nomic-embed-text

#install requirements
pip install -r requirements.txt

echo "============DONE!=============="

