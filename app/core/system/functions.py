import re

def clean_html(html_string):
    # Удаляем теги <a> вместе с содержимым
    cleaned_string = re.sub(r'<a[^>]*>.*?</a>', '', html_string, flags=re.DOTALL)
    
    # Заменяем теги <p> на символ новой строки
    cleaned_string = re.sub(r'<p>', '\n', cleaned_string)
    cleaned_string = re.sub(r'</p>', '', cleaned_string)  # Удаляем закрывающий тег </p>
    
    # Удаляем все остальные HTML-теги
    cleaned_string = re.sub(r'<[^>]+>', '', cleaned_string)
    
    # Удаляем лишние символы новой строки
    cleaned_string = re.sub(r'\n+', '\n\n', cleaned_string)  # Заменяем несколько \n на два
    cleaned_string = cleaned_string.strip()  # Удаляем пробелы в начале и конце

    return cleaned_string
