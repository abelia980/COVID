class paperScrapy:
    # please change the dir as the directory of ChromeDriver
    # using the VPN of CUFE to access the Web of Science
    def arxiv(start='2020-01-01', end='2020-08-20'):
        import requests
        from bs4 import BeautifulSoup
        from pandas.core.frame import DataFrame
        import pandas as pd
        import urllib
        from pdfminer.pdfparser import PDFParser, PDFDocument
        from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
        from pdfminer.converter import PDFPageAggregator
        from pdfminer.layout import LTTextBoxHorizontal, LAParams
        from pdfminer.pdfinterp import PDFTextExtractionNotAllowed

        page = requests.get(
            'https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND&terms-0-term=COVID-19&terms-0-field=title&terms-1-operator=OR&terms-1-term=SARS-CoV-2&terms-1-field=abstract&terms-3-operator=OR&terms-3-term=COVID-19&terms-3-field=abstract&terms-4-operator=OR&terms-4-term=SARS-CoV-2&terms-4-field=title&terms-5-operator=OR&terms-5-term=coronavirus&terms-5-field=title&terms-6-operator=OR&terms-6-term=coronavirus&terms-6-field=abstract&classification-physics_archives=all&classification-include_cross_list=include&date-filter_by=all_dates&date-year=&date-from_date=&date-to_date=&date-date_type=submitted_date&abstracts=show&size=200&order=-announced_date_first&source=home-covid-19&start=0')
        soup = BeautifulSoup(page.content, "html.parser")  # 解析网页
        # 获取所有链接
        url = soup.find_all("ul", class_="pagination-list")[0]
        a = url.find_all('a')[4:]  # 链接标签
        href = []
        id = []
        category = []
        title = []
        authors = []
        abstract = []
        create = []
        update = []
        author_info = []
        for k in a:
            href = 'https://arxiv.org/' + k['href']
            print(href)
            page = requests.get(href)
            soup = BeautifulSoup(page.content, "html.parser")  # 解析网页
            s_p = soup.find_all("li", class_="arxiv-result")[2:4]
            for i in s_p:

                time = i.find("p", class_="is-size-7")
                time = time.strings
                date = pd.to_datetime("".join(time).strip().split(';')[0][10:])
                # 判断时间是否在起止范围
                if ((str(date) >= start) & (str(date) <= end)):
                    # id
                    j = i.find("p", class_="list-title is-inline-block")
                    aa = j.find_all('a')[0]
                    idd = aa['href'].split('/')[-1]
                    id.append(idd)
                    # print(id)
                    # category
                    cate = i.find("div", class_="tags is-inline-block")
                    cate = cate.strings
                    category.append("".join(cate).strip('').replace('\n', ' ').lstrip().rstrip())
                    # print(category)
                    # title
                    tit = i.find("p", class_="title is-5 mathjax")
                    tit = tit.strings
                    title.append("".join(tit).strip('').replace('\n', '').strip())
                    # print(title)
                    # authors
                    au = i.find("p", class_="authors")
                    au = au.strings
                    authors.append("".join(au).replace('\n', '').replace('  ', '').replace(', ', ',')[9:])
                    # print(authors)
                    # abstract
                    abs = i.find("span", class_="abstract-full has-text-grey-dark mathjax")
                    abs = abs.strings
                    abstract.append("".join(abs).strip().replace('\n        △ Less', ''))
                    # print(abstract)
                    # create
                    create.append(date)
                    # print(create)
                    # update
                    time = i.find("p", class_="is-size-7")
                    time = time.strings
                    update.append("".join(time).split(';')[-1].strip()[21:].replace('.\n      \n    ', ''))
                    # pdf
                    try:
                        pdf_url = 'https://arxiv.org/pdf/' + idd + '.pdf'
                        # print(pdf_url)
                        pdf1 = urllib.request.urlopen(pdf_url)

                        # 创建一个与文档关联的解析器
                        parser = PDFParser(pdf1)
                        # 创建一个PDF文档对象
                        doc = PDFDocument()
                        # 连接两者
                        parser.set_document(doc)
                        doc.set_parser(parser)
                        # 文档初始化
                        doc.initialize('')
                        # 创建PDF资源管理器
                        resources = PDFResourceManager()
                        # 创建参数分析器
                        laparam = LAParams()
                        # 创建一个聚合器，并接收资源管理器，参数分析器作为参数
                        device = PDFPageAggregator(resources, laparams=laparam)
                        # 创建一个页面解释器
                        interpreter = PDFPageInterpreter(resources, device)
                        for page in doc.get_pages():
                            department = ''
                            # 使用页面解释器读取页面
                            interpreter.process_page(page)
                            # 使用聚合器读取页面页面内容
                            layout = device.get_result()
                            for out in layout:
                                if hasattr(out, 'get_text'):  # 因为文档中不只有text文本
                                    if (('Depart' in out.get_text()) | ('Univer' in out.get_text()) | (
                                            'Institute' in out.get_text()) | ('Affiliations' in out.get_text()) | (
                                            'School' in out.get_text()) | ('Dept.' in out.get_text()) | (
                                            'Camp' in out.get_text()) | ('Academy' in out.get_text()) | (
                                            'UNIVERSITY' in out.get_text()) | ('Cambridge' in out.get_text())):
                                        out = out.get_text()
                                        department = department + out
                                        department = department.replace('\t\r', '').replace('\n', ' ')
                            author_info.append(department)
                            # print(department)
                            break
                    except:
                        # print('打不开')
                        department = ''
                        author_info.append(department)
                        continue
        result = {"id": id, "category": category, "title": title, "authors": authors, "abstract": abstract,
                  "Submitted ": create, "originally announced": update, "author_info": author_info}
        df = DataFrame(result)
        return df

    def sci_scrapy(username, password, keywords, starttime=0, endtime=0):
        '''

        :param username: based the VPN of center university finance and economics, the student's username for login the school net
        :param password: the student's password for login the school net
        :param keywords: the keywords you want to search
        :param starttime: the time of start
        :param endtime: the time of end
        :return: the dataframe of results
        '''
        import time
        import pandas as pd
        from selenium import webdriver
        import datetime
        from requests import ReadTimeout

        if (len(keywords) == 0):
            return "The length of keywords is 0"
        if (starttime > endtime) | (starttime < 1980) | (endtime > datetime.datetime.now().year):
            return "The time filter is wrong, the start time>endtime or start time<1980 or endtime> this year "

        ##create the dataframe, and the columns are
        ## "tilte","author","jounary","DOI","public_date","type","abstract","KeyWords","author info","fund","category"
        sciData = pd.DataFrame(
            columns={"title", "author", "jounary", "DOI", "public_date", "type", "abstract", "KeyWords", "author info",
                     "fund",
                     "category"})

        ##login page
        new_driver = webdriver.Chrome()
        url = "http://login.webofknowledge.com/"
        try:
            new_driver.get(url)
            new_driver.find_element_by_id('select2-shibSelect-container').click()

            a = new_driver.find_elements_by_class_name("select2-results__option")  # CHINA CERNET Federation
            a[8].click()
            new_driver.find_element_by_id("shibSubmit").click()
            school = "中央财经大学(Central University of Finance and Economics)"  # 机构名称
            new_driver.find_element_by_id("idpSelectInput").send_keys(school)
            new_driver.find_element_by_id("idpSelectSelectButton").click()
            time.sleep(5)

            new_driver.find_element_by_id("username").send_keys(username)  # 学校账号
            new_driver.find_element_by_id("password").send_keys(password)  # 学校密码
            new_driver.find_element_by_id("submit").click()
            time.sleep(5)
        except:
            print("The network is real poor")
            return 0
        try:
            temp = new_driver.find_element_by_id("username").id
            if (temp):
                return "the username or password is wrong"
        except:
            print("login sucessfully")

        index = 0  # sci's index
        for iteration in keywords:
            time1 = time.time()
            print("this is " + iteration)
            new_driver.find_element_by_id("value(input1)").clear()  ##首先把文本框中的值清理
            new_driver.find_element_by_id("value(input1)").send_keys(iteration)

            ##choose the time
            if index == 0:
                if (starttime | endtime):
                    new_driver.find_element_by_xpath(
                        '//*[@id="timespan"]/div[2]/div/span/span[1]/span/span[2]/b').click()
                    temp = new_driver.find_elements_by_xpath('//*[@role="treeitem"]')
                    temp[len(temp) - 1].click()
                    if (starttime != 0):
                        new_driver.find_element_by_xpath \
                            ('//*[@id="timespan"]/div[3]/div/span[2]/span[1]/span/span[2]/b').click()
                        temp = new_driver.find_elements_by_xpath('//*[@role="treeitem"]')
                        temp[int(starttime) - 1980].click()
                    if (endtime != 0):
                        new_driver.find_element_by_xpath \
                            ('//*[@id="timespan"]/div[3]/div/span[4]/span[1]/span/span[2]/b').click()
                        temp = new_driver.find_elements_by_xpath('//*[@role="treeitem"]')
                        temp[int(endtime) - datetime.datetime.now().year].click()

            new_driver.find_element_by_class_name("searchButton").click()
            time.sleep(5)  ##搜索关键词停顿一下
            flag = 1  # 标记是否是点击第一条记录
            hitCount = new_driver.find_element_by_id("hitCount.top").text
            print("there are " + str(hitCount) + "records")
            count = 0  # record the numbers of results
            while (True):
                try:
                    if flag == 1:
                        new_driver.find_element_by_xpath(
                            '//*[@id = "RECORD_1"]/div[3]/div/div[1]/div/a/value').click()  # 点击第一条记录
                        flag = 0
                    time.sleep(2)
                    a = new_driver.find_element_by_xpath(
                        '// *[ @ id = "records_form"] / div / div / div / div[1] / div / div[1] / value').text
                    sciData.at[index, 'title'] = a
                    try:
                        sciData.at[index, 'author'] = new_driver.find_element_by_xpath \
                            ('//*[@id="records_form"]/div/div/div/div[1]/div/div[2]/p').text
                    except:
                        sciData.at[index, 'author'] = new_driver.find_element_by_xpath("//*[text()='作者:']/..").text
                    try:
                        sciData.at[index, 'jounary'] = new_driver.find_element_by_xpath \
                            ('//*[@id="records_form"]/div/div/div/div[1]/div/div[3]/p[1]/span/value').text
                    except:
                        try:
                            sciData.at[index, 'jounary'] = new_driver.find_element_by_xpath \
                                ('//*[@id="records_form"]/div/div/div/div[1]/div/div[4]/p[2]/value').text
                        except:
                            sciData.at[index, 'jounary'] = new_driver.find_element_by_class_name("sourceTitle").text

                    try:
                        sciData.at[index, 'DOI'] = new_driver.find_element_by_xpath \
                            ('//*[@id="records_form"]/div/div/div/div[1]/div/div[3]/p[2]/value').text
                    except:
                        sciData.at[index, 'DOI'] = ""
                    try:
                        sciData.at[index, 'public_date'] = new_driver.find_element_by_xpath \
                            ("//*[text()='出版年:‏']/..").text
                    except:
                        try:
                            sciData.at[index, 'public_date'] = new_driver.find_element_by_xpath \
                                ('//*[@id="records_form"]/div/div/div/div[1]/div/div[3]/p[3]/value').text
                        except:
                            sciData.at[index, 'public_date'] = new_driver.find_element_by_xpath \
                                ('//*[@id="records_form"]/div/div/div/div[1]/div/div[3]/value').text

                    try:
                        sciData.at[index, 'type'] = new_driver.find_element_by_xpath \
                            ("//*[text()='文献类型:']/..").text
                    except:
                        sciData.at[index, 'type'] = ""
                    try:
                        sciData.at[index, 'abstract'] = new_driver.find_element_by_xpath \
                            ("//*[text()='摘要']/..").text
                    except:
                        sciData.at[index, 'abstract'] = ""
                    try:
                        sciData.at[index, 'KeyWords'] = new_driver.find_element_by_xpath(
                            "//*[text()='作者关键词:']/..").text
                    except:
                        sciData.at[index, 'KeyWords'] = ""
                    author_info_list = new_driver.find_elements_by_class_name("fr_address_row2")
                    author_info_num = len(author_info_list)
                    text = ""
                    for iter in range(author_info_num):
                        text = text + author_info_list[iter].text + '\n'
                    sciData.at[index, 'author info'] = text
                    if (author_info_num == 0):
                        try:
                            sciData.at[index, 'author info'] = new_driver.find_element_by_xpath(
                                "//*[text()='地址:']/..").text
                        except:
                            sciData.at[index, 'author info'] = ""
                    try:
                        sciData.at[index, 'fund'] = new_driver.find_element_by_xpath \
                            ("//*[text()='基金资助机构']/../../tr[2]/td[1]").text
                    except:
                        sciData.at[index, 'fund'] = ""
                    sciData.at[index, 'category'] = new_driver.find_element_by_xpath \
                        ("//*[text()='研究方向:']/..").text
                    # print("this the " + str(index) + "th paper")
                    index += 1
                    count += 1
                except:
                    print("the " + str(count) + "th paper access fail")
                    count += 1
                if (count == hitCount):
                    print("The scrapy of " + iteration + "is over")
                    break
                try:
                    new_driver.find_element_by_xpath('//*[@id="paginationForm"]/span/a[2]/i').click()
                    time.sleep(5)
                except(ConnectionError, ReadTimeout):
                    print("timeout")
                    return sciData

            print("The time of keyWord scrapy is" + str(time.time() - time1))
            new_driver.find_element_by_xpath('//*[@id="skip-to-navigation"]/ul[1]/li[1]/a').click()
            time.sleep(5)
        return sciData

    def biorxiv(start, end, href='https://connect.biorxiv.org/relate/content/181'):
        '''
     |
     |    To grab data from the BioRxiv web site between specified dates.
     |
     |  Parameters
     |  ----------
     |  start: str
     |    The recent date to start crawling data, formed as "yyyy-mm-dd"
     |  end: str
     |    The date to end crawling data, formed as "yyyy-mm-dd"
     |  href: str
     |    The url to start crawling data
     |
     |  Example
     |  --------
     |  >>> href = "https://connect.biorxiv.org/relate/content/181?page=71"
     |  >>> df = biorxiv(start='2020-05-12',end='2020-05-02',href=href)

         '''
        from selenium import webdriver
        import pandas as pd

        try:
            driver = webdriver.Chrome()
            driver.get(href)
            driver.add_cookie({'name': 'foo', 'value': 'bar', 'path': '/', 'secure': True})
            driver.add_cookie({'name': '__cfduid', 'value': 'df25ebfe67044c813ef0e846d6667d6d41568814115', 'path': '/',
                               'secure': True})
            driver.add_cookie(
                {'name': 'SESS1dd6867f1a1b90340f573dcdef3076bc', 'value': 'deleted', 'path': '/', 'secure': True})
            mainhandle = driver.current_window_handle  # 主页面
        except Exception as e:
            print(e)
            driver.quit()

        info = pd.DataFrame()

        try:
            while (True):
                divs0 = driver.find_elements_by_class_name('highwire-cite-metadata-journal')
                divs = driver.find_elements_by_class_name('highwire-cite-title')
                for i in range(10):
                    date = divs0[i].text[-10:]
                    if date <= start and date >= end:
                        total = get_info(driver, divs[2 * i])
                        info = info.append(pd.DataFrame(total, index=[0]))
                        driver.close()
                        driver.switch_to.window(mainhandle)
                    elif date < end:
                        driver.quit()
                        return info
                driver.find_element_by_class_name('pager-next').click()
        except Exception as e:
            print(e)
            driver.quit()
            return info

    def get_info(driver, div):
        from selenium.webdriver.common.action_chains import ActionChains

        ActionChains(driver).move_to_element(div).click().perform()
        driver.switch_to.window(driver.window_handles[-1])

        title = driver.find_element_by_id('page-title').text
        author = driver.find_element_by_class_name('highwire-cite-authors').text
        doi = driver.find_element_by_class_name('highwire-cite-metadata-doi').text
        abstract = driver.find_element_by_class_name('abstract').text
        date = driver.find_element_by_class_name('pane-1').text
        href = driver.find_element_by_class_name('article-dl-pdf-link').get_attribute('href')  # 全文链接
        source = href[12:19]
        if source == 'medrxiv':
            if driver.find_element_by_xpath('//*[@id="content-block-markup"]/div/h3[2]').text == 'Funding Statement':
                fund = driver.find_element_by_xpath('//*[@id="p-4"]').text
            else:
                fund = driver.find_element_by_xpath('//*[@id="p-5"]').text
        else:
            fund = ''

        try:
            category = driver.find_element_by_class_name('highwire-list').text
        except:
            category = ''
        # 调用js脚本显示作者机构
        js = "document.querySelector('div[id^=\"hw-article-author-popups-node\"]').style.display='block';"
        driver.execute_script(js)
        affiliation = {a.text for a in driver.find_elements_by_class_name('author-affiliation')}  # 作者机构

        date = mydate1(date)
        doi = doi.replace('doi: ', '')
        date_doi = mydate2(doi[24:34])
        author = author.replace('View ORCID Profile', '').replace('\n', ' ')
        abstract = abstract.replace('Abstract\n', '')

        total = {'title': title, 'doi': doi, 'date': date, 'date_doi': date_doi, 'author': author,
                 'affiliation': affiliation, 'fund': fund, 'category': category, 'abstract': abstract, 'href': href,
                 'source': source}
        return total

    def mydate1(date):
        import datetime
        time_format = datetime.datetime.strptime(date, 'Posted %B %d, %Y.')
        date = datetime.datetime.strftime(time_format, '%Y-%m-%d')
        return date

    def mydate2(date):
        import datetime
        time_format = datetime.datetime.strptime(date, '%Y.%m.%d')
        date = datetime.datetime.strftime(time_format, '%Y-%m-%d')
        return date

    def data_clean(data):
        import re
        data.drop_duplicates(subset="title", inplace=True)
        data.reset_index(inplace=True, drop=True)
        data.fillna("", inplace=True)
        ### Kewords
        data.KeyWords = [str(i).replace("作者关键词:", "") for i in data.KeyWords]
        # abstract
        data.abstract = [str(i).replace("摘要\n", "") for i in data.abstract]
        # author
        data.author = [str(i).replace("作者:", "") for i in data.author]
        # category
        data.category = [str(i).replace("研究方向:", "") for i in data.category]
        # public_date
        data.public_date = [str(i).replace("出版年: ", "") for i in data.public_date]
        # type
        data.type = [str(i).replace("文献类型:", "") for i in data.type]
        for k in range(len(data)):
            if (data['author info'][k] != ""):
                temp = [i.split(",")[0] for i in re.findall(r'\[ [0-9] \]([^,].*),', data['author info'][k])]
                for i in range(len(temp)):
                    data.author[k] = data.author[k].replace(str(i + 1), temp[i])
        data['year'] = data.public_date.apply(lambda x: x[-4:])
        data['month'] = data.public_date.apply(lambda x: re.findall(r'[A-Z]+', x))
        data['day'] = data.public_date.apply(lambda x: re.findall(r' [0-9]+ ', x))
        data['month'] = dateAdjustment(data.month)
        data['day'] = dateAdjustment(data.day)
        return data

    def dateAdjustment(x):
        temp = []
        for i in x:
            if (len(i) != 0):
                temp.append(i[0])
            else:
                temp.append("")
        return temp

    #关键词，摘要文本处理
    #input：数据库中给定条件的行，（条件筛选）
    #output：
    #展示：时间主题的变化趋势，研究的关注度（网页形式）
