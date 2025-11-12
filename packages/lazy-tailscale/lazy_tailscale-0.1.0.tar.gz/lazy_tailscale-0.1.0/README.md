

## Interface


```python
client = TailscaleClient(token="ABC", tailnet="my-tailnet")
devices = client.list_devices()

client = AsyncTailscaleClient(token="ABC", tailnet="my-tailnet")
devices = await client.list_devices()


## Development
`source .env && uv run textual run --dev -c lazytailscale --port 7342`
`uv run textual console --port 7342 -x SYSTEM -x DEBUG -x INFO`





```
```


```
