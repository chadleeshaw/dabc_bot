# Utah DABC Discord Bot

This bot will once a day post Utah DABC limited and Allocated items to Discord.

Requirements:
```
Discord Webhook
```

Usage:
```
docker run -d \
-e BOOZE_TIME=12:00 \ #Optional
-e TZ=America/{yourtimezone} \
-e ALLOCATED_HOOK={yourdiscordwebhook} \
-e LIMITED_HOOK={yourdiscordwebhook} \
-e DRAWINGS_HOOK={yourdiscordwebhook} \
ghcr.io/chadleeshaw/dabc_bot:latest
```
