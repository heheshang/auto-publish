import websocket
import json

def connect_to_websocket():
    # 建立 WebSocket 连接
    ws = websocket.WebSocket()
    ws.connect("wss://itos-dify-chat-test.local.opentide.com.cn/ws")
    
    # 发送消息示例
    message = {
        "type": "connection_init",
        "payload": {}
    }
    ws.send(json.dumps(message))
    
    # 接收响应
    response = ws.recv()
    print(f"Received: {response}")
    
    # 关闭连接
    ws.close()

# 使用示例
if __name__ == "__main__":
    connect_to_websocket()