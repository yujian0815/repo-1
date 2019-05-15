import pystache  # Used for templating of HTML files
import json  # Used to parse various JSON files
import datetime  # For getting the compile date
import os  # For file path correction
import mistune  # Markdown parser
import random  # If no packages are featured, feature a random one.
from subprocess import check_output  # Get upstream URL for API
from util.PackageLister import PackageLister


class DepictionGenerator:
    """
   描述生成器处理描述的呈现和生成.

    """

    def __init__(self, version):
        super(DepictionGenerator, self).__init__()
        self.version = version
        self.root = os.path.dirname(os.path.abspath(__file__)) + "/../"
        self.PackageLister = PackageLister(self.version)

    def RenderPackageHTML(self, tweak_data):
        """
        网页转tweak.mustache的描述等于.
        """
        with open(self.root + "Styles/tweak.mustache", "r") as content_file:
            index = content_file.read()
            replacements = DepictionGenerator.RenderDataHTML(self)
            replacements['tweak_name'] = tweak_data['name']
            replacements['tweak_developer'] = tweak_data['developer']['name']
            replacements['tweak_compatibility'] = "iOS " + tweak_data['works_min'] + " 至 " + tweak_data['works_max']
            replacements['tweak_version'] = tweak_data['version']
            replacements['tweak_section'] = tweak_data['section']
            replacements['tweak_bundle_id'] = tweak_data['bundle_id']
            replacements['works_min'] = tweak_data['works_min']
            replacements['works_max'] = tweak_data['works_max']
            replacements['tweak_dataSupport'] = tweak_data['Support']
            replacements['tweak_datasize'] = tweak_data['Installed-Size']
            replacements['tweak_datetime'] = datetime.datetime.now().strftime("%Y年%m月%d日%H:%M")
            replacements['tweak_carousel'] = DepictionGenerator.ScreenshotCarousel(self, tweak_data)
            replacements['tweak_changelog'] = DepictionGenerator.RenderChangelogHTML(self, tweak_data)
            replacements['tweak_tagline'] = tweak_data['tagline']
            replacements['footer'] = DepictionGenerator.RenderFooter(self)
            try:
                if tweak_data['source'] != "":
                    replacements['source'] = tweak_data['source']
            except Exception:
                pass

            try:
                replacements['tint_color'] = tweak_data['tint']
            except Exception:
                try:
                    repo_settings = PackageLister.GetRepoSettings(self)
                    replacements['tint_color'] = repo_settings['tint']
                except Exception:
                    replacements['tint_color'] = "#2cb1be"

            try:
                with open(self.root + "docs/assets/" + tweak_data['bundle_id'] + "/description.md", "r") as md_file:
                    raw_md = md_file.read()
                    desc_md = mistune.markdown(raw_md)
                    replacements['tweak_description'] = desc_md
            except Exception:
                replacements['tweak_description'] = tweak_data['tagline']

            # tweak_carousel

            return pystache.render(index, replacements)

    def RenderPackageNative(self, tweak_data):
        """
        Renders a package's depiction using Sileo's "native depiction" format.

        Object tweak_data: A single index of a "tweak release" object.
        """
        repo_settings = PackageLister.GetRepoSettings(self)
        try:
            tint = tweak_data['tint']
        except Exception:
            try:
                tint = repo_settings['tint']
            except Exception:
                tint = "#2cb1be"

        try:
            with open(self.root + "docs/assets/" + tweak_data['bundle_id'] + "/description.md", "r") as md_file:
                md_txt = md_file.read()
        except Exception:
            md_txt = tweak_data['tagline']

        date = datetime.datetime.now().strftime("%Y-%m-%d")

        screenshot_obj = []
        image_list = self.PackageLister.GetScreenshots(tweak_data)
        subfolder = PackageLister.FullPathCname(self, repo_settings)
        if len(image_list) > 0:
            for image in image_list:
                screenshot_entry = {
                    "url": "https://" + repo_settings['cname'] + subfolder + "/assets/" + tweak_data['bundle_id'] + "/screenshot/"
                           + image,
                    "accessibilityText": "Screenshot"
                }
                screenshot_obj.append(screenshot_entry)
            # The following code is evil, but is actually easier to maintain. My humblest apologies.
            screenshot_view_title = "DepictionHeaderView"
            screenshot_view_carousel = "DepictionScreenshotsView"
        else:
            # The following code is evil, but is actually easier to maintain. My humblest apologies.
            screenshot_view_title = "HiddenDepictionHeaderView"
            screenshot_view_carousel = "HiddenDepictionScreenshotsView"

        changelog = DepictionGenerator.RenderNativeChangelog(self, tweak_data)
        screenshot_size = PackageLister.GetScreenshotSize(self, tweak_data)

        depiction = {
            "minVersion": "0.1",
            "headerImage": "https://" + repo_settings['cname'] + subfolder + "/assets/" + tweak_data['bundle_id'] + "/banner.png",
            "tintColor": tint,
            "tabs": [
                {
                     "tabname": "插件描述",
                     "views": [
                               {
                               "markdown":"\n插件说明:\n \n " ,
                               "useSpacing": "true",
                               "class": "DepictionMarkdownView"
                               },
                               {
                               "markdown":"<center>" + "A12插件兼容说明移步底下\n \n \n  " + "  \n  \n  " + md_txt + "</center>",
                               "useSpacing": "true",
                               "class": "DepictionMarkdownView"
                               },
                               {
                               "markdown":"\n \n \n \n \n-插件截图",
                               "useSpacing": "true",
                               "class": "DepictionMarkdownView"
                               },
                        {
                            "class": screenshot_view_carousel,
                            "screenshots": screenshot_obj,
                            "itemCornerRadius": 8,
                            "itemSize": screenshot_size
                        },
                        {
                            "class": "DepictionSpacerView"
                        },
                        {
                              "class": "DepictionHeaderView",
                              "title": "更新日志",
                               "font-size": "12pt"
                        },
                        {
                              "class": "DepictionMarkdownView",
                              "markdown": "没有更改日志.",
                        },
                        {
                            "class": "DepictionHeaderView",
                            "title": "版本描述",
                            "font-size": "20pt",
                        },
                        {
                            "class": "DepictionTableTextView",
                            "title": "开发人员",
                            "text": tweak_data['developer']['name']
                        },
                        {
                            "class": "DepictionTableTextView",
                            "title": "插件版本",
                            "text": tweak_data['version']
                        },
                        {
                        "class": "DepictionTableTextView",
                        "title": "支持A12?",
                        "text": tweak_data['Support']
                        },
                        {
                        "class": "DepictionTableTextView",
                        "title": "插件大小",
                        "text": tweak_data['Installed-Size'] + " KB "
                        },
                        {
                            "class": "DepictionTableTextView",
                            "title": "支持系统",
                            "text": "iOS " + tweak_data['works_min'] + " 至 " + tweak_data['works_max']
                        },
                        {
                              "class": "DepictionTableTextView",
                              "title": "更新时间",
                              "text": datetime.datetime.now().strftime("%Y年%m月%d日%H:%M"),
                        },
                        {
                            "class": "DepictionSpacerView"
                        },
                        {
                              "class": "DepictionTableButtonView",
                              "title": "更多帮助",
                              "action": "depiction-https://sileo-cydia.github.io/docs/depiction/native/help.json",
                              "openExternal": "true",
                              "tintColor": tint
                        },
                        {
                              "class": "DepictionTableButtonView",
                              "title": "捐赠支持「谢谢大家了」",
                               "action": "depiction-https://sileo-cydia.github.io/docs/depiction/native/juanzeng.json",
                              "openExternal": "true",
                              "tintColor": tint
                        },
                        {
                            "class": "DepictionTableButtonView",
                            "title": "加入的我QQ群(付费8.8)",
                            "action": "https://qm.qq.com/cgi-bin/qm/qr?k=3E6NIMRxJuoAGun5DH6XLWoQ8cm5T4TW/",
                            "openExternal": "true",
                            "tintColor": tint
                        },
                        {
                            "class": "DepictionLabelView",
                            "text": DepictionGenerator.RenderFooter(self),
                            "textColor": "#999999",
                            "fontSize": "10.0",
                            "alignment": 1
                        }
                    ],
                    "class": "DepictionStackView"
                },
                {
                    "tabname": "关于我们",
                    "views": changelog,
                    "class": "DepictionStackView"
                },
            ],
            "class": "DepictionTabView"
        }

        blank = {
                    "class": "DepictionSpacerView"
                }

        try:
            if tweak_data['source'] != "":
                source_btn = {
                                "class": "DepictionTableButtonView",
                                "title": "View Source Code",
                                "action": tweak_data['source'],
                                "openExternal": "true",
                                "tintColor": tint
                            }
                depiction['tabs'][0]['views'].insert(8, source_btn)
                depiction['tabs'][0]['views'].insert(8, blank)
                pass
        except Exception:
            pass

        return json.dumps(depiction)

    def RenderNativeChangelog(self, tweak_data):
        """
            生成用于本机描述的变更日志。
            对象调整数据：“调整发布”对象的单个索引。
        """
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        try:
            changelog = []
            for version in tweak_data['changelog'][::-1]:
                ver_entry = {
                    "class": "DepictionMarkdownView",
                    "markdown": "#### Version {0}\n\n{1}".format(version['version'], version['changes']),
                }
                changelog.append(ver_entry)
            changelog.append({
                            "class": "DepictionLabelView",
                            "text": DepictionGenerator.RenderFooter(self),
                            "textColor": "#999999",
                            "fontSize": "10.0",
                            "alignment": 1
            })
            return changelog
        except Exception:
            return [
                    
                    {
                    "class":"DepictionMarkdownView",
                    "markdown" :".\n- 立志做一个专业的源.\n- 为广大基友服务.\n- 开发不易求打赏.\n- 更新就不会失去动力.\n- 越狱中遇到小问题.\n- 如插件更新存在问题\n- 安装使用上的问题\n- 版本兼容的问题\n- 欢迎反馈\n- 安装插件前请详细阅读安装说明\n- 分清楚汉化包,跟汉化插件\n- 仔细观看兼容系统\n- 不要乱安装不兼容的插件\n- 如碰到问题\n- 点击下方加入我的QQ群\n- 专业为你解决所有越狱问题 ",
                    "fontSize": "15.0",
                    },
                {   
                    "class": "DepictionLabelView",
                    "text": DepictionGenerator.RenderFooter(self),
                    "textColor": "#999999",
                    "fontSize": "10.0",
                    "alignment": 1
                },
                {
                "class": "DepictionTableButtonView",
                "title": "越狱教程(后续更新中)",
                    "action": "depiction-https://sileo-cydia.github.io/docs/depiction/native/yueyujiaocheng.json",
                "openExternal": "true",
                
                },
                {
                "class": "DepictionTableButtonView",
                "title": "破解软件(后续更新中)",
                "action": "depiction-https://sileo-cydia.github.io/docs/depiction/native/pojieruanjian.json",
                "openExternal": "true",
                
                },
                {
                "class": "DepictionTableButtonView",
                "title": "越狱软件(企业版越狱下载)",
                "action": "depiction-https://sileo-cydia.github.io/docs/depiction/native/yueyuruanjian.json",
                "openExternal": "true",
                
                },
                {
                "class": "DepictionTableButtonView",
                "title": "加入的我QQ群(付费8.8)",
                "action": "https://qm.qq.com/cgi-bin/qm/qr?k=3E6NIMRxJuoAGun5DH6XLWoQ8cm5T4TW/",
                "openExternal": "true",
                
                },
            ]

    def ChangelogEntry(self, version, raw_md):
        """
        Generates a div for changelog entries.

        String version: The version number.
        String raw_md: The changelog entry text (Markdown-compatible).
        """
        return '''<div class="changelog_entry">
                <h4>{0}</h4>
                <div class="md_view">{1}</div>
            </div>'''.format(version, mistune.markdown(raw_md))

    def RenderChangelogHTML(self, tweak_data):
        """
            生成一个changelog条目的DIV。
            对象调整数据：“调整发布”对象的单个索引.
        """
        element = ""
        try:
            for version in tweak_data['changelog'][::-1]:
                element += DepictionGenerator.ChangelogEntry(self, version['version'], version['changes'])
            return element
        except Exception:
            return "<center><small style='color:#FF0000;font-size:17px;'>立志做一个专业的源.</small><br /><small style='color:#00FF00;font-size:17px;'> 为广大基友服务.</script><br /><small style='color:#0000FF;font-size:17px'>开发不易求打赏.</script><br /><small style='color:#FF00FF;font-size:17px;'>更新就不会失去动力.</script><br /><small style='color:#00FF00;font-size:17px;'>越狱中遇到小问题.</script><br /><small style='color:#FF00FF;font-size:17px;'> 如插件更新存在问题</script><br /><small style='color:#0000FF;font-size:17px;'> 安装使用上的问题</script><br /><small style='color:#FF0000;font-size:17px;'> 版本兼容的问题</script><br /><small style='color:#00FF00;font-size:17px;'>欢迎反馈</small><br /><small style='color:#0000FF;font-size:17px;'>安装插件前请详细阅读安装说明</script><br /><small style='color:#FF0033;font-size:17px;'> 分清楚汉化包,跟汉化插件<br /><small style='color:#FF0000;font-size:19px;'> 仔细观看兼容系统</script><br /><small style='color:#005080;font-size:17px;'> 不要乱安装不兼容的插件</script><br /><small style='color:#FF0000;font-size:17px;'> 如碰到问题</script><br /><small style='color:#FF00FF;font-size:17px;'>点击下方添加qq群联系到我</script><br /><small style='color:#FFBB00;font-size:17px;'> 专业为你解决所有越狱问题</script><br /></a></center>"

    def RenderIndexHTML(self):
        """
        Renders the home page (index.html).
        """
        repo_settings = PackageLister.GetRepoSettings(self)
        with open(self.root + "Styles/index.mustache", "r") as content_file:
            index = content_file.read()
            replacements = DepictionGenerator.RenderDataHTML(self)
            replacements['tint_color'] = repo_settings['tint']
            replacements['footer'] = DepictionGenerator.RenderFooter(self)
            replacements['tweak_release'] = PackageLister.GetTweakRelease(self)
            return pystache.render(index, replacements)

    def RenderFooter(self):
        """
        Renders the footer.
        """
        repo_settings = PackageLister.GetRepoSettings(self)
        data = DepictionGenerator.RenderDataHTML(self)
        try:
            footer = pystache.render(repo_settings['footer'], data)
        except Exception:
            footer = pystache.render("他是个疯子 {{silica_version}}", data)
        return footer

    def RenderDataBasic(self):
        """
        获取要传递给pystache的基本repo数据的值.
        """
        repo_settings = PackageLister.GetRepoSettings(self)
        with open(self.root + "Styles/settings.json", "r") as content_file:
            data = json.load(content_file)
            date = datetime.datetime.now().strftime("%Y年%m月%d日%H时%M分")
            subfolder = PackageLister.FullPathCname(self, repo_settings)
            return {
                "silica_version": self.version,
                "silica_compile_date": date,
                "repo_name": data['name'],
                "repo_url": data['dname'] + subfolder,
                "repo_desc": data['description'],
                "repo_tint": data['tint']
            }

    def RenderDataHTML(self):
        data = DepictionGenerator.RenderDataBasic(self)

        tweak_release = PackageLister.GetTweakRelease(self)

        data['repo_packages'] = DepictionGenerator.PackageEntryList(self, tweak_release)

        data['repo_carousel'] = DepictionGenerator.CarouselEntryList(self, tweak_release)

        return data

    def PackageEntry(self, name, author, icon, bundle_id):
        """
        Generates a package entry div.

        String name: The package's name
        String author: The author's name
        String (URL) icon: A URL to an image of the package icon.

        Scope: HTML > Generation > Helpers
        """

        if (bundle_id != "silica_do_not_hyperlink"):
            return '''<a class="subtle_link" href="depiction/web/{3}.html"><div class="package">
            <img src="{0}">
            <div class="package_info">
                <p class="package_name">{1}</p>
                <p class="package_caption">{2}</p>
            </div>
        </div></a>'''.format(icon, name, author, bundle_id)
        else:
            return '''<div class="package">
                <img src="{0}">
                <div class="package_info">
                    <p class="package_name">{1}</p>
                    <p class="package_caption">{2}</p>
                </div>
            </div>'''.format(icon, name, author)

    def ScreenshotCarousel(self, tweak_data):
        """
        Generates a screenshot div.

        Object tweak_data: A single index of a "tweak release" object.
        """
        repo_settings = PackageLister.GetRepoSettings(self)
        screenshot_div = "<div class=\"scroll_view\">"
        image_list = self.PackageLister.GetScreenshots(tweak_data)
        if (len(image_list) > 0):
            for image in image_list:
                screenshot_div += '''<img class="img_card" src="../../assets/{1}/screenshot/{2}">'''.format(
                    repo_settings['cname'], tweak_data['bundle_id'], image)
            screenshot_div += "</div>"
        else:
            screenshot_div = ""
        return screenshot_div

    def CarouselEntry(self, name, banner, bundle_id):
        """
        Generates a card to be used in Featured carousels.

        String name: The package's name
        String (URL) banner: A URL to an image of the package banner.
        """
        if len(name) > 18:
            name = name[:18] + "…"
        return '''<a href="depiction/web/{0}.html" style="background-image: url({1})" class="card">
                <p>{2}</p>
            </a>'''.format(bundle_id, banner, name)

    def NativeFeaturedCarousel(self, tweak_release):
        """
        Generate a sileo-featured.json file for featured packages.

        Object carousel_entry_list: A "tweak release" object.
        """
        repo_settings = PackageLister.GetRepoSettings(self)
        subfolder = PackageLister.FullPathCname(self, repo_settings)
        banners = []
        for package in tweak_release:
            try:
                if package['featured'].lower() == "true":
                    ar_el = {
                        "package": package['bundle_id'],
                        "title": package['name'],
                        "url": "https://" + repo_settings['cname'] + subfolder + "/assets/" + package['bundle_id'] + "/banner.png",
                        "hideShadow": "true"

                    }
                    banners.append(ar_el)
            except Exception:
                pass
        if len(banners) == 0:
            featured_int = random.randint(0,(len(tweak_release)-1))
            featured_package = tweak_release[featured_int]
            ar_el = {
                "package": featured_package['bundle_id'],
                "title": featured_package['name'],
                "url": "https://" + repo_settings['cname'] + subfolder + "/assets/" + featured_package['bundle_id'] + "/banner.png",
                "hideShadow": "true"

            }
            banners.append(ar_el)

        featured_json = {
            "class": "FeaturedBannersView",
            "itemSize": "{263, 148}",
            "itemCornerRadius": 8,
            "banners": banners
        }
        return json.dumps(featured_json)

    def PackageEntryList(self, tweak_release):
        """
        Generate a user-friendly list of packages on the repo.

        Object tweak_release: A "tweak release" object.
        """
        list_el = ""
        for package in tweak_release:
            list_el += DepictionGenerator.PackageEntry(self, package['name'], package['developer']['name'],
                                                       "assets/" + package['bundle_id'] + "/icon.png",
                                                       package['bundle_id'])
        return list_el

    def CarouselEntryList(self, tweak_release):
        """
        Generate a carousel of featured packages on the repo.

        Object tweak_release: A "tweak release" object.
        """
        list_el = ""
        for package in tweak_release:
            try:
                if package['featured'].lower() == "true":
                    list_el += DepictionGenerator.CarouselEntry(self, package['name'],
                                                                "assets/" + package['bundle_id'] + "/.png",
                                                                package['bundle_id'])
            except Exception:
                pass
        if list_el == "":
            featured_int = random.randint(0,(len(tweak_release)-1))
            featured_package = tweak_release[featured_int]
            list_el += DepictionGenerator.CarouselEntry(self, featured_package['name'],
                                                        "assets/" + featured_package['bundle_id'] + "/banner.png",
                                                        featured_package['bundle_id'])
        return list_el

    def SilicaAbout(self):
        """
        Returns a JSON object that describes information about the Silica install.
        """

        compile_date = datetime.datetime.now().isoformat()
        try:
            upstream_url = check_output(["git", "config", "--get", "remote.origin.url"], cwd=self.root).decode("utf-8")
        except Exception:
            upstream_url = "undefined"
        return {
            "software": "Silica",
            "version": self.version,
            "compile_date": compile_date,
            "upstream_url": upstream_url
        }

    def RenderNativeHelp(self, tweak_data):
        """
        Generates a help view for Sileo users.

        Object tweak_data: A single index of a "tweak release" object.
        """

        repo_settings = PackageLister.GetRepoSettings(self)

        try:
            tint = tweak_data['tint']
        except Exception:
            try:
                tint = repo_settings['tint']
            except Exception:
                tint = "#2cb1be"

        view = []
        try:
            if tweak_data['developer']['email']:
                view.append(
                    {
                        "class": "DepictionMarkdownView",
                        "markdown": "如果你需要帮助 \"" + tweak_data['name'] + "\", 你可以联系 "
                                    + tweak_data['developer']['name'] + ", 开发者的邮箱."
                    }
                )
                view.append(
                    {
                        "class": "DepictionTableButtonView",
                        "title": "Email Developer",
                        "action": "mailto:" + tweak_data['developer']['email'],
                        "openExternal": "true",
                        "tintColor": tint
                    }
                )
        except Exception:
            try:
                view.append(
                    {
                        "class": "DepictionMarkdownView",
                        "markdown": "如果你需要帮助 \"" + tweak_data['name'] + "\", 你可以联系 "
                                    + tweak_data['developer']['name']
                                    + ", 谁是开发商。很遗憾，我们不知道他们的电子邮件."
                    }
                )
            except Exception:
                view.append(
                    {
                        "class": "DepictionMarkdownView",
                        "markdown": "包的开发人员 \"" + tweak_data['name']
                                    + "\" 尚不清楚。尝试联系回购维护人员以获取更多信息."
                    }
                )

        try:
            if tweak_data['social']:
                view.append(
                    {
                        "class": "DepictionMarkdownView",
                        "markdown": "您也可以联系 " + tweak_data['developer']['name'] + " 使用以下内容" +
                        " sites:"
                    }
                )
                for entry in tweak_data['social']:
                    view.append({
                        "class": "DepictionTableButtonView",
                        "title": entry['name'],
                        "action": entry['url'],
                        "openExternal": "true",
                        "tintColor": tint
                    })
        except Exception:
            pass

        view.append(
            {
                "class": "DepictionMarkdownView",
                "markdown": "如果您在描述中发现错误或无法下载包，您可以发邮件联系"
                    + "源的管理人员 \"" + repo_settings['name'] + "\" 源\n- By:, "
                            + repo_settings['maintainer']['name'] + "."
            }
        )
        view.append(
            {
                "class": "DepictionTableButtonView",
                "title": "点击发送邮件给他",
                "action": "mailto:" + repo_settings['maintainer']['email'],
                "openExternal": "true",
                "tintColor": tint
            }
        )

        try:
            if repo_settings['social']:
                view.append(
                    {
                        "class": "DepictionMarkdownView",
                        "markdown": "您还可以通过以下方式联系回购维护人员" +
                        " sites:"
                    }
                )
                for entry in repo_settings['social']:
                    view.append({
                        "class": "DepictionTableButtonView",
                        "title": entry['name'],
                        "action": entry['url'],
                        "openExternal": "true",
                        "tintColor": tint
                    })
        except Exception:
            pass

        return json.dumps({
            "class": "DepictionStackView",
            "tintColor": tint,
            "title": "Contact Support",
            "views": view
        })
