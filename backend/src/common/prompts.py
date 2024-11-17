from langchain_core.prompts import ChatPromptTemplate

message_intent_detection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a helpful AI assistant tasked with detecting the intent of a user's message. Your goal is to understand and categorize the message into one of the following intents: greeting, house_buying_knowledge_question, finding_property_finland, unsupported_intent. Here are the definitions of each intent:
                
                1. greeting: A simple salutation or farewell, such as "Hello," "Hi," "Good morning," "Goodbye," or "See you later."
                2. house_buying_knowledge_question: Any questions related to buying property in Finland, including but not limited to:
                    - Financial aspects (prices, mortgages, loans, down payments, costs)
                    - Legal requirements and processes
                    - Taxes and fees
                    - Property rights and ownership
                    - Required documentation
                    - Real estate market conditions
                    - Property inspection and assessment
                    - Insurance requirements
                    - Renovation and maintenance responsibilities
                3. finding_property_finland: The user wants to find a property (apartment, house, land, any real estate) in Finland. The message might contain a city, price range, number of rooms, etc but the main idea is that the user is looking for a property.
                4. unsupported_intent: Any question that does not fall under the above intent categories.
         """,
        ),
        (
            "human",
            """
            <chat_history>
            {chat_history}
            </chat_history>

            <question>
            {question}
            </question>
            
            Carefully read and analyze the message to determine its intent based on the definitions provided above.

            Guidelines for categorization:
            - If the message is a simple greeting or farewell, classify it as "greeting"
            - If the message is a question related to buying property in Finland, classify it as "house_buying_knowledge_question"
            - If the message is about finding a property to buy in Finland, classify it as "finding_property_finland"
            - For questions that do not fall under the above categories or cannot be answered based on the chat history, classify it as "unsupported_intent"

            After analyzing the question, provide your reasoning for the intent classification.
            """,
        ),
    ]
)

knowledge_rag_answer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a helpful AI assistant tasked to answer a question based on a set of documents. Your goal is to provide a concise and informative answer for the user's question using the information from the documents.
            """,
        ),
        (
            "human",
            """
            Here are two inputs:
            <source>
            {source}
            </source>

            <question>
            {question}
            </question>
            
            Here is the guideline for answering the question:
            
            1. Carefully read and analyze all the given documents
            2. Identify information from the resource that is relevant to the question
            3. Extract the information in the document to formulate a comprehensive answer to the question. Do not include any external knowledge or information not present in the sources.
            4. As you write your answer, include citations for each piece of information you use from the sources. Use superscript numbers for citations, and link it with the sourceURL if exists. The superscript number should be the same as the one in the "References" section.
            5. Your answer should be in a friendly and engaging tone.
            6. Format your answer in markdown format, following this structure:
                - Main content with superscript citations
                - A "References" section that lists the document ids used to answer the question with links to the documents if possible.
            7. Use the following format for citations and references:
                - In-text citation: Use superscript like "¹" to refer to a reference
                - Reference entry: Quote shortly the sentence you used to give the answer with the link to the sourceURL if exists.
            8. Ensure that all citations in the text have a corresponding reference entry, and vice versa.
            9. If the answer is not present in the source, don't answer the question. And don't provide any sources of references. Just apologize that you don't have the answer in your knowledge base.
            
            Always return the answer in a structured output within the "answer" key!
            Remember to use only the information provided in the sources to answer the question. Do not include any external knowledge or personal opinions. Ensure that your answer is comprehensive, well-structured, and properly cited. Always answer in the same language as the question.
            """,
        ),
    ]
)
