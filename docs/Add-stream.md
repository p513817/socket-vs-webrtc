# Public RTSP
```
"27aec28e-6181-4753-9acd-0456a75f0289": {
  "channels": {
    "0": {
      "url": "rtmp://171.25.232.10/12d525bc9f014e209c1280bc0d46a87e",
      "debug": false,
      "audio": true
    }
  },
  "name": "111111111"
}
```

# Add a Stream

```bash
curl \
--header "Content-Type: application/json" \
--request POST \
--data '{
            "name": "test video",
            "channels": {
                "0": {
                    "name": "ch1",
                    "url": "rtmp://171.25.232.10/12d525bc9f014e209c1280bc0d46a87e",
                    "on_demand": false,
                    "debug": false,
                    "status": 0
                },
            }
        }' \
http://demo:demo@127.0.0.1:8083/stream/27aec28e-6181-4753-9acd-0456a75f0289/add
```