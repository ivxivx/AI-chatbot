from fastapi import APIRouter
from starlette.requests import Request

from api.qarequest import QARequest
from api.qaresponse import QAResponse
import model.transform as tf 

prediction_router = APIRouter()

raw_text = tf.extract_doc("../sample.txt")

text_chunks = tf.chunk_texts(raw_text)

vectorstore = tf.get_vectorstore(text_chunks)

chain = tf.get_chain(vectorstore)


@prediction_router.post("/questions", response_model=QAResponse, name="questions")
def post_question(
    request: Request,
    body: QARequest = None,
) -> QAResponse:
    """
    #### Retrieves an answer from context given a question

    """
    
    answer = chain.run({"question": body.question})

    return QAResponse(answer=answer)


api_router = APIRouter()
api_router.include_router(prediction_router, tags=["prediction"], prefix="/v1")

