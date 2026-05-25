import pandas as pd


def order_to_excel(order_obj):

    # داده‌ها (می‌تونی از هر منبعی بگیری: API، فایل JSON، و غیره)
    data = [
        {
            "id": 1,
            "attribute": 1,
            "attribute_name": "option 1",
            "selected_option": 1,
            "selected_option_name": "value 1 is long value for test",
            "value": "value_1"
        },
        {
            "id": 2,
            "attribute": 2,
            "attribute_name": "option 2",
            "selected_option": 4,
            "selected_option_name": "value 2",
            "value": "value_2"
        },
        {
            "id": 3,
            "attribute": 3,
            "attribute_name": "تعداد",
            "selected_option": 9,
            "selected_option_name": "30",
            "value": "30"
        }
    ]

    # ساخت DataFrame با فقط دو ستون مورد نظر
    df = pd.DataFrame(data)[["attribute_name", "selected_option_name"]]

    # ذخیره به فایل اکسل
    output_path = "order_attributes.xlsx"
    df.to_excel(output_path, index=False)

    print(f"✅ فایل اکسل ساخته شد: {output_path}")
