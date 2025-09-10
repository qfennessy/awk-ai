# 🤖 PyAwk AI Functions Quick Reference

## Core AI Functions

| Function | Purpose | Example |
|----------|---------|---------|
| `ai_sentiment(text)` | Analyze emotional tone | `ai_sentiment("I love this!")` → `"positive"` |
| `ai_classify(text, categories)` | Categorize text | `ai_classify("Breaking news", "news,sports,tech")` → `"news"` |
| `ai_translate(text, lang)` | Translate to language | `ai_translate("Hello", "Spanish")` → `"Hola"` |
| `ai_summarize(text, words)` | Summarize in N words | `ai_summarize(long_text, 10)` → `"Brief summary"` |
| `ai_entity_extract(text, type)` | Find entities | `ai_entity_extract("John said", "person")` → `"John"` |
| `ai_fact_check(statement)` | Verify facts | `ai_fact_check("Earth is round")` → `"true"` |
| `ai_extract_info(text, info)` | Extract specific data | `ai_extract_info(review, "product")` → `"laptop"` |
| `ai_math_word_problem(prob)` | Solve math problems | `ai_math_word_problem("2+2=?")` → `"4"` |

## Quick Examples

### Sentiment Analysis Pipeline
```bash
python3 pyawk.py '{
    sentiment = ai_sentiment(field(0))
    print field(0) " → " sentiment
}' social_posts.txt
```

### Smart Content Classification
```bash
python3 pyawk.py '{
    category = ai_classify(field(0), "urgent,normal,low")
    print "[" category "] " field(0)
}' support_tickets.txt
```

### Multilingual Processing
```bash
python3 pyawk.py '{
    spanish = ai_translate(field(0), "Spanish")
    print "EN: " field(0)
    print "ES: " spanish
}' english_content.txt
```

### Entity Extraction
```bash
python3 pyawk.py '{
    people = ai_entity_extract(field(0), "person")
    places = ai_entity_extract(field(0), "place")
    if (people != "none") print "People: " people
    if (places != "none") print "Places: " places
}' documents.txt
```

### Combined AI Analysis
```bash
python3 pyawk.py '{
    sentiment = ai_sentiment(field(0))
    summary = ai_summarize(field(0), 15)
    category = ai_classify(field(0), "positive,negative,neutral")
    
    print "Text: " field(0)
    print "Sentiment: " sentiment  
    print "Summary: " summary
    print "Category: " category
    print ""
}' mixed_content.txt
```

## Pro Tips

1. **Chain AI functions** for powerful analysis pipelines
2. **Use in BEGIN/END blocks** for summary reports
3. **Combine with traditional AWK** for hybrid processing
4. **Filter with AI results** using conditions like `sentiment == "positive"`
5. **Store AI results** in variables for reuse

## Entity Types
- `"person"` - People names
- `"place"` - Locations, cities, countries
- `"organization"` - Companies, institutions
- `"product"` - Products, brands
- `"date"` - Dates and times

## Languages Supported
Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Korean, Arabic, Hindi, and more!

Ready to revolutionize your text processing? 🚀
