#!/bin/bash
echo "二氧化硅配置实用程序"
echo ""
if [ ! -f .is_setup ]; then
    echo "我们会问你几个问题，为你准备一些基础知识!"
    echo "有关依赖项的完整列表以及如何安装它们，请阅读自述文件。"

    echo "给我们一点时间来安装python依赖项."
    pip3 install -r requirements.txt
    echo "已安装所有必需的软件包！现在，就几个关于你的问题."
    echo ""
    printf "你的回购应该叫什么？? "
    read silica_repo_name
    printf "你能简单描述一下你的回购协议是关于什么的吗? "
    read silica_repo_description
    printf "您要在哪个域上承载repo（不包括https://，只包括域）? "
    read silica_repo_cname
    printf "你叫什么名字？ "
    read silica_repo_maintainer_name
    printf "你的电子邮件是什么? "
    read silica_repo_maintainer_email
    printf "使用Sileo，您可以自定义回购的色调。你能提供一个十六进制代码吗? "
    read silica_repo_tint
    printf "运行时是否希望Silica自动将repo推送到Git服务器？（真/假） (true/false) "
    read silica_auto_git

    mkdir "Packages"

    printf "{
    \"name\": \"$silica_repo_name\",
    \"description\": \"$silica_repo_description\",
    \"tint\": \"$silica_repo_tint\",
    \"cname\": \"$silica_repo_cname\",
    \"maintainer\": {
        \"name\": \"$silica_repo_maintainer_name\",
        \"email\": \"$silica_repo_maintainer_email\"
    },
    \"automatic_git\": \"$silica_auto_git\"
}" > Styles/settings.json

    echo ""
    echo "谢谢您！现在让我们为您生成一些GPG密钥。把这些放在安全的地方，否则你可能再也无法编辑回购协议了。!"
    echo "   熵注意：请同时做一些事情，像垃圾邮件一些钥匙或晃动你的鼠标。我们需要熵!"
    gpg --batch --gen-key util/gpg.batchgen
    echo "已将密钥导出到GPG密钥环中。此计算机是唯一可用于二氧化硅的计算机（在默认设置下）."

    echo ""
    echo "记住：对于github页面，您必须进入github.com上的存储库设置并为/docs启用github页面。."
    echo "已成功配置二氧化硅!"    
    echo ""
    echo "要将包添加到回购中，请查看包中的预捆绑文件/或使用UI从DEB管理/创建它们。."
    touch .is_setup
else
    echo "二氧化硅已经形成。如果您正在移动机器，请删除。是否已设置并确保GPG钥匙圈已结转。流产…"
fi