# This file contains the core logic for your NLP package.
import re

# This is the "NLP" part: a mapping of keywords to emojis.
# You can expand this list as much as you want!
EMOJI_MAP = {
    'happy': '😊',
    'sad': '😢',
    'love': '❤️',
    'heart': '❤️',
    'cat': '🐱',
    'dog': '🐶',
    'sun': '☀️',
    'moon': '🌙',
    'star': '⭐',
    'coffee': '☕',
    'tea': '🍵',
    'book': '📚',
    'rain': '🌧️',
    'raining': '🌧️',
    'fire': '🔥',
    'hot': '🔥',
    'cold': '❄️',
    'winter': '❄️',
    'snow': '❄️',
    'tree': '🌳',
    'flower': '🌸',
    'pizza': '🍕',
    'burger': '🍔',
    'computer': '💻',
    'code': '💻',
    'coding': '💻',
    'phone': '📱',
    'music': '🎵',
    'party': '🎉',
    'congratulations': '🎉',
    'celebrate': '🎉',
    'cry': '😢',
    'laugh': '😂',
    'smile': '😊',
    'think': '🤔',
    'brain': '🧠',
    'strong': '💪',
    'muscle': '💪',
    'ghost': '👻',
    'sleep': '😴',
    'tired': '😴',
    'money': '💰',
    'cash': '💰',
    'win': '🏆',
    'success': '🏆',
}


def emojify(text, replace=False):
    """
    Appends or replaces keywords in a text string with their corresponding emojis.

    Args:
        text (str): The input text.
        replace (bool, optional): 
            If False (default), appends the emoji after the word.
            If True, replaces the word with the emoji.

    Returns:
        str: The emojified text.
    """
    
    # We iterate over a copy of the keys to avoid any runtime errors
    # if we wanted to modify the dict (though we don't here).
    for keyword in EMOJI_MAP.keys():
        emoji = EMOJI_MAP[keyword]
        
        # \b is a "word boundary" so we don't replace "cat" in "caterpillar"
        # re.IGNORECASE makes the match case-insensitive
        pattern = r'\b' + re.escape(keyword) + r'\b'
        
        if replace:
            # Replace the word entirely with the emoji
            replacement = emoji
        else:
            # Append the emoji after the word
            # \g<0> refers to the entire match (i.e., the original word)
            replacement = r'\g<0> ' + emoji
            
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text

# --- This is the new part! ---
if __name__ == "__main__":
    # This block only runs when you execute this file directly.
    # It won't run when your package is imported by another user.
    print("--- Testing emojify() ---")
    
    test_text = "I am so happy to drink my coffee and code. I love my cat!"
    
    # Test 1: Append mode (default)
    emojified_text = emojify(test_text)
    print("Append mode:")
    print(emojified_text)
    # Expected output: "I am so happy 😊 to drink my coffee ☕ and code 💻. I love ❤️ my cat 🐱!"
    
    print("-" * 20)
    
    # Test 2: Replace mode
    replaced_text = emojify(test_text, replace=True)
    print("Replace mode:")
    print(replaced_text)
    # Expected output: "I am so 😊 to drink my ☕ and 💻. I ❤️ my 🐱!"