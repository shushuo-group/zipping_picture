# zipping_picture
本项目是基于**fastapi**完成的——
**上传、压缩图片的服务器**

必要的库由下命令安装：
```shell
pip install -r requirements.txt
```

## 测试环境搭建
以下是建立在已完成测试环境数据库搭建的前提

图片服务很简单 仅需执行俩个步骤即可

    搭建流程：
        1. 分别输入所需的
            debug_nozip_dir
            debug_zip_dir
            这俩个路径(必须为本地网站目录下对应的文件夹目录)

            tips:
                1.路径不允许出现中文字符
                2.使用绝对路径

        2. 解开俩段注释代码
            1. # nozip_dir = debug_nozip_dir
            2. # zip_dir = debug_zip_dir

    提交流程：
        1. 恢复
            debug_nozip_dir = "必须为网站目录下对应的文件夹目录"
            debug_zip_dir = "必须为网站目录下对应的文件夹目录"

        2. 加上俩段注释
            1. # nozip_dir = debug_nozip_dir
            2. # zip_dir = debug_zip_dir

网站主体服务：

    搭建流程：
        1. 邮件主动发送功能的关闭
        2. 缓存的关闭
        3. bin/www 文件内的端口由 6666 ---> 8080
        4. 图片上传模块的url需要进行替换
        https://image.shushuo.space/uploadfile/ ---> http://localhost:6788/uploadfile/

    提交流程：
        1. http://localhost:6788/uploadfile/ ---> https://image.shushuo.space/uploadfile/
        2. public || views || routes 进行迁移 (因为主要编码部分再次 其他情况具体执行)
        3. 注意静态资源缓存机制的执行