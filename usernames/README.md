# Username Lists

This directory contains username lists for monitoring.

## Setup Instructions

1. Create custom username lists as text files
2. One username per line
3. The tool will automatically detect and use these files

## Example Files

### example_list.txt
```
cool
epic
user
name
fire
star
moon
```

## Username Sources

The tool supports multiple username sources:

### 1. Custom File
- Load usernames from text file
- One username per line
- Supports any length (2-20 characters)

### 2. Dictionary Words
- Uses English dictionary (NLTK required)
- Filters by length (2-12 characters)
- Automatically removes invalid characters

### 3. Generated Usernames
- Creates random alphanumeric usernames
- Specify length and count
- Good for testing availability patterns

## Best Practices

- **Mix different lengths** - Include 3-6 character names for better results
- **Avoid common words** - Popular names are usually taken
- **Use combinations** - Mix letters and numbers
- **Regular updates** - Refresh lists periodically

## Character Restrictions

Discord usernames must:
- Be 2-32 characters long
- Contain only letters, numbers, periods, and underscores
- Not start or end with periods
- Not have consecutive periods

## List Management

- The tool cycles through lists infinitely
- Progress is tracked and displayed
- Can switch lists without restarting
- Supports large lists (10,000+ usernames)