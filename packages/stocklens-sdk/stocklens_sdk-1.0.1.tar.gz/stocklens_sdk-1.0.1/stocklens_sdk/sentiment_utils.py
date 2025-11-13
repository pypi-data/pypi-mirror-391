from textblob import TextBlob

def analyze_sentiment(text):
    """Returns sentiment label and score based on polarity."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        sentiment = "Positive"
    elif polarity < -0.1:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    return sentiment, round(polarity, 2)
