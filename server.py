# -*- coding = utf-8 -*-
# @Time : 2025/3/12 17:43
# @Author : mae
# @File : server.py
# @software : PyCharm
import wx
from socket import socket,AF_INET,SOCK_STREAM
import threading
import time

class myServer(wx.Frame):
    # 窗口绘制部分
    def __init__(self):
        # 设置窗口
        wx.Frame.__init__(self,None,id=1002,title='SERVER界面',pos=wx.DefaultPosition,size=(400,500))
        # 设置面板
        pl = wx.Panel(self)
        # 创建一个垂直方向的BoxSizer用于整体布局
        main_box = wx.BoxSizer(wx.VERTICAL)
        # 创建一个水平方向的BoxSizer用于按钮布局
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        # 添加按钮
        start_server_btn = wx.Button(pl, size=(100, 40), label='启动服务')
        save_btn = wx.Button(pl, size=(100, 40), label='保存聊天记录')
        stop_server_btn = wx.Button(pl, size=(100, 40), label='停止服务')
        # 将按钮添加到水平BoxSizer中
        button_box.Add(start_server_btn, 0, wx.ALL, 5)  # 添加外边距
        button_box.Add(save_btn, 0, wx.ALL, 5)
        button_box.Add(stop_server_btn, 0, wx.ALL, 5)
        # 将按钮的水平BoxSizer添加到主垂直BoxSizer中
        main_box.Add(button_box, 0, wx.ALIGN_CENTER | wx.ALL, 10)  # 水平居中并添加外边距
        # 设置文本显示框
        self.show_text = wx.TextCtrl(pl, size=(200, 100), style=wx.TE_MULTILINE | wx.TE_READONLY)
        # 将文本框添加到主垂直BoxSizer中
        main_box.Add(self.show_text, 1, wx.EXPAND | wx.ALL, 10)  # 文本框可伸展并添加外边距
        # 将主垂直BoxSizer设置到面板
        pl.SetSizer(main_box)
        # ================================功能部分====================================================================
        self.isOn = False       # 服务启动状态
        self.host_port = ('127.0.0.1',7776)         # 服务器地址端口
        # 创建一个TCP套接字（用来监听和接受客户端的连接请求）。AF_INET表示使用IPv4地址族，SOCK_STREAM表示使用TCP协议
        self.server_socket = socket(AF_INET,SOCK_STREAM)
        self.server_socket.bind(self.host_port)         # 绑定地址端口
        self.server_socket.listen(5)        # 开始监听 队列长度5
        # 创建字典存储会话   客户端名称:会话线程
        self.session_thread_dict = {}
        # 绑定按钮事件（button事件-对应函数-对应button）
        self.Bind(wx.EVT_BUTTON,self.start_server,start_server_btn)
        self.Bind(wx.EVT_BUTTON,self.save_record,save_btn)
        self.Bind(wx.EVT_BUTTON,self.stop_server,stop_server_btn)


    # 服务启动函数
    def start_server(self,event):
        if not self.isOn:
            self.isOn = True
            # 函数式创建主线程
            main_thread = threading.Thread(target=self.do_work)
            # 设置守护线程
            main_thread.daemon = True
            # 启动主线程
            main_thread.start()

    def save_record(self,event):
        # 获取聊天内容
        saved_data = self.show_text.GetValue()
        with open('record.log','a',encoding='utf-8') as file:
            file.write('o'*40 + '\n')
            file.write(saved_data)
            file.write('o' * 40 + '\n')
            print('聊天记录已保存')

    def stop_server(self,event):
        self.show_info_and_sendto_client('服务器通知', '服务器已断开,会话结束.',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        print('服务器断开中。。。')
        self.isOn = False
        # 关闭监听套接字，防止新的客户端连接
        try:
            self.server_socket.close()
        except Exception as e:
            print(f'关闭服务器套接字时发生异常：{e}')
        # 通知所有会话线程退出
        for session_thread in self.session_thread_dict.values():
            session_thread.isOn = False
            try:
                session_thread.client_socket.close()
            except Exception as e:
                print(f'关闭客户端套接字时发生异常：{e}')
        # 等待所有会话线程结束
        for session_thread in self.session_thread_dict.values():
            session_thread.join()
        print('---服务器断开完毕---')



    def do_work(self):
        while self.isOn:
            try:
                # 开始接收客户端链接请求
                session_socket, client_addr = self.server_socket.accept()
                # 接收数据，user_name由客户端默认自动发送
                user_name = session_socket.recv(1024).decode('utf-8')
                # 创建会话线程SessionThread对象
                session_thread = SessionThread(session_socket, user_name, self)
                # 线程对象存到字典
                self.session_thread_dict[user_name] = session_thread
                # 启动会话线程
                session_thread.start()
                # 输出服务器的提示信息
                self.show_info_and_sendto_client('服务器通知', f'{user_name}进入了聊天室.',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
            except OSError as e:
                print(f'主线程发生异常：{e}')
                break  # 如果发生异常，退出循环
        # 关闭socket对象
        self.server_socket.close()
    # 文本框内容
    def show_info_and_sendto_client(self,data_source,data,data_time):
        send_data = f'{data_source} ({data_time}):\n  {data}'
        self.show_text.AppendText('-'*40+'\n'+send_data+'\n')
        # 内容转发给每个用户
        for client in self.session_thread_dict.values():
            if client.isOn:
                client.client_socket.send(send_data.encode('utf-8'))



# 服务器会话线程的类
class SessionThread(threading.Thread):
    def __init__(self,client_socket,user_name,server):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.user_name = user_name
        self.server = server
        self.isOn = True

    def run(self) -> None:
        print(f'客户端【{self.user_name}】成功连接到服务器')
        while self.isOn:
            try:
                # 接收客户端数据
                data = self.client_socket.recv(1024).decode('utf-8')
                if data == 'disconnect':
                    self.isOn = False
                    self.server.show_info_and_sendto_client('服务器通知', f'{self.user_name}离开了聊天室.',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                else:
                    self.server.show_info_and_sendto_client(self.user_name, data,time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
            except ConnectionAbortedError:
                print(f'客户端【{self.user_name}】的连接被中断')
                self.isOn = False
            except Exception as e:
                print(f'会话线程【{self.user_name}】发生异常：{e}')
                self.isOn = False
        self.client_socket.close()



if __name__ == '__main__':
    app = wx.App()
    server = myServer()
    server.Show()

    app.MainLoop()

