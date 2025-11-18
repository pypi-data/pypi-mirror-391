from conversational_sop import WorkflowTool

tool = WorkflowTool(
    yaml_path="./greeting_workflow.yaml",
    name="test",
    description="test",
    checkpointer=None
)

if __name__ == "__main__" :
    while True :
        query = input("Enter: ")

        result = tool.execute(
            thread_id="test_thread_1",
            user_message=query,
            initial_context=None
        )

        print(result)