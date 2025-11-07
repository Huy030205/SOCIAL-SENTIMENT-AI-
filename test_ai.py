from transformers import pipeline

# Tạo pipeline phân tích cảm xúc
sentiment = pipeline("sentiment-analysis")

# Nhập văn bản cần phân tích
text = input("Nhập bài đăng: ")

# Phân tích cảm xúc
result = sentiment(text)[0]

print("Kết quả:", result['label'])
print("Độ tin cậy:", round(result['score'] * 100, 2), "%")
