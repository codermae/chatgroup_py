# -*- coding = utf-8 -*-
# @Time : 2025/3/12 16:52
# @Author : mae
# @File : client.py
# @software : PyCharm
import wx
from socket import socket,AF_INET,SOCK_STREAM
import threading
class myClient(wx.Frame):
    def __init__(self,client_name):
        # 创建窗口
        wx.Frame.__init__(
            self,None,id=1001,title=client_name+'的客户端',
            pos=wx.DefaultPosition,size=(400,450)
        )
        # 创建面板
        pl = wx.Panel(self)

        # 创建主垂直布局管理器
        main_box = wx.BoxSizer(wx.VERTICAL)

        # 第一行：连接和断开按钮
        button_box1 = wx.BoxSizer(wx.HORIZONTAL)
        conn_btn = wx.Button(pl, size=(100, 40), label='连接')
        dis_conn_btn = wx.Button(pl, size=(100, 40), label='断开')
        button_box1.Add(conn_btn, 0, wx.ALL, 5)  # 添加外边距
        button_box1.Add(dis_conn_btn, 0, wx.ALL, 5)
        main_box.Add(button_box1, 0, wx.ALIGN_CENTER | wx.ALL, 10)  # 水平居中并添加外边距

        # 第二行：只读文本框
        self.show_text = wx.TextCtrl(pl, size=(300, 110), style=wx.TE_MULTILINE | wx.TE_READONLY)
        main_box.Add(self.show_text, 1, wx.EXPAND | wx.ALL, 10)  # 文本框可伸展并添加外边距

        # 第三行：聊天文本框
        self.chat_text = wx.TextCtrl(pl, size=(300, 110), style=wx.TE_MULTILINE)
        main_box.Add(self.chat_text, 1, wx.EXPAND | wx.ALL, 10)  # 文本框可伸展并添加外边距

        # 第四行：重置和发送按钮
        button_box2 = wx.BoxSizer(wx.HORIZONTAL)
        reset_btn = wx.Button(pl, size=(100, 40), label='重置')
        send_btn = wx.Button(pl, size=(100, 40), label='发送')
        button_box2.Add(reset_btn, 0, wx.ALL, 5)  # 添加外边距
        button_box2.Add(send_btn, 0, wx.ALL, 5)
        main_box.Add(button_box2, 0, wx.ALIGN_CENTER | wx.ALL, 10)  # 水平居中并添加外边距

        # 将主布局管理器设置到面板
        pl.SetSizer(main_box)
# =====================================================================================================
        self.Bind(wx.EVT_BUTTON,self.connect_to_server,conn_btn)
        # 实例属性的设置
        self.client_name = client_name
        # 存储客户端连接服务器的状态
        self.isConnected = False
        # 设置客户端的socket对象为空
        self.client_socket = None
        # 发送按钮
        self.Bind(wx.EVT_BUTTON,self.send_to_serve,send_btn)
        # 断开链接按钮
        self.Bind(wx.EVT_BUTTON,self.dis_conn_server,dis_conn_btn)
        # 重置按钮
        self.Bind(wx.EVT_BUTTON,self.reset,reset_btn)

    def connect_to_server(self,event):
        print(f'客户端【{self.client_name}】连接服务器...')
        # 开始连接服务器
        if not self.isConnected:
            server_host_port = ('127.0.0.1',7776)
            # 创建socket对象
            self.client_socket = socket(AF_INET,SOCK_STREAM)
            # 发送链接请求
            self.client_socket.connect(server_host_port)
            # 如果连接成功，发送一条数据 自报家门
            self.client_socket.send(self.client_name.encode('utf-8'))
            # 启动一个线程，客户端的线程与服务器的会话线程进行会话
            client_thread = threading.Thread(target=self.recv_data)
            # 设置守护线程
            client_thread.daemon = True
            # 修改连接状态
            self.isConnected = True
            # 启动线程
            client_thread.start()

    def send_to_serve(self,event):
        # 判断链接状态
        if self.isConnected:
            # 获取输入框内容
            input_data = self.chat_text.GetValue()
            if input_data != '':
                # 发送数据
                self.client_socket.send(input_data.encode('utf-8'))
                # 清空输入框
                self.chat_text.SetValue('')

        pass

    def dis_conn_server(self,event):
        # 发送断开请求
        self.client_socket.send('disconnect'.encode('utf-8'))
        # 改变链接状态
        self.isConnected = False

    def reset(self,event):
        self.chat_text.Clear()

    def recv_data(self):
        while self.isConnected:
            # 接收数据
            data = self.client_socket.recv(1024).decode('utf-8')
            # 显示数据
            self.show_text.AppendText('-'*40+'\n'+data+'\n')

if __name__ == '__main__':
    # 初始化APP
    app = wx.App()
    name = input('请输入你的客户端名称：')
    client = myClient(name)
    client.Show()

    # 循环刷新显示
    app.MainLoop()