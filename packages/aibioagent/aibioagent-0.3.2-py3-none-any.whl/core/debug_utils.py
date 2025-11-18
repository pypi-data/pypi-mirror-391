from langchain_core.runnables import RunnableLambda

def debug_stage(label: str):
    """Return a RunnableLambda that prints input and output for debugging."""
    def _debug_fn(x):
        print(f"\n🪶 [DEBUG] Entering stage: {label}")
        print(f"Input type: {type(x).__name__}")
        if isinstance(x, dict):
            for k, v in x.items():
                print(f"  {k}: {str(v)[:300]}{'...' if len(str(v)) > 300 else ''}")
        else:
            print(f"  Value: {str(x)[:500]}{'...' if len(str(x)) > 500 else ''}")
        return x  # pass through unchanged

    return RunnableLambda(_debug_fn)

