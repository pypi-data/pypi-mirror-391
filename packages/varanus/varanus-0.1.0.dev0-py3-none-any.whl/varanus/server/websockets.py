async def websocket_application(scope, receive, send):
    while True:
        event = await receive()
        match event["type"]:
            case "websocket.connect":
                print("CONNECT", scope)
                await send({"type": "websocket.accept"})
            case "websocket.disconnect":
                break
            case "websocket.receive":
                print(event)
            case _:
                print("UNKNOWN EVENT", event)
