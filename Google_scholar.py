from io import TextIOWrapper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import math
import time
import random
import requests_html


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
            time.sleep(5)

    def main(self):
        self.JumpInfo()
        self.file.close()
        self.driver.quit()


if __name__ == '__main__':
    gat = Gather()
    gat.main()
