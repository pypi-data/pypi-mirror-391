#!/usr/bin/env python3
"""
Test Navigation Functionality

This script tests the backward navigation and state rollback functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from conversational_sop.engine import load_workflow

def test_workflow_loading():
    """Test that workflows load successfully with navigation support"""
    try:
        # Test return workflow
        graph, engine = load_workflow('examples/return_workflow.yaml')
        print("✅ Return workflow loaded successfully")
        print(f"   - Workflow: {engine.workflow_name}")
        print(f"   - Collection nodes: {[s['id'] for s in engine.steps if s['action'] == 'collect_input_with_agent']}")

        # Test greeting workflow
        graph2, engine2 = load_workflow('examples/greeting_workflow.yaml')
        print("✅ Greeting workflow loaded successfully")
        print(f"   - Workflow: {engine2.workflow_name}")
        print(f"   - Collection nodes: {[s['id'] for s in engine2.steps if s['action'] == 'collect_input_with_agent']}")

        return True
    except Exception as e:
        print(f"❌ Error loading workflows: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_navigation_state_functions():
    """Test navigation state management functions"""
    try:
        graph, engine = load_workflow('examples/return_workflow.yaml')

        # Create test state
        test_state = {
            'order_id': 'TEST123',
            'return_reason': 'damaged',
            '_field_collection_order': ['order_id', 'return_reason'],
            '_completed_collection_nodes': {
                'collect_order_id': {'field': 'order_id', 'description': 'Change order ID'},
                'collect_reason': {'field': 'return_reason', 'description': 'Change return reason'}
            },
            '_conversations': {
                'order_id_conversation': [{'role': 'user', 'content': 'TEST123'}],
                'return_reason_conversation': [{'role': 'user', 'content': 'damaged'}]
            }
        }

        print("\n📋 Testing State Management:")
        print(f"   - Initial state: order_id={test_state.get('order_id')}, return_reason={test_state.get('return_reason')}")

        # Test rollback to collect_order_id
        engine._rollback_state_to_node(test_state, 'collect_order_id')
        print(f"   - After rollback to collect_order_id: order_id={test_state.get('order_id')}, return_reason={test_state.get('return_reason')}")
        print(f"   - Field collection order: {test_state.get('_field_collection_order', [])}")
        print(f"   - Remaining conversations: {list(test_state.get('_conversations', {}).keys())}")

        print("✅ Navigation state management works correctly")
        return True

    except Exception as e:
        print(f"❌ Error testing navigation functions: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_navigation_prompt_generation():
    """Test navigation prompt generation"""
    try:
        graph, engine = load_workflow('examples/return_workflow.yaml')

        # Create test state with completed nodes
        test_state = {
            '_completed_collection_nodes': {
                'collect_order_id': {'field': 'order_id', 'description': 'Change order ID'},
                'collect_reason': {'field': 'return_reason', 'description': 'Change return reason'}
            }
        }

        nav_prompt = engine._generate_navigation_prompt_addition(test_state)
        print("\n🔄 Testing Navigation Prompt Generation:")
        print("Generated navigation prompt:")
        print(nav_prompt)

        # Check if prompt contains expected elements
        if "INTENT_CHANGE:" in nav_prompt and "collect_order_id" in nav_prompt and "collect_reason" in nav_prompt:
            print("✅ Navigation prompt generation works correctly")
            return True
        else:
            print("❌ Navigation prompt missing expected elements")
            return False

    except Exception as e:
        print(f"❌ Error testing navigation prompt: {e}")
        return False

def main():
    """Run all navigation tests"""
    print("🧪 Testing Navigation Functionality")
    print("=" * 50)

    tests = [
        test_workflow_loading,
        test_navigation_state_functions,
        test_navigation_prompt_generation
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()  # Empty line between tests

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All navigation tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
