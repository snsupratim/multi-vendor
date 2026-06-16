import tiktoken


encoding = tiktoken.get_encoding(
    "cl100k_base"
)


class TokenService:

    @staticmethod
    def count_tokens(
        text: str
    ):

        return len(
            encoding.encode(text)
        )