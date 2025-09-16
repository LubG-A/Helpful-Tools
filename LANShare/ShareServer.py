from flask import Flask, request, send_from_directory, render_template_string, redirect, url_for
import os
import socket
import logging
import datetime
from threading import Lock
from flask import send_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024  # 限制上传大小为1GB

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

clipboard_content = ""
clipboard_lock = Lock()

# HTML
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>资源服务器</title>
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #333; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 10px 0; padding: 10px; background-color: #f5f5f5; border-radius: 5px; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
        form { margin: 20px 0; padding: 15px; background-color: #f9f9f9; border-radius: 5px; }
        input[type=submit] { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
        input[type=submit]:hover { background-color: #45a049; }
        textarea { width: 100%; height: 120px; font-size: 16px; }
    </style>
</head>
<body>
    <h1>资源服务器</h1>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <h2>上传文件</h2>
        <input type="file" name="file" required>
        <input type="submit" value="上传">
    </form>
    <h2>下载文件</h2>
    <ul>
        {% for file in files %}
            <li>
                <a href="/download/{{ file }}">{{ file }}</a>
                <a href="/delete/{{ file }}" style="color: red; margin-left: 10px;">删除</a>
            </li>
        {% endfor %}
    </ul>
    <form method="post">
        <h2>共享剪切板</h2>
        <textarea name="clipboard_content" required>{{ clipboard_content }}</textarea><br>
        <input type="submit" value="保存剪切板">
        <button type="submit" name="save_clipboard" value="1">保存为文件</button>
    </form>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    global clipboard_content
    if request.method == 'POST':
        # 剪切板表单
        if 'clipboard_content' in request.form:
            new_content = request.form.get('clipboard_content', '')
            with clipboard_lock:
                clipboard_content = new_content
            logger.info("剪切板内容已更新")
            # 检查是否点击了“保存为文件”按钮
            if 'save_clipboard' in request.form:
                now = datetime.datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
                filename = f"clipboard_save_{now}.txt"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(clipboard_content)
                logger.info(f"剪切板内容已保存为文件: {filename}")
        # 文件上传表单
        elif 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filename)
                logger.info(f"文件已上传: {file.filename}")
        return redirect(url_for('index'))
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    with clipboard_lock:
        content = clipboard_content
    return render_template_string(HTML, files=files, clipboard_content=content)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        logger.info(f"文件已上传: {file.filename}")
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    logger.info(f"下载文件: {filename}")
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"文件已删除: {filename}")
    return redirect(url_for('index'))

def get_local_ip():
    try:
        # 创建一个临时套接字连接到外部地址，获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

@app.route('/favicon.ico')
def favicon():
    return send_file('favicon.ico', mimetype='image/x-icon')

if __name__ == '__main__':
    host = get_local_ip()
    port = 5000
    
    print(f"文件服务器已启动!")
    print(f"请访问: http://{host}:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=True)