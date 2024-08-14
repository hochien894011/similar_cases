import os
import json
import re
import pandas as pd
import argparse

# 定義數字項的串列
segment_list = [
    ('甲、', '乙、', '丙、', '丁、', '戊、', '己、', '庚、', '辛、', '壬、', '奎、'),
    ('壹、', '貳、', '參、', '叄、', '叁、', '参、', '肆、', '伍、', '陸、', '柒、', '捌、', '玖、', '拾、'),
    ('一、', '二、', '三、', '四、', '五、', '六、', '七、', '八、', '九、', '十、', '十一、', '十二、', '十三、', '十四、', '十五、', '十六、', '十七、', '十八、', '十九、', '二十 '),
    ('','','','','','','','','','','','','','','','','','','','','','',''),
    ('（一）', '（二）', '（三）', '（四）', '（五）', '（六）', '（七）', '（八）', '（九）', '（十）', '（十一）', '（十二）', '（十三）', '（十四）', '（十五）', '（十六）', '（十七）', '（十八）', '（十九）', '（二十）'),
    ('(一)', '(二)', '(三)', '(四)', '(五)', '(六)', '(七)', '(八)', '(九)', '(十)', '(十一)', '(十二)', '(十三)', '(十四)', '(十五)', '(十六)', '(十七)', '(十八)', '(十九)', '(二十)'),
    ('㈠','㈡','㈢','㈣','㈤','㈥','㈦','㈧','㈨','㈩'),
    ('㊀', '㊁', '㊂', '㊃', '㊄', '㊅', '㊆', '㊇', '㊈', '㊉')
    ]
all_segment = tuple()
for segment in segment_list:
    all_segment += segment

def find_material_part(fact):
    for index, line in enumerate(fact):
        for segments in segment_list:
            for s in segments:
                material_pattern = '^' + s + '實體'
                if re.match(material_pattern, line):
                    return index
    return -1

def find_position(fact):
    # 把原告主張的部分通通加進array中並回傳
    for line in fact:
        for num, segments in enumerate(segment_list):
            for n,s in enumerate(segments):
                plantiff_pattern = '^' + s + '(本件|本訴)?原(告|吿)'
                if re.match(plantiff_pattern, line):
                    return num, n
    return -1, -1

def find_second_part(fact):
    # 把原告主張的部分通通加進array中並回傳
    for line in fact:
        for num, segments in enumerate(segment_list):
            for n,s in enumerate(segments):
                plantiff_pattern = '^' + s + '事實摘要'
                if re.match(plantiff_pattern, line):
                    return num, n
    return -1, -1


