class TextUtils:
    @staticmethod
    def strip_join(text_list: list[str], join_element: str = " ") -> str:
        return join_element.join(text.strip() for text in text_list if text is not None)
