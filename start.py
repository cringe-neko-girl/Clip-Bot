import os

os.system("docker build -t senkosanbroentername/clip-bot:newversion .")
os.system("docker push senkosanbroentername/clip-bot:newversion")
os.system("kubectl rollout restart deployment clip-bot")
