#!/usr/bin/env python3

from examples.return_functions import check_eligibility, validate_reason, process_return
from examples.greeting_functions import create_personalized_greeting

# Test state-based function calls
test_state = {
    'order_id': 'ORD123',
    'return_reason': 'damaged item',
    'name': 'John',
    'age': 25
}

print('✅ Testing check_eligibility:', check_eligibility(test_state))
print('✅ Testing validate_reason:', validate_reason(test_state))
print('✅ Testing process_return:', process_return(test_state))
print('✅ Testing create_personalized_greeting:', create_personalized_greeting(test_state))
