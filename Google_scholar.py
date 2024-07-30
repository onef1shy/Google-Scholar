import math
import time
import random
import requests_html
import random
import time
import json
from io import TextIOWrapper
from jupyterlab_server import translator
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models


class Gather:
    def __init__(self) -> None:
        option = Options()
        # option.add_argument('--headless')
        self.driver = webdriver.Chrome(options=option)
        self.Passage_name = []
        self.Cited_by = []
        src = input("请输入您的文章页面网址：")
        self.driver.get(src)
        self.page_no = 0
        self.src = []
        self.name = ""
        self.file = None
        self.sum = 0
        self.SecretId = "AKIDDkM0tZ2QjpiWH7fo1gXDhz63xSQVQKqF"
        self.SecretKey = "qfTp4a7zqUokgKsATntlYSOGzyzXw88t"

    def get_result(self, id_d):
        try:
            cred = credential.Credential(self.SecretId, self.SecretKey)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "asr.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = asr_client.AsrClient(cred, "", clientProfile)

            req = models.DescribeTaskStatusRequest()
            params = {
                "TaskId": id_d
            }
            req.from_json_string(json.dumps(params))

            resp = client.DescribeTaskStatus(req)
            # print(resp.to_json_string())
            if json.loads(resp.to_json_string())["Data"]["StatusStr"] == "waiting" or json.loads(resp.to_json_string())["Data"]["StatusStr"] == "doing":
                return False
            try:
                json.loads(resp.to_json_string())[
                    "Data"]["Result"].split("]")[-1][2:]
            except:
                # print(json.loads(resp.to_json_string()))
                return False
            return json.loads(resp.to_json_string())["Data"]["Result"].split("]")[-1][2:-1]

        except TencentCloudSDKException as err:
            print(err)
            return False

    # 上传音频链接msg_url

    def upload(self, msg_url):
        try:
            cred = credential.Credential(self.SecretId, self.SecretKey)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "asr.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = asr_client.AsrClient(cred, "", clientProfile)

            req = models.CreateRecTaskRequest()
            params = {
                "EngineModelType": "16k_en",
                "ChannelNum": 1,
                "ResTextFormat": 0,
                "SourceType": 0,
                "Url": msg_url
            }
            req.from_json_string(json.dumps(params))

            resp = client.CreateRecTask(req)
            # print(resp)
            ID = json.loads(resp.to_json_string())["Data"]["TaskId"]
            # print(ID)
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

    # 关键点，上面两函数直接套着用就行了，不用管，这里是重点

    def pass_recaptha(self):
        # 点击验证
        # 等待加载上验证框，验证框iframe被套在一个form中
        WebDriverWait(self.driver, 15, 0.5).until(
            EC.visibility_of_element_located((By.XPATH,
                                              '//*[@id="gs_captcha_c"]/div/div/iframe')))
        # 进入验证框所在iframe
        self.driver.switch_to.frame(self.driver.find_element(By.XPATH,
                                                             '//*[@id="gs_captcha_c"]/div/div/iframe'))
        print("加载验证中")
        # 等待勾选框可点击再点击
        WebDriverWait(self.driver, 15, 0.5).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#recaptcha-anchor"))).click()
        # 随机2~3秒避免加载不出来
        time.sleep(random.uniform(2, 3))
        print(1)
        try:
            # 回到默认页面
            self.driver.switch_to.default_content()
            # 等待点击勾选框后的弹窗界面iframe有没有加载出来
            WebDriverWait(self.driver, 15, 0.5).until(
                EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[4]/iframe')))
            # 进入弹窗界面的iframe
            self.driver.switch_to.frame(self.driver.find_element(
                By.XPATH, '/html/body/div[2]/div[4]/iframe'))
            print(2)
            # 等待语音按钮是否加载出来，注意，这里在shadow-root里面，不可以直接用css选择器或xpath路径点击
            WebDriverWait(self.driver, 30, 0.5).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="recaptcha-audio-button"]')))
            print(3)
            # 选中语音按钮
            button = self.driver.find_element(
                By.XPATH, '//*[@id="recaptcha-audio-button"]')
            button.click()
            # 初始化键盘事件
            print("点击了语音按钮")
            # 等待页面跳转出现下载按钮，跳转后会出现语音下载按钮，需要捕获它的href值，它就是音频链接msg_url
            WebDriverWait(self.driver, 30, 0.5).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="rc-audio"]/div[7]/a')))
            msg_url = self.driver.find_element(
                # 获取链接
                By.XPATH, '//*[@id="rc-audio"]/div[7]/a').get_attribute("href")
            print(4)
            result1 = self.upload(msg_url)  # 上传链接返回结果
            time.sleep(1)
            print(5)
            print("识别结果为：")
            print(result1)
            # 等待加载填写框
            WebDriverWait(self.driver, 15, 0.5).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="audio-response"]')))
            # 选中填写框
            self.driver.find_element(
                By.XPATH, '//*[@id="audio-response"]').send_keys(result1)
            print(6)
            # 随机时长，避免判断为机器人
            time.sleep(random.uniform(1.5, 3))
            # 等待加载verify验证按钮
            WebDriverWait(self.driver, 15, 0.5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="recaptcha-verify-button"]')))
            # 选中点击verify按钮
            self.driver.find_element(
                By.XPATH, '//*[@id="recaptcha-verify-button"]').click()
            print(translator.trans("语音验证通过"))
        except Exception as e:
            print(e)
        print(7)
        # 回到初始页面，进行下一步操作
        self.driver.switch_to.default_content()
        print(8)

    def JumpInfo(self):
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
                split_index = aut_name.find(' - ')

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
            self.pass_recaptha()

    def main(self):
        self.JumpInfo()
        self.file.close()
        self.driver.quit()


if __name__ == '__main__':
    gat = Gather()
    gat.main()
