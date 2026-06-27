1：下载release中的zip
https://github.com/stascorp/rdpwrap

2：关闭Windows安全中心关于实时保护和应用控制等

3：右键管理员运行install.bat

4：双击运行RDPConf.exe

5：如果Listener State报错，则更新这个文件到`C:\Program Files\RDP Wrapper`
可能会遇到文件占用，需要打开`服务`然后停止`Remote Desktop Services`
https://github.com/sebaxakerhtc/rdpwrap.ini/blob/master/rdpwrap.ini

6：双击运行RDPConf.exe确认状态全绿

7：tailscale速度慢，用tailscale status看到类似`relay "nue"`的关键字，表示在使用名为nue的中继服务器，tailscale有提供免费的中继服务器，都在国外
可以考虑部署自建的 DERP 节点，需要一个云服务器，建议需要5Mbps以上的宽带
