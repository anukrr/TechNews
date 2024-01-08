# Visualisation Ideas
- Pie chart for topics that shows ratio of +ve, -ve.

#NLP comments
Use all parent comments
Why parent comments only? Because an unpopular opinion could generate a lot of negative children comments which aren't actually about the post itself!
    - first get a string of comment
    - run it through sentiment analysis
    - keep in df
    - prepare visualisation 

#NLP metrics
- TextBlob; -1(negative sentiment) to +1(positive sentiment)

<!-- 
TextBlob returns polarity and subjectivity of a sentence. 
Polarity lies between [-1,1], -1 defines a negative sentiment and 1 defines a positive sentiment. 
Negation words reverse the polarity.
 -->