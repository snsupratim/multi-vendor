class CostService:

    @staticmethod
    def estimate_cost(
        input_tokens: int,
        output_tokens: int
    ) -> float:

        #
        # Placeholder values.
        # Replace with actual Gemini pricing later.
        #

        input_cost = (
            input_tokens / 1_000_000
        ) * 0.10

        output_cost = (
            output_tokens / 1_000_000
        ) * 0.40

        return round(
            input_cost + output_cost,
            8
        )