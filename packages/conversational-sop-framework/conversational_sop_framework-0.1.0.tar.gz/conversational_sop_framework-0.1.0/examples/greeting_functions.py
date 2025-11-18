def create_personalized_greeting(state: dict) -> str:
    name = state.get('name')
    age = state.get('age')
    return f"Nice to meet you, {name}! You are {age} years old. Welcome!"
