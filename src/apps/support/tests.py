import tldextract


# This will print the availabe models for each LLM
# print(GrokRAG.get_models())
# print(MistralRAG.get_models())
# print(ClaudeRAG.get_models())
# print(OpenAIRAG.get_models())
# print(GeminiRAG.get_models())
# print(CohereRAG.get_models())

def extract_domain_name(link):
    return tldextract.extract(link).domain


def main():
    response = rag.get_response(query, USER_ID)

    while True:
        query = input("User: ").strip()
        if not query:
            continue
        if query.lower() == 'quit':
            break

        try:
            print("Assistant:", response)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
