import setuptools
 
long_desc = \
'''
# clc99

> 三年后，我再次更新了它。。。。

## 介绍

这是一个用于命令行美化的python库，他可以实现像`Metasploit`一样的命令行显示。为了文档的简洁性，请阅读[帮助文档](https://github.com/windows99-hue/clc99/blob/master/help-chinese.md)

# 安装

在命令行下执行

~~~bash
pip install clc99
~~~

这将会为您安装 `clc99`

## 使用

详情请见[帮助文档](https://github.com/windows99-hue/clc99/blob/master/help-chinese.md)

## 在最后

我在GitHub上开源了它。我希望您能维护和改进我的代码，感激不尽。

这次更新，也算是完成了我小时候的一个愿望，而我将会带着这份礼物，继续向前。。。。。

'''

setuptools.setup(
    name="clc99", # 包的分发名称。只要包含字母，数字_和，就可以是任何名称-。它也不能在pypi.org上使用。请务必使用您的用户名更新此内容，因为这可确保您在上传程序包时不会遇到任何名称冲突
    version="2.2", # 包版本
    author="99", # 用于识别包的作者，下同，可以填写你的信息或者随便填一个
    author_email="3013907412@qq.com",
    description="This is a module to make your 'print' function looks like Metasploit.", # 一个简短的包的总结
    long_description=long_desc, # 包的详细说明，可以加载前面说的README.md作为长描述，也可以直接输入你的包名称或者任何你想详细说明的内容
    url="https://github.com/windows99-hue/clc99",
    packages=setuptools.find_packages(), # 应包含在分发包中的所有Python 导入包的列表。我们可以使用 自动发现所有包和子包，而不是手动列出每个包。在这种情况下，包列表将是example_pkg，因为它是唯一存在的包。find_packages()classifiers告诉索引并点一些关于你的包的其他元数据
    install_requires = ['colorama'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6"
)