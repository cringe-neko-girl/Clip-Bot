# Clip Bot

Clip Bot is a Discord bot designed to clip users' messages efficiently, providing easy access to clipped messages, images of the clipped messages, and a variety of helpful commands for managing clips within your server.

## Goals
- **Message Clipping:** Clip user's messages and send images of the clipped messages.
- **Message Linking:** Provide links to the messages that are clipped for easy reference.
- **Easy-to-Use Commands:** Implement simple commands for interacting with the bot and accessing information about clipped messages.
- **Star Board Integration:** Allow clipped messages to be displayed in a starboard channel for recognition.
- **User Clips Access:** Provide a command to access all the clips of a specific user.
- **Sane Leaderboard:** Generate a leaderboard ranking users from most to least sane based on their clipped messages.
- **Command Help Menu:** Design a user-friendly command help menu with a selection menu for easy navigation.
- **Easy Configuration:** Ensure the bot is easy to configure and set up for server administrators.

## Invite Clip Bot to Your Server | Warning its still in development
[![Invite Clip Bot](https://img.shields.io/badge/Invite-Clip_Bot-blue?style=for-the-badge)](https://discord.com/oauth2/authorize?client_id=1226365381527081020&permissions=2147601600&scope=bot)

## Join Our Discord Server
[![Join Our Discord Server](https://img.shields.io/badge/Join-Discord_Server-blue?style=for-the-badge)](https://discord.gg/mm5738HDxH)

## Status
Clip Bot is under active development and aims to provide a seamless experience for managing clipped messages within your Discord server. Feel free to reach out on our Discord server if you encounter any issues or have suggestions for improvement.

---

# Developer Notes

- Editing  / Restarting Code:
  -  Apply the updated deployment manifest to your Kubernetes cluster
      ```
      $ kubectl apply -f   kubernetes/deployment.yaml
      ```

  - Restarting

     ```
     $ docker build -t senkosanbroentername/clip-bot:newversion .
     $ docker push senkosanbroentername/clip-bot:newversion
    
    # Run newversion
     $ kubectl rollout restart deployment clip-bot
    ```
  -  Checking Uptime
     ```
        $ kubectl get pods
     ```

