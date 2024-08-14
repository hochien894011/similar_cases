import os
import pandas as pd
import requests
import datetime

# Load API key from a secure file
with open('API_keys.txt', 'r') as file:
    API_KEY = file.read().strip()

def embedding_generate(row):
    result = dict()
    result['embedding'] = ''
    result['label'] = row['label']
    result['判決字號'] = row['判決字號']  # Include the '判決字號' column in the result

    data = {
        "input": row['text'],
        "model": "text-embedding-3-large"
    }

    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        data = response.json()
        embedding = data["data"][0]["embedding"]
        result['embedding'] = embedding
        print(datetime.datetime.now())
    else:
        print(f"Error: {response.status_code}")
        print(response.text)  # This might contain error details

    return result, response.status_code == 200

def embedding_df(df):
    # Shuffle the DataFrame
    df = df.sample(frac=1).reset_index(drop=True)
    
    result_list = []
    success_count = 0
    for index, row in df.iterrows():
        if len(row['text']) < 60 or "一造辯論" in row['text']:
            continue
        result, success = embedding_generate(row)
        if success:
            result_list.append(result)
            success_count += 1
            if success_count >= 500:
                break
    result_df = pd.DataFrame(result_list)
    return result_df, result_df['label'][0] if not result_df.empty else None

