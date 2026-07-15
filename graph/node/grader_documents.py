from typing import Dict, Any

from graph.chains.retreiver_chain import retriever_chain, GradeDocuments
from graph.state import GraphState


def grader_documents(state: GraphState) -> Dict[str, Any]:
    print("--- GRADER DOCUMENTS ---")

    question = state["question"]
    documents = state["documents"]
    web_search = False
    filter_documents = []

    for document in documents:
        score: GradeDocuments = retriever_chain.invoke(
            {"question": question, "document": documents}
        )
        grade = score.binary_score
        if grade.lower() == "yes":
            filter_documents.append(document)
        else:
            web_search = True
            continue

    return {
        "question": question,
        "documents": filter_documents,
        "web_search": web_search,
    }


if __name__ == "__main__":
    res = grader_documents(state={"question": "what is agent?", "documents": []})
    print(res)
