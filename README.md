# Utah DABC Discord Bot

This bot will once a day post Utah DABC limited and Allocated Whiskeys to Discord.

Requirements:
```
Discord Webhook
```

Usage:
```
docker run -d \
-e BOOZE_TIME=12:00 \ #Optional
-e TZ=America/{yourtimezone} \
-e BOURBON_ALLOCATED_HOOK={yourdiscordwebhook} \
-e BOURBON_LIMITED_HOOK={yourdiscordwebhook} \
-e DRAWINGS_HOOK={yourdiscordwebhook} \
-e TEQUILA_ALLOCATED_HOOK={yourdiscordwebhook} \
-e TEQUILA_LIMITED_HOOK={yourdiscordwebhook} \
ghcr.io/chadleeshaw/dabc_bot:latest
```
