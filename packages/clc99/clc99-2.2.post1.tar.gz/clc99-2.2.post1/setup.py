import setuptools
 
long_desc = \
'''
<img width="1314" height="336" alt="LOGO" src="https://github.com/user-attachments/assets/757b4ef1-3cd2-47aa-b1e3-cc99692027db" />

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
    name="clc99",
    version="2.2.post1",
    author="99",
    author_email="3013907412@qq.com",
    description="This is a module to make your 'print' function looks like Metasploit.",
    long_description=long_desc,
    url="https://github.com/windows99-hue/clc99",
    
    # 关键修改：告诉 setuptools 包在 src 目录下
    packages=setuptools.find_packages(where='src'),
    package_dir={'': 'src'},  # 告诉 setuptools 包目录在 src 下
    long_description_content_type="text/markdown",
    install_requires=['colorama'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6"
)