def crop_judgement(judgement):
    
    # 初始化
    result = dict()
    result['判決字號'] = ''
    #result['字別'] = ''
    result['案由'] = ''
    result['主文'] = ''
    result['原告主張'] = ''
    jfull_raw = judgement['JFULL'].splitlines()

    # 判決字號
    result['判決字號'] = judgement['JID']
    
    # 判決字別
    #result['字別'] = judgement['JCASE']

    # 案由
    result['案由'] = judgement['JTITLE']

    # 格式化判決的主文及事實與理由
    judgement_dict = dict()
    titles = ['主文', '事實', '理由', '事實及理由', '事實及理由要領']
    pattern_title = '^\s*(' + '|'.join(['\s*'.join(title) for title in titles]) + ')\s*$'
    pattern_date = '^\s*中\s*華\s*民\s*國.*年.*月.*日\s*$'
    flag = None
    for num, line in enumerate(jfull_raw):
        if num == 0:
            continue
        # section
        if re.match(pattern_title, line) is not None:
            flag = re.sub('\s', '', line)
            judgement_dict[flag] = list()
        elif re.match(pattern_date, line) is not None:
            flag = None
            break
        elif flag is not None:
            judgement_dict[flag].append(line.strip())
            
    # 主文
    try:
        main_result = ''.join(judgement_dict['主文'])
        # 將主文以句點分割，並刪除空元素
        main_result = main_result.split("。")
        if main_result[-1] == "":
            main_result.pop()       
    except:
        main_result = []
    result['主文'] = main_result
    
    plantiff = []
    
    # 事實與理由
    
    # 找有效title
    target_title = None
    try:
        for title in judgement_dict.keys():
            if re.match("事實",title):
                target_title = title
    except:
        target_title = None
    
    # 找原告的區塊  
    if target_title is not None:
        index = find_material_part(judgement_dict[target_title])
        if index > 0:
            judgement_dict[target_title] = judgement_dict[target_title][index:]
        segment_pos, s_pos = find_second_part(judgement_dict[target_title])
        if segment_pos > -1:
            plantiff_pattern = "^" + segment_list[segment_pos][s_pos] + "事實"
            try:
                defendant_pattern = "^" + segment_list[segment_pos][s_pos+1]
                sentinal = 0
                for line in judgement_dict[target_title]:
                    if re.match(plantiff_pattern,line):
                        sentinal = 1
                    if re.match(defendant_pattern,line) and sentinal == 1:
                        sentinal = 0
                        break
                    if sentinal == 1:
                        plantiff.append(line)
            except:
                segment_pos, s_pos = find_position(judgement_dict[target_title])
                if segment_pos > -1:
                    plantiff_pattern = "^" + segment_list[segment_pos][s_pos] + '(本件|本訴)?原(告|吿)'
                    try:
                        defendant_pattern = "^" + segment_list[segment_pos][s_pos+1]
                    except:
                        return result
                    sentinal = 0
                    for line in judgement_dict[target_title]:
                        if re.match(plantiff_pattern,line):
                            sentinal = 1
                        if re.match(defendant_pattern,line) and sentinal == 1:
                            sentinal = 0
                            break
                        if sentinal == 1:
                            plantiff.append(line)
            
        
                
        else:
            segment_pos, s_pos = find_position(judgement_dict[target_title])
            if segment_pos > -1:
                plantiff_pattern = "^" + segment_list[segment_pos][s_pos] + '(本件|本訴)?原(告|吿)'
                try:
                    defendant_pattern = "^" + segment_list[segment_pos][s_pos+1]
                except:
                    return result
                sentinal = 0
                for line in judgement_dict[target_title]:
                    if re.match(plantiff_pattern,line):
                        sentinal = 1
                    if re.match(defendant_pattern,line) and sentinal == 1:
                        sentinal = 0
                        break
                    if sentinal == 1:
                        plantiff.append(line)
            
    
    plantiff_claim = ''.join(plantiff)
    result['原告主張'] = plantiff_claim
    
    
    # 傳回主程式
    return result
    

def process_directory(directory):
    rows = []
    total = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    judgement = json.load(f)
                    print(file_path)
                    judgement_data = crop_judgement(judgement)  # Assuming crop_judgement function is defined
                    if judgement_data['判決字號'] != '' and judgement_data['案由'] != '' and judgement_data['主文'] != '' and judgement_data['原告主張'] != '':
                        rows.append(judgement_data)
                        total += 1
    
    df = pd.DataFrame(rows)
    return df

def main(folder_num):
    processed_csv = process_directory("../"+folder_num)
    processed_csv.to_csv("../preprocess_data/"+folder_num+".csv", index=False)
    print(f"Processed data saved to {folder_num}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process directory of JSON files.")
    parser.add_argument("folder_num", type=str, help="Directory containing JSON files.")
    args = parser.parse_args()

    main(args.folder_num)
    
# other segementation
#('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.', '14.', '15.', '16.', '17.', '18.', '19.', '20.'),
#('⒈', '⒉', '⒊', '⒋', '⒌', '⒍', '⒎', '⒏', '⒐', '⒑', '⒒', '⒓', '⒔', '⒕', '⒖', '⒗', '⒘', '⒙', '⒚', '⒛'),
#('⑴','⑵','⑶','⑷','⑸','⑹','⑺','⑻','⑼','⑽','⑾','⑿','⒀','⒁','⒂','⒃','⒄','⒅','⒆','⒇'),
#('①','②','③','④','⑤','⑥','⑦','⑧','⑨','⑩','⑪','⑫','⑬','⑭','⑮','⑯','⑰','⑱','⑲','⑳'),
#('❶', '❷', '❸', '❹', '❺', '❻', '❼', '❽', '❾', '❿', '⓫', '⓬', '⓭', '⓮', '⓯', '⓰', '⓱', '⓲', '⓳', '⓴'),
#('⓵', '⓶', '⓷', '⓸', '⓹', '⓺', '⓻', '⓼', '⓽', '⓾'),
#('A.', 'B.', 'C.', 'D.', 'E.', 'F.', 'G.', 'H.', 'I.', 'J.', 'K.'),
#('Ⅰ','Ⅱ','Ⅲ','Ⅳ','Ⅴ','Ⅵ','Ⅶ','Ⅷ','Ⅸ','Ⅹ')