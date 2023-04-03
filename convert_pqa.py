import json

with open("amazon-pqa/amazon_pqa_headsets.json") as input:
  with open("amazon-pqa/converted_amazon_pqa_headsets_1000.json","w") as output:
    i=0
    for line in input:
      line_data = json.loads(line)
      meta = '{"index":{"_index":"nlp_pqa"}}\n'
      output.write(meta)
      data = '{"question":"' 
      data = data + line_data['question_text']
      data = data + '","answer":"'
      data = data + line_data['answers'][0]['answer_text']
      data = data + '"}\n'
      output.write(data)
      i+=1
      if(i == 1000):
        break
      
print("converted file is saved to 'amazon-pqa/converted_amazon_pqa_headsets_1000.json'")