from pypdf import PdfReader


class PDFService:

    @staticmethod
    def extract_text(
        file_path: str
    ):

        reader = PdfReader(
            file_path
        )

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text