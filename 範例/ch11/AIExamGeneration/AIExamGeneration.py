import openai
import tkinter as tk
import json
from tkinter import messagebox
from docxtpl import DocxTemplate
from datetime import datetime

# 按下生成試卷鈕執行fnExamGenerate()函式
def fnExamGenerate():
    # 取得學科名稱subject、章節範圍chapters、出題數num_questions與教師姓名teacher
    subject = txtSubject_entry.get()
    chapters = txtChapter_entry.get()
    num_questions = txtNum_entry.get()
    teacher = txtTeacher_entry.get()
    # 若其中之一欄位沒有填寫則顯示對話方塊，並離開此函式
    if subject=="" or chapters=="" or num_questions=="" or teacher=="":
        messagebox.showinfo("訊息", "請正確填寫所有欄位")
        return 
    
    # 取得當前日期和時間
    current_datetime = datetime.now()
    current_date = current_datetime.date()
    
    # 範本檔名與試卷
    template_file = "試卷模版.docx"
    exam_file = "試卷(含答案).docx"
    exam_file_noAns = "試卷(無答案).docx"
    
    # 指定系統角色提示
    system_content = f"你是一位教授「{subject}」的教師，請你以此身份回覆"
    # 指定生成試題提示
    user_content = f"請出「{num_questions}」題「{chapters}」的選擇題，每一題使用JSON字串表示，JSON格式為：\n"
    user_content += '{{"exam_id": 題號, "question": "題目", "options": ["A:選項1", "B:選項2", "C:選項3", "D:選項4"], "answer": "答案"}}，\n'
    user_content += "所有題目的JSON以串列表示。"
   
    # 呼叫OpenAI API成生試題
    openai.api_key = 'OpenAIAPI金鑰'
    response = openai.chat.completions.create(
        model = 'gpt-3.5-turbo',
        messages = [
            {'role':'system', 'content':system_content},
            {'role': 'user', 'content': user_content}
        ]
    )
    exam_json=response.choices[0].message.content
    #印出成生的試題，並以json字串顯示
    #print(exam_json)
    
    #將exam_json轉成字典物件
    exam_data = json.loads(exam_json)

    # 印出每一題試題的內容，含題號、題目、選項、答案
    # for item in exam_data:
    #    print(item)
    
    # 將exam_data的試題套到「試卷模版.docx」，建立包含答案的試卷(含答案).docx
    doc = DocxTemplate(template_file)
    exam_context = { 
        "create_date": current_date,
        "course_title":subject,
        "chapters":chapters,
        "teacher": teacher,
        "exam_data":exam_data
    }
    # 建立有答案的「試卷(含答案).docx」
    doc.render(exam_context)
    doc.save(exam_file)
    
    # 建立沒有答案的 exam_date_noAns串列
    exam_date_noAns=[]
    for item in exam_data:
        item["answer"]=""
        exam_date_noAns.append(item)
    
    # 將exam_date_noAns的試題套到「試卷模版.docx」，建立沒有答案的試卷(無答案).docx
    docnoAns = DocxTemplate(template_file)
    exam_contextnoAns = { 
        "create_date": current_date,
        "course_title":subject,
        "chapters":chapters,
        "teacher": teacher,
        "exam_data":exam_date_noAns
    }
    # 建立無答案的「試卷(無答案).docx」
    docnoAns.render(exam_contextnoAns)
    docnoAns.save(exam_file_noAns)
    messagebox.showinfo("訊息","考卷建立成功")
    

# 建立主視窗
root = tk.Tk()
root.title("OpenAI考卷產生器")

# 建立學科名稱標籤和文字欄位
tk.Label(root, text="學科名稱：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
txtSubject_entry = tk.Entry(root)
txtSubject_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)

# 建立章節範圍標籤和文字欄位
tk.Label(root, text="章節範圍：").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
txtChapter_entry = tk.Entry(root)
txtChapter_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.E)

# 建立題數標籤和文字欄位
tk.Label(root, text="題數：").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
txtNum_entry = tk.Entry(root)
txtNum_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.E)

# 建立教師姓名標籤和文字欄位
tk.Label(root, text="教師姓名：").grid(row=3, column=0, padx=5,
     pady=5, sticky=tk.W)
txtTeacher_entry = tk.Entry(root)
txtTeacher_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.E)

# 建立生成試卷按鈕，按下此鈕執行fnExamGenerate()函式
btnExamGenerate = tk.Button(root, text="生成試卷", command=fnExamGenerate)
btnExamGenerate.grid(row=4, columnspan=2, padx=5, pady=10)

# 執行行主程式迴圈
root.mainloop()
