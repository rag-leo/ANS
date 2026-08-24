from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)


class ChunkingService:

    def __init__(self):

        self.text_splitter = (
            RecursiveCharacterTextSplitter(
                chunk_size=1500,
                chunk_overlap=250,
                length_function=len,
                separators=[
                    "\n\n",
                    "\n",
                    "।",
                    ".",
                    " ",
                    "",
                ],
            )
        )

    def chunk_text(
        self,
        text: str,
    ) -> list[str]:
        return self.text_splitter.split_text(
            text
        )
