# 导入必要的库
import math
import time
import random
import requests_html
import json
from io import TextIOWrapper

# Selenium相关导入
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# 腾讯云SDK相关导入
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models


class Gather:
    def __init__(self) -> None:
        # 初始化Chrome浏览器选项
        option = Options()
        # option.add_argument('--headless')  # 可选：启用无头模式
        self.driver = webdriver.Chrome(options=option)  # 创建Chrome浏览器实例
        self.Passage_name = []  # 存储文章名称
        self.Cited_by = []  # 存储被引用次数
        src = input("请输入您的文章页面网址：")  # 获取用户输入的网址
        self.driver.get(src)  # 打开指定网址
        self.page_no = 0  # 初始化页码
        self.src = []  # 存储链接
        self.name = ""  # 存储作者名称
        self.file = None  # 文件对象，用于写入数据
        self.sum = 0  # 计数器
        # 腾讯云API密钥，需要替换为实际的密钥
        self.SecretId = ""
        self.SecretKey = ""

    def get_result(self, id_d):
        # 获取语音识别任务的结果
        try:
            # 创建腾讯云认证对象
            cred = credential.Credential(self.SecretId, self.SecretKey)
            # 配置HTTP选项
            httpProfile = HttpProfile()
            httpProfile.endpoint = "asr.tencentcloudapi.com"
            
            # 创建客户端配置
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            # 创建ASR客户端
            client = asr_client.AsrClient(cred, "", clientProfile)

            # 创建查询任务状态的请求
            req = models.DescribeTaskStatusRequest()
            params = {
                "TaskId": id_d
            }
            req.from_json_string(json.dumps(params))

            # 发送请求并获取响应
            resp = client.DescribeTaskStatus(req)
            # 解析响应结果
            if json.loads(resp.to_json_string())["Data"]["StatusStr"] == "waiting" or json.loads(resp.to_json_string())["Data"]["StatusStr"] == "doing":
                return False
            try:
                json.loads(resp.to_json_string())[
                    "Data"]["Result"].split("]")[-1][2:]
            except:
                return False
            return json.loads(resp.to_json_string())["Data"]["Result"].split("]")[-1][2:-1]

        except TencentCloudSDKException as err:
            print(err)
            return False

    def upload(self, msg_url):
        # 上传音频链接并创建识别任务
        try:
            # 创建腾讯云认证对象
            cred = credential.Credential(self.SecretId, self.SecretKey)
            # 配置HTTP选项
            httpProfile = HttpProfile()
            httpProfile.endpoint = "asr.tencentcloudapi.com"

            # 创建客户端配置
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            # 创建ASR客户端
            client = asr_client.AsrClient(cred, "", clientProfile)

            # 创建识别任务请求
            req = models.CreateRecTaskRequest()
            params = {
                "EngineModelType": "16k_en",
                "ChannelNum": 1,
                "ResTextFormat": 0,
                "SourceType": 0,
                "Url": msg_url
            }
            req.from_json_string(json.dumps(params))

            # 发送请求并获取响应
            resp = client.CreateRecTask(req)
            ID = json.loads(resp.to_json_string())["Data"]["TaskId"]
            
            # 等待识别结果
            count = 0
            while True:
                st = self.get_result(int(ID))
                if st != False:
                    break
                time.sleep(0.7)
                count += 1
                if count > 120:
                    return
            print(st)
            return st
        except TencentCloudSDKException as err:
            print(err)

    def pass_recaptha(self):
        # 处理Google reCAPTCHA验证
        # 等待验证框加载
        WebDriverWait(self.driver, 15, 0.5).until(
            EC.visibility_of_element_located((By.XPATH,
                                              '//*[@id="gs_captcha_c"]/div/div/iframe')))
        # 切换到验证框iframe
        self.driver.switch_to.frame(self.driver.find_element(By.XPATH,
                                                             '//*[@id="gs_captcha_c"]/div/div/iframe'))
        print("加载验证中")
        # 点击复选框
        WebDriverWait(self.driver, 15, 0.5).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#recaptcha-anchor"))).click()
        time.sleep(random.uniform(3, 4))
        print(1)
        try:
            # 处理音频验证
            self.driver.switch_to.default_content()
            WebDriverWait(self.driver, 15, 0.5).until(
                EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[4]/iframe')))
            self.driver.switch_to.frame(self.driver.find_element(
                By.XPATH, '/html/body/div[2]/div[4]/iframe'))
            print(2)
            WebDriverWait(self.driver, 30, 0.5).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="recaptcha-audio-button"]')))
            print(3)
            button = self.driver.find_element(
                By.XPATH, '//*[@id="recaptcha-audio-button"]')
            button.click()
            print("点击了语音按钮")
            WebDriverWait(self.driver, 30, 0.5).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="rc-audio"]/div[7]/a')))
            msg_url = self.driver.find_element(
                By.XPATH, '//*[@id="rc-audio"]/div[7]/a').get_attribute("href")
            print(4)
            result1 = self.upload(msg_url)  # 上传音频链接并获取识别结果
            time.sleep(1)
            print(5)
            print("识别结果为：")
            print(result1)
            WebDriverWait(self.driver, 15, 0.5).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="audio-response"]')))
            self.driver.find_element(
                By.XPATH, '//*[@id="audio-response"]').send_keys(result1)
            print(6)
            time.sleep(random.uniform(1.5, 3))
            WebDriverWait(self.driver, 15, 0.5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="recaptcha-verify-button"]')))
            self.driver.find_element(
                By.XPATH, '//*[@id="recaptcha-verify-button"]').click()
            print("语音验证通过")
        except Exception as e:
            print(e)
        print(7)
        self.driver.switch_to.default_content()
        print(8)

    def JumpInfo(self):
        # 获取文章信息
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="gsc_a_b"]/tr/td[2]/a')))
        Passage_name = self.driver.find_elements(
            By.XPATH, '//*[@id="gsc_a_b"]/tr/td[1]/a')
        Cited_by = self.driver.find_elements(
            By.XPATH, '//*[@id="gsc_a_b"]/tr/td[2]/a')
        for Passage, Cited in zip(Passage_name, Cited_by):
            self.Passage_name.append(Passage.text)
            if Cited.text != '':
                self.Cited_by.append(int(Cited.text))
            else:
                self.Cited_by.append(0)
            self.src.append(Cited.get_attribute('href'))
        self.name = self.driver.find_element(
            By.XPATH, '//*[@id="gsc_prf_in"]').text
        self.file: TextIOWrapper = open(f'{self.name}_Infomation.txt', 'a')
        self.getInfo()

    def getInfo(self):
        # 获取每篇文章的引用信息
        for i in range(len(self.Cited_by)):
            if (self.Cited_by[i] > 0):
                self.page_no = math.ceil(self.Cited_by[i]/10)
                if self.page_no > 100:
                    self.page_no = 100
                self.file.write(f"{self.Passage_name[i]}:"
                                f"{self.Cited_by[i]}\n")
                self.sum = 0
                self.collectInfo(id=i)

    def collectInfo(self, id):
        # 收集引用文章的详细信息
        base_url = self.src[id]
        for num in range(self.page_no):
            extend = f'&start={num*10}'
            url = base_url+extend
            HTML = self.get_html(url)
            cite_page_name = HTML.xpath('//h3/a')
            cite_page_src = HTML.xpath('//h3/a/@href')
            cite_aut_name = HTML.xpath(
                '//*[@id="gs_res_ccl_mid"]/div/div/div[1]')
            cite_aut_name = [
                cite_aut.text for cite_aut in cite_aut_name if '[PDF]' not in cite_aut.text and '[HTML]' not in cite_aut.text]
            for page_name, aut_name, page_src in zip(cite_page_name, cite_aut_name, cite_page_src):
                split_index = aut_name.find(' - ')

                if split_index != -1:
                    authors = aut_name[:split_index].strip()
                    publication_info = aut_name[split_index + 3:].strip()
                else:
                    plit_index = aut_name.find(' - ')
                    authors = aut_name[:plit_index].strip()
                    publication_info = aut_name[plit_index + 3:].strip()
                self.sum += 1
                self.file.write(f'  {self.sum}:\n')
                self.file.write(f"\tCited_By_Passage: {page_name.text}\n"
                                f"\tCited_By_Author: {authors}\n"
                                f"\tCited_By_Journal: {publication_info}\n"
                                f"\tPassage_Src: {page_src}\n")

    def get_html(self, url):
        # 获取页面HTML内容
        if self.driver is None:
            raise Exception("driver is not configured!")
        self.driver.get(url)
        time.sleep(random.randint(1, 5))

        while True:
            try:
                self.driver.find_element(
                    By.CSS_SELECTOR, '#gs_captcha_ccl,#recaptcha')
            except NoSuchElementException:
                try:
                    html = self.driver.find_element(
                        By.CSS_SELECTOR, '#gs_top').get_attribute('innerHTML')
                    return requests_html.HTML(html=html)
                except NoSuchElementException:
                    print("google has blocked this browser, reopening")
                    self.driver.close()
                    self.driver = webdriver.Chrome()
                    return self.get_html(url)

            print("... it's CAPTCHA time!\a ...")
            # self.pass_recaptha()
            time.sleep(5)

    def main(self):
        # 主函数，执行整个流程
        self.JumpInfo()
        self.file.close()
        self.driver.quit()


if __name__ == '__main__':
    gat = Gather()
    gat.main()
