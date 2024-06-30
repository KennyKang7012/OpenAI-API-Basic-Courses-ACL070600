import base64
import requests
import openai
import re
import os
import tkinter as tk
from tkinter import filedialog, messagebox

html_file_name="sample.html"  #生成網頁檔名 
image_file_name="image.jpg"   #生成圖檔檔名

# OpenAI API金鑰
openapi_key="OpenAIAPI金鑰" 

# 將image_path的圖片讀取並進行 Base64 編碼，最後將編碼後的字串以 UTF-8 解碼傳回
def EncodeImage(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# 進行視覺分析取得網頁程式碼
def Vision(image): 
  api_key =  openapi_key
  base64_image = EncodeImage(image)
  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
  }
  payload = {
    "model":"gpt-4o", #建議使用gpt-4o，在非英語語言方面具有最佳的視覺和表現
    "messages":[
      {
        "role":"user",
        "content": [
          {"type":"text","text":"圖像為網頁佈局設計草圖，請提供網頁的HTML和CSS程式碼就可以，且CSS程式碼放在<style>內，將<img>的src皆指定為image.jpg。"},
          {"type":"image_url",
           "image_url":{"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]
      }
    ],
    "max_tokens": 2000
  }
  response = requests.post("https://api.openai.com/v1/chat/completions",
      headers=headers,json=payload)
  dictRes = response.json()
  return dictRes['choices'][0]['message']['content']

# OpenAI生成圖檔，並傳回圖檔網址
def GImageUrl(imgPrompt):
    openai.api_key=openapi_key
    response = openai.images.generate(
        model="dall-e-2",  #使用dall-e-2模型，可自行替換
        prompt=imgPrompt,
        size="512x512",
        quality="standard",
        n=1,
    )
    # 圖片的 URL
    return response.data[0].url

# 按 [瀏覽圖檔] 鈕執行 fnBrowseImage() 函式
def fnBrowseImage():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        lblImage.config(text=file_path) # lblImage顯示選擇的圖檔檔名

# 按 [分析圖檔] 鈕執行 fnAnalyzeImage() 函式
def fnAnalyzeImage():
    # 取得圖檔檔名
    image_filename = lblImage.cget("text")
    # 若image_filename圖檔名稱為空，則顯示對話對話方塊
    if image_filename=="":
        messagebox.showinfo("上傳圖檔",
            "請按 [瀏覽圖檔] 鈕，選擇要分析的網頁佈局圖")
        return # 離開 fnAnalyzeImage 函式
    # 使用正規表達式 ( Regualr expression ) 找到被「```html」~「```」括住的內容
    match = re.search(r"```html(.*?)```",
        Vision(image_filename), re.DOTALL)
    html_content=""
    if match:
        # 提取匹配的字串，即找被「```html」~「```」括住的字串，再指定給html_content
        html_content = match.group(1)
        txtHtmlContent.delete(1.0, tk.END)  
        # 將生成的網頁程式碼顯示在description_text內
        txtHtmlContent.insert(tk.END, html_content)  
        
        # 若網頁中有img，即生成圖檔  
        if "img" in html_content:
            # 圖片提示
            imgPrompt = txtImgPrompt.get()
            # 圖片的 URL
            image_url = GImageUrl(imgPrompt)
            # 發送 HTTP 請求，下載圖片
            response = requests.get(image_url)
            # 檢查請求是否成功
            if response.status_code == 200:
                # 將圖片儲存到目前路徑
                with open(image_file_name, "wb") as image_file:
                    image_file.write(response.content)
            else:
                messagebox.showinfo("圖片生成失敗", f"無法下載圖片，HTTP 狀態碼:{response.status_code}")
        
        # 打開檔案並寫入 HTML 內容
        with open(html_file_name, 'w', encoding='utf-8') as html_file:
            html_file.write(html_content)
            os.startfile(html_file_name)    
    else:
        messagebox.showinfo("分析結果", f"網頁成生失敗")

# 主視窗
root = tk.Tk()
root.title("OpenAI網頁產生器")

# [瀏覽圖檔] ，按下此鈕執行fnBrowseImage()函式，可進行選圖
btnBrowse = tk.Button(root, text="瀏覽圖檔", command=fnBrowseImage)
btnBrowse.grid(row=0, column=0, padx=10, pady=5)
lblImage = tk.Label(root, text="")
lblImage.grid(row=0, column=1, columnspan=2, padx=10, pady=5)

# 圖檔提示單行文字欄
lblImgPrompt = tk.Label(root, text="圖檔提示：")
lblImgPrompt.grid(row=1, column=0, padx=10, pady=5)
txtImgPrompt = tk.Entry(root)
txtImgPrompt.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

# 網頁程式碼多行文字方塊
lblHtmlContent = tk.Label(root, text="網頁程式碼:")
lblHtmlContent.grid(row=2, column=0, sticky="w", padx=10, pady=5)
txtHtmlContent = tk.Text(root, width=50, height=7)
txtHtmlContent.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky=tk.W)

# [分析圖檔] 按鈕，按下此鈕執行fnAnalyzeImage()函式
btnAnalyze = tk.Button(root, text="分析圖檔", command=fnAnalyzeImage)
btnAnalyze.grid(row=3, column=1, padx=10, pady=5)

# 啟動視窗主迴圈
root.mainloop()
