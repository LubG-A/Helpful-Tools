一个用于在局域网共享文件和剪切板的服务器脚本，具有文件的上传、下载功能和一个临时的剪切板。如果你不想配置FTP等文件服务器或者一些第三方软件，可以用这个脚本来实现通过网络的文件共享。

相信会看我这种小仓库的诸位都不需要说明，但是还是简要解释一下如何使用：

⚠️配置好python，如果你不会配置python，请一定上网查看资料。此外，，Linux系统下还要安装pip包管理器，Windows下则要配置好环境路径⚠

安装python包flask，一般是运行如下命令

- Linux系统
```sh
pip3 install flask
```
- Windows系统
```sh
pip install flask
```

然后使用python运行该脚本即可，一般运行如下命令：

- Linux系统
```sh
python3 ShareServer.py
```
- Windows系统
```sh
python ShareServer.py
```


使用Windows的各位也可以双击bat快速启动🙂
