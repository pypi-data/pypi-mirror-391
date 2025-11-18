from docling.document_converter import DocumentConverter
import json

def describe_object(obj, name="result", depth=0, max_depth=2):
    """Recursively print attributes and types for inspection."""
    indent = "  " * depth
    if depth > max_depth:
        return
    print(f"{indent}- {name}: {type(obj).__name__}")

    if hasattr(obj, "__dict__"):
        for k, v in obj.__dict__.items():
            print(f"{indent}   • {k} -> {type(v).__name__}")
            if isinstance(v, (list, tuple)):
                print(f"{indent}     [len={len(v)}]")
                if v and depth + 1 <= max_depth:
                    describe_object(v[0], f"{k}[0]", depth + 1, max_depth)
            elif hasattr(v, "__dict__") and depth + 1 <= max_depth:
                describe_object(v, k, depth + 1, max_depth)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            print(f"{indent}   • {k} -> {type(v).__name__}")

def inspect_docling_json(pdf_path):
    converter = DocumentConverter()
    result = converter.convert(pdf_path)

    print("\n=== TOP-LEVEL KEYS ===")
    print(result.model_dump().keys())

    json_path = pdf_path.replace(".pdf", "_docling.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(result.model_dump_json(indent=2))

    print(f"✅ Saved structured JSON to: {json_path}")


def main():
    pdf_path = "data/pdf_samples/deeplearning_lightsheet.pdf"  # replace with your file
    inspect_docling_json(pdf_path)
    # converter = DocumentConverter()
    # result = converter.convert(pdf_path)

    # print("\n=== TYPE INFO ===")
    # print(f"type(result) = {type(result)}")
    # print(f"dir(result): {[a for a in dir(result) if not a.startswith('_')]}\n")

    # print("=== ATTRIBUTE TREE ===")
    # describe_object(result, "result")

    # # If possible, show high-level JSON summary
    # if hasattr(result, "to_json"):
    #     try:
    #         print("\n=== JSON STRUCTURE PREVIEW ===")
    #         preview = result.to_json()
    #         print(json.dumps(preview, indent=2)[:1500], "...\n")
    #     except Exception as e:
    #         print(f"[warn] result.to_json() failed: {e}")

if __name__ == "__main__":
    main()