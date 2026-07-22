import csv

with open('fashion_cleaned_dataset.csv', mode='r', encoding='utf-8') as csv_file:
    with open('textfashion.txt', mode='w', encoding='utf-8') as txt_file:
        csv_read = csv.reader(csv_file)
        first_row = next(csv_read)

        for row in csv_read:
            obj = f"[Product_id:{row[0]},\ngender:{row[1]},\nmaster_Category:{row[2]},\nsub_Category:{row[3]},\narticle_Type:{row[4]},\nColour:{row[5]},\nseason:{row[6]},\nyear:{row[7]},\nusage:{row[8]},\nProduct_Name:{row[9]}],\n"

            txt_file.write(obj)
        