# 负责验证客户端，和分发消息内容
## 验证流程
### 第一步  
客户端与服务端建立连接，完成三次握手等一系列准备工作(交给底层库和操作系统完成)  
### 第二步  
客户端发送ClientHello，格式如下  
```
{
  "type": "Client",
  "load": "ClientHello",
  "client": "QQ",
  "name": "XXXX"
}
```
### 第三步
服务端发送ServerHello,格式如下
```
{
  "type": "Server",
  "load": "ServerHello",
  "connection": "keep-alive",
  "uuid": 返回连接时产生的uuid
}
```
### 第四步  
连接建立传输数据,今后每次发送数据均需携带uuid信息  