def main():
    src_directory = "../data_by_label"
    
    label_list = ['撤銷贈與行為及塗銷所有權移轉登記', '返還保證金', '返還房屋', '請求侵權行為損害賠償', '所有權移轉登記', '撤銷股東會決議', '清償消費款', '代位分割遺產', '塗銷抵押權', '請求履行契約', '給付報酬金', '給付貨款', '返還訂金', '婚姻無效', '撤銷調解', '損害賠償（交通）', '確認本票債權關係不存在', '返還貨款', '塗銷分割繼承登記', '返還定金', '確認委任關係不存在', '請求返還借款', '確認派下權不存在', '履行同居', '撤銷遺產分割登記', '返還代墊款', '返還寄託物', '給付消費借貸款', '損害賠償', '返還不當得利', '交還土地', '終止收養關係', '確認非婚生子女', '塗銷抵押權登記', '返還金錢', '履行和解契約', '給付廣告費', '異議之訴', '給付信用卡消費款', '返還信用卡消費款', '返還遺產', '確認抵押權不存在', '請求離婚', '移轉所有權登記', '確定界址', '確認租賃關係存在', '返還借貸款', '返還車輛', '確認董事關係不存在', '給付扶養費', '確認董事委任關係不存在', '給付加班費', '給付獎金', '返還履約保證金', '調整租金', '給付服務報酬', '給付租金', '返還支票', '給付分期買賣價金', '返還所有權狀', '侵權行為損害賠償（交通）', '返還所有物', '給付簽帳卡消費款', '給付合會金', '返還土地', '返還租金', '宣告夫妻分別財產制', '清償信用卡消費款', '給付修繕費', '給付管理費-公寓大廈管理條例', '給付扣押款', '確認債權不存在', '不當得利', '返還工程款', '給付承攬報酬', '確認債權存在', '返還信用卡消費貸款', '債務人異議之訴', '遷讓房屋', '塗銷土地抵押權登記', '清償票款', '給付利息', '聲請宣告夫妻分別財產制', '確認經界', '拆除地上物返還土地', '確認婚姻關係不成立', '確認遺囑真正', '夫妻剩餘財產分配', '給付保險金', '給付職業災害補償金', '給付仲介費', '拆除地上物', '清償貸款', '損害賠償(交通)', '確認婚姻無效', '給付電信費', '拆屋交地', '返還無權占有土地', '國家賠償', '清償欠款', '土地所有權移轉登記', '塗銷所有權登記', '修復漏水', '債務不履行損害賠償', '當選無效', '確認派下權存在', '清償電信費', '給付買賣價金', '請求塗銷抵押權登記', '清償現金卡借貸款', '返還電信欠款', '履行買賣契約', '履行契約', '給付補償金', '第三人異議之訴', '給付電費', '返還押金', '確認本票債權不存在', '返還費用', '侵權行為損害賠償(交通)', '履行協議', '返還墊款', '返還勞保補償金', '給付遲延利息', '給付借款', '請求所有權移轉登記', '返還借款', '返還租賃房屋', '給付費用', '離婚', '請求損害賠償', '確認婚姻關係存在', '塗銷所有權移轉登記', '返還消費借貸款', '給付委任報酬', '給付保險費', '清償現金卡借款', '確認所有權存在', '履行離婚協議', '返還停車位', '確認僱傭關係存在', '清償借款', '撤銷贈與', '確認親子關係存在', '給付工程款', '給付修理費', '代位請求分割共有物', '塗銷地上權登記', '清償消費借貸款', '給付使用補償金', '確認抵押債權不存在', '給付信用卡帳款', '確認所有權', '返還電信費欠款', '侵權行為損害賠償', '清償債務', '確認股東關係不存在', '租佃爭議', '撤銷仲裁判斷', '確認親子關係不存在', '給付不當得利', '給付薪資', '執行異議', '給付運費', '給付維修費', '賠償損害', '撤銷調解之訴', '不動產所有權移轉登記', '給付退休金差額', '給付管理費', '償還犯罪被害補償金', '返還租賃物', '給付價金', '確認通行權', '返還價金', '給付代墊款', '給付土地使用補償金', '確認通行權存在', '給付電話費', '給付會款', '給付退休金', '請求給付工資', '返還牌照', '返還押租金', '確認租賃關係不存在', '確認婚姻關係不存在', '認領無效', '袋地通行權', '返還款項', '給付分期付款買賣價金', '侵害專利權有關財產權爭議', '返還存款', '代位請求分割遺產', '給付扣押薪資', '給付款項', '認領子女', '給付價款', '確認買賣關係不存在', '給付薪資扣押款', '塗銷抵押權設定登記', '宣告分別財產制', '給付公寓大廈管理費', '給付票款', '分配表異議之訴', '清償現金卡消費款', '分割共有物', '給付服務費', '返還投資款', '給付違約金', '回復原狀', '確認支票債權不存在', '返還就學貸款', '給付水費', '代位分割共有物', '返還買賣價金', '給付工資', '回復繼承權', '國家損害賠償', '償還補償金', '給付報酬', '撤銷死亡宣告', '否認子女', '返還補償金', '給付醫療費', '給付居間報酬', '排除侵害', '清償信用卡消費借款', '確認區分所有權人會議決議無效', '塗銷遺產分割登記', '宣告改用分別財產制', '拆屋還地', '塗銷不動產所有權移轉登記', '確認優先承買權存在', '確認繼承權不存在', '分割遺產', '侵害著作權有關財產權爭議', '執行異議之訴', '確認婚姻不成立', '塗銷土地所有權移轉登記', '給付醫療費用', '返還合夥出資', '給付修繕費用', '確認界址', '給付資遣費', '否認婚生子女', '給付佣金', '確認繼承權存在', '減少價金', '清償貨款', '改用夫妻分別財產制']

    
    files = [file for file in os.listdir(src_directory) if file.endswith('.csv') and not file.startswith('@') and file.split('.')[0] in label_list]
    files = sorted(files, key=lambda file: os.path.getsize(os.path.join(src_directory, file)), reverse=True)
    
    for file in files:
        file_path = os.path.join(src_directory, file)
        input_df = pd.read_csv(file_path)
        output_df, df_label = embedding_df(input_df)
        if df_label:
            output_path = f"../embedded/{df_label}.csv"
            output_df.to_csv(output_path, index=False)
        os.rename(file_path, os.path.join(src_directory, f"@{file}"))
            
if __name__ == "__main__":
    main()